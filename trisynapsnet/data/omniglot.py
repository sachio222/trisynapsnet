# Adapted from github.com/sachio222/aha4 (MIT), utils/data.py at 446d6db.
# New here: load_background_runs, validation runs built from the background
# alphabets, load_instance_runs for AHA's instance task, and
# load_characters, one drawing of every character, for E1c.
"""Omniglot: Lake's 20 one-shot runs and validation runs like them.

Omniglot (Lake, Salakhutdinov and Tenenbaum 2015) has 1623 handwritten
characters from 50 alphabets, each drawn once by 20 different people. The
30 "background" alphabets are for learning general features. The 20
"evaluation" alphabets hold the 20 official one-shot runs.

This project does not keep its own copy of the data. By default it reads
the folder that aha4 downloads into, ../aha4/data, which holds:

    omniglot-py/images_background/   the 30 background alphabets
    omniglot-runs/run01 ... run20/   the official one-shot runs

aha4 never downloads the evaluation alphabets as whole folders, and this
project never writes into aha4, so they go to ./data instead (see
download_alphabets).

Set TSN_AHA4 to aha4's folder when it does not sit next to this repo, as
in a git worktree. Result files still record the standard layout,
../aha4/..., through portable().
"""

import hashlib
import os
import random
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

REPO = Path(__file__).resolve().parents[2]
# aha4's folder: next to this repo, unless TSN_AHA4 says otherwise.
AHA4 = Path(os.environ.get("TSN_AHA4", REPO.parent / "aha4")).resolve()
DEFAULT_DATA = AHA4 / "data"
DEFAULT_CHECKPOINT = AHA4 / "checkpoints" / "vc_pretrained.pth.tar"
# Where this project keeps data that aha4 does not have.
LOCAL_DATA = REPO / "data"


def portable(path):
    """A path as result files record it: relative to the repo, with aha4
    written as ../aha4 wherever it lives on this machine.

    A relative path is taken as already relative to the repo.
    """
    path = Path(path)
    if not path.is_absolute():
        return path.as_posix()
    path = path.resolve()
    if path.is_relative_to(REPO):
        return path.relative_to(REPO).as_posix() or "."
    if path.is_relative_to(AHA4):
        return (Path("..") / "aha4" / path.relative_to(AHA4)).as_posix()
    return os.path.relpath(path, REPO)

RUNS_URL = ("https://raw.githubusercontent.com/brendenlake/omniglot/master/"
            "python/one-shot-classification/all_runs.zip")
RUNS_SHA256 = "437c1eeab0af8484112e1b4cc0f3d541ec727f7c47b9b202da738af9dfd6c325"
N_RUNS = 20
RUN_SIZE = 20       # characters per run
N_DRAWERS = 20      # people who drew every character

ALPHABETS_URL = ("https://raw.githubusercontent.com/brendenlake/omniglot/master/"
                 "python/images_{}.zip")
# The evaluation zip's MD5 matches torchvision's (6b91aef0f799c5bb55b94e3f2daec811).
ALPHABETS_SHA256 = {
    "evaluation": "1f61a8f3366785b057fc117d9228e78a16e3d976c8953b2a10fcc74cf0609cee",
}


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


def _safe_extract(archive, folder):
    """Unpacks archive into folder, safely when several jobs do it at once.

    The archive goes into a temporary folder beside its destination first,
    and each top-level entry then moves into place with one rename. A
    rename either puts a whole entry in place or finds that another job
    already did, so no job trips over another's half-written files and no
    job sees a partial folder.
    """
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            # Refuse anything that would unpack outside the folder.
            if name.startswith("/") or ".." in Path(name).parts:
                raise RuntimeError("Unsafe path in archive: {}".format(name))
        scratch = Path(tempfile.mkdtemp(prefix=".unpacking-", dir=folder))
        try:
            z.extractall(scratch)
            for entry in sorted(scratch.iterdir()):
                target = folder / entry.name
                try:
                    os.rename(entry, target)
                except OSError:
                    # Another job put this entry in place first.
                    if not target.exists():
                        raise
        finally:
            shutil.rmtree(scratch, ignore_errors=True)


def _download(url, archive):
    """Downloads url to archive through a temporary file, so a job never
    sees another job's half-downloaded archive."""
    archive = Path(archive)
    fd, part = tempfile.mkstemp(prefix=".downloading-", dir=archive.parent)
    os.close(fd)
    try:
        print("Downloading {}".format(url))
        urllib.request.urlretrieve(url, part)
        os.replace(part, archive)
    finally:
        if os.path.exists(part):
            os.remove(part)


def download_runs(root=DEFAULT_DATA):
    """Downloads and unpacks the 20 official runs once. Returns the folder."""
    folder = Path(root) / "omniglot-runs"
    if (folder / "run20" / "class_labels.txt").is_file():
        return folder

    folder.mkdir(parents=True, exist_ok=True)
    archive = folder / "all_runs.zip"
    if not archive.is_file():
        _download(RUNS_URL, archive)

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != RUNS_SHA256:
        raise RuntimeError("all_runs.zip checksum mismatch: {}".format(digest))

    _safe_extract(archive, folder)
    return folder


def download_alphabets(split, root=LOCAL_DATA):
    """The folder of one Omniglot split, downloading it once if needed.

    Returns root/omniglot-py/images_<split>. Only the evaluation split can
    be downloaded here. The background split comes from aha4's folder.
    """
    folder = Path(root) / "omniglot-py" / "images_{}".format(split)
    if folder.is_dir():
        return folder
    if split not in ALPHABETS_SHA256:
        raise FileNotFoundError("No {} alphabets at {}".format(split, folder))

    folder.parent.mkdir(parents=True, exist_ok=True)
    archive = folder.parent / "images_{}.zip".format(split)
    if not archive.is_file():
        _download(ALPHABETS_URL.format(split), archive)

    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != ALPHABETS_SHA256[split]:
        raise RuntimeError("{} checksum mismatch: {}".format(archive.name, digest))
    _safe_extract(archive, folder.parent)
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


def load_instance_runs(root=LOCAL_DATA, image_size=52, centre=True, seed=0,
                       split="evaluation", n_runs=N_RUNS):
    """Builds runs for AHA's one-shot instance-classification task.

    AHA's paper, Section 3.2: "the train character exemplar must be matched
    with the exact same exemplar amongst a set of 20 distractor exemplars of
    the same character class. [...] In each run, the character class and
    exemplars are selected by randomly sampling without repeats from the
    'evaluation' set."

    Each run here:
      * one character, drawn without repeats across runs from every
        character in the split,
      * all 20 of its drawings, one per drawer, as the study set in a
        shuffled drawer order,
      * the same 20 drawings again as the test set, in another shuffled
        order, with labels pointing at the study item each one is,
      * the same preprocessing as Lake's runs.

    split="background" builds the same runs from the 30 background
    alphabets, for trying settings without touching the evaluation set.
    The draw comes from `seed` alone.

    Returns runs shaped like load_runs(), each with an "info" dict naming
    the split, alphabet, character and study drawer order.
    """
    folder = download_alphabets(split, root)
    load = _loader(image_size, centre)
    rng = random.Random(seed)

    characters = sorted((a.name, c.name) for a in folder.iterdir() if a.is_dir()
                        for c in a.iterdir() if c.is_dir())
    if len(characters) < n_runs:
        raise ValueError("Only {} characters in {}".format(len(characters), folder))

    runs = []
    for alphabet, character in rng.sample(characters, n_runs):
        files = {int(p.stem.split("_")[1]): p
                 for p in (folder / alphabet / character).glob("*_*.png")}
        if sorted(files) != list(range(1, N_DRAWERS + 1)):
            raise FileNotFoundError("Expected drawers 1 to {} in {}/{}".format(
                N_DRAWERS, alphabet, character))
        drawers = rng.sample(range(1, N_DRAWERS + 1), N_DRAWERS)
        order = list(range(N_DRAWERS))
        rng.shuffle(order)

        study = torch.stack([load(files[d]) for d in drawers])
        labels = torch.tensor(order)
        runs.append({
            "study": study,
            "recall": study[labels].clone(),
            "labels": labels,
            "info": {"split": split, "alphabet": alphabet, "character": character,
                     "drawers": drawers},
        })
    return runs


def load_characters(root=None, split="evaluation", image_size=52, centre=True, seed=0):
    """One drawing of every character in a split, for E1c's load tests.

    E1c stores many memories at once, one drawing each of different
    characters. Each character's drawer is drawn at random from its 20,
    from `seed` alone, so the same seed always gives the same drawings.
    Characters come in sorted (alphabet, character) order.

    root defaults to aha4's folder for the background split and to this
    project's ./data for the evaluation split, which download_alphabets
    fetches on first use.

    Returns (images, info): images is (characters, 1, H, W), and info is a
    list of {"alphabet", "character", "drawer"} in the same order.
    """
    if root is None:
        root = DEFAULT_DATA if split == "background" else LOCAL_DATA
    folder = download_alphabets(split, root)
    load = _loader(image_size, centre)
    rng = random.Random(seed)

    characters = sorted((a.name, c.name) for a in folder.iterdir() if a.is_dir()
                        for c in a.iterdir() if c.is_dir())
    images, info = [], []
    for alphabet, character in characters:
        drawer = rng.randint(1, N_DRAWERS)
        matches = sorted((folder / alphabet / character).glob("*_{:02d}.png".format(drawer)))
        if len(matches) != 1:
            raise FileNotFoundError("Expected one drawing by drawer {} in {}/{}".format(
                drawer, alphabet, character))
        images.append(load(matches[0]))
        info.append({"alphabet": alphabet, "character": character, "drawer": drawer})
    return torch.stack(images), info
