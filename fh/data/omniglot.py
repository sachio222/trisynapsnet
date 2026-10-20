# Adapted from github.com/sachio222/aha4 (MIT), utils/data.py at 446d6db.
# New here: load_background_runs, validation runs built from the background
# alphabets.
"""Omniglot: Lake's 20 one-shot runs and validation runs like them.

Omniglot (Lake, Salakhutdinov and Tenenbaum 2015) has 1623 handwritten
characters from 50 alphabets, each drawn once by 20 different people. The
30 "background" alphabets are for learning general features. The 20
"evaluation" alphabets hold the 20 official one-shot runs.

This project does not keep its own copy of the data. By default it reads
the folder that aha4 downloads into, ../aha4/data, which holds:

    omniglot-py/images_background/   the 30 background alphabets
    omniglot-runs/run01 ... run20/   the official one-shot runs
"""

import hashlib
import random
import urllib.request
import zipfile
from pathlib import Path

import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

REPO = Path(__file__).resolve().parents[2]
DEFAULT_DATA = REPO.parent / "aha4" / "data"
DEFAULT_CHECKPOINT = REPO.parent / "aha4" / "checkpoints" / "vc_pretrained.pth.tar"

RUNS_URL = ("https://raw.githubusercontent.com/brendenlake/omniglot/master/"
            "python/one-shot-classification/all_runs.zip")
RUNS_SHA256 = "437c1eeab0af8484112e1b4cc0f3d541ec727f7c47b9b202da738af9dfd6c325"
N_RUNS = 20
RUN_SIZE = 20       # characters per run
N_DRAWERS = 20      # people who drew every character


def invert(x):
    """Omniglot is black ink on white. Flip it so ink is 1 and paper is 0."""
    return 1.0 - x


def centre_of_mass(x):
    """Shifts a (1, H, W) drawing so its centre of ink sits mid-frame.

    The AHA paper doesn't mention this step, but the authors' PyTorch code
    (github.com/Cerenaut/pt-aha) centres every drawing this way. Shifts are
    sub-pixel, with bilinear interpolation and blank fill.
    """
    _, h, w = x.shape
    mass = x.sum()
    if mass <= 0:
        return x
    ys = torch.arange(h, dtype=x.dtype)
    xs = torch.arange(w, dtype=x.dtype)
    cy = (x[0].sum(dim=1) * ys).sum() / mass
    cx = (x[0].sum(dim=0) * xs).sum() / mass
    dy, dx = (h - 1) / 2 - cy, (w - 1) / 2 - cx

    # affine_grid works in [-1, 1] coordinates, where one pixel is 2/size.
    theta = torch.tensor([[1.0, 0.0, -2 * dx / w], [0.0, 1.0, -2 * dy / h]], dtype=x.dtype)
    grid = F.affine_grid(theta[None], [1, 1, h, w], align_corners=False)
    return F.grid_sample(x[None], grid, mode="bilinear", padding_mode="zeros",
                         align_corners=False)[0]


def omniglot_transform(image_size=52, centre=True):
    """105x105 drawings -> image_size x image_size tensors, ink = 1."""
    steps = [
        transforms.Resize(image_size, antialias=True),
        transforms.ToTensor(),
        transforms.Lambda(invert),
    ]
    if centre:
        steps.append(transforms.Lambda(centre_of_mass))
    return transforms.Compose(steps)


def parse_class_labels(lines):
    """Reads a run's class_labels.txt into 0-based study indices.

    Each line looks like "run01/test/item01.png run01/training/class08.png",
    meaning test item 1 shows the character of study drawing 8.
    """
    pairs = []
    for line in lines:
        if not line.strip():
            continue
        test, train = line.split()
        item = int(Path(test).stem.replace("item", ""))
        cls = int(Path(train).stem.replace("class", ""))
        pairs.append((item, cls - 1))
    return [cls for _, cls in sorted(pairs)]


def download_runs(root=DEFAULT_DATA):
    """Downloads and unpacks the 20 official runs once. Returns the folder."""
    folder = Path(root) / "omniglot-runs"
    if (folder / "run20" / "class_labels.txt").is_file():
        return folder

    folder.mkdir(parents=True, exist_ok=True)
    archive = folder / "all_runs.zip"
    if not archive.is_file():
        print("Downloading {}".format(RUNS_URL))
        urllib.request.urlretrieve(RUNS_URL, archive)

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != RUNS_SHA256:
        raise RuntimeError("all_runs.zip checksum mismatch: {}".format(digest))

    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            # Refuse anything that would unpack outside the folder.
            if name.startswith("/") or ".." in Path(name).parts:
                raise RuntimeError("Unsafe path in archive: {}".format(name))
        z.extractall(folder)
    return folder


def _loader(image_size, centre):
    tsfm = omniglot_transform(image_size, centre)

    def load(path):
        return tsfm(Image.open(path).convert("L"))
    return load


def load_runs(root=DEFAULT_DATA, image_size=52, centre=True):
    """Loads the 20 official runs as tensors.

    Each run is a dict with:
        study:  (20, 1, H, W) study drawings, class01 ... class20
        recall: (20, 1, H, W) test drawings, item01 ... item20
        labels: (20,) index of the study drawing each test drawing matches
    """
    folder = download_runs(root)
    load = _loader(image_size, centre)

    runs = []
    for r in range(1, N_RUNS + 1):
        run_dir = folder / "run{:02d}".format(r)
        study = torch.stack([load(run_dir / "training" / "class{:02d}.png".format(i))
                             for i in range(1, RUN_SIZE + 1)])
        recall = torch.stack([load(run_dir / "test" / "item{:02d}.png".format(i))
                              for i in range(1, RUN_SIZE + 1)])
        labels = parse_class_labels((run_dir / "class_labels.txt").read_text().splitlines())
        runs.append({"study": study, "recall": recall, "labels": torch.tensor(labels)})
    return runs


def load_background_runs(root=DEFAULT_DATA, image_size=52, centre=True, seed=0,
                         n_runs=N_RUNS):
    """Builds one-shot runs from the 30 background alphabets, for validation.

    Lake's 20 runs have no separate validation set, so choosing settings on
    them inflates their scores. These runs copy Lake's structure from the
    background alphabets instead:
      * each run uses its own alphabet, one with at least 20 characters,
      * 20 different characters from that alphabet,
      * one person's drawings for all 20 study items, and a different
        person's drawings for all 20 test items,
      * test items in shuffled order, with labels pointing at the study item
        each one shows,
      * the same preprocessing as the official runs (resize to 52, invert,
        centre).

    The draw comes from `seed` alone, separate from the model's seed, so the
    same seed always gives the same runs.

    The vision network was pretrained on these alphabets, without labels.
    Scores here may read a little high in absolute terms. They are for
    comparing settings with each other.

    Returns runs shaped like load_runs(), each with an extra "info" dict
    naming the alphabet, characters and drawers.
    """
    folder = Path(root) / "omniglot-py" / "images_background"
    if not folder.is_dir():
        raise FileNotFoundError("No background alphabets at {}".format(folder))
    load = _loader(image_size, centre)
    rng = random.Random(seed)

    alphabets = sorted(p.name for p in folder.iterdir()
                       if p.is_dir() and sum(c.is_dir() for c in p.iterdir()) >= RUN_SIZE)
    if len(alphabets) < n_runs:
        raise ValueError("Only {} alphabets have {} characters".format(len(alphabets), RUN_SIZE))

    def drawing(alphabet, character, drawer):
        # Files are named <image id>_<drawer>.png, drawers 01 to 20.
        matches = sorted((folder / alphabet / character).glob("*_{:02d}.png".format(drawer)))
        if len(matches) != 1:
            raise FileNotFoundError("Expected one drawing by drawer {} in {}/{}".format(
                drawer, alphabet, character))
        return matches[0]

    runs = []
    for alphabet in rng.sample(alphabets, n_runs):
        characters = sorted(p.name for p in (folder / alphabet).iterdir() if p.is_dir())
        chosen = rng.sample(characters, RUN_SIZE)
        study_drawer, test_drawer = rng.sample(range(1, N_DRAWERS + 1), 2)
        order = list(range(RUN_SIZE))
        rng.shuffle(order)

        study = torch.stack([load(drawing(alphabet, c, study_drawer)) for c in chosen])
        recall = torch.stack([load(drawing(alphabet, chosen[i], test_drawer)) for i in order])
        runs.append({
            "study": study,
            "recall": recall,
            "labels": torch.tensor(order),
            "info": {"alphabet": alphabet, "characters": chosen,
                     "study_drawer": study_drawer, "test_drawer": test_drawer},
        })
    return runs
