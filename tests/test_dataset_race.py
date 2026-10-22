"""Two jobs unpacking the evaluation alphabets at once.

E8b's main run crashed when two runs started together on a machine with
no evaluation alphabets yet: both saw the folder missing, both unpacked
the archive into it, and one hit FileExistsError inside zipfile. Several
jobs starting on an empty data folder must each get a complete folder.
"""

import hashlib
import os
import subprocess
import sys
import time
import zipfile
from pathlib import Path

from trisynapsnet.data import omniglot

JOBS = 6

CHILD = r"""
import sys, time
from pathlib import Path
from trisynapsnet.data import omniglot
root, digest, go = sys.argv[1], sys.argv[2], Path(sys.argv[3])
omniglot.ALPHABETS_SHA256["evaluation"] = digest
while not go.exists():
    time.sleep(0.001)
folder = omniglot.download_alphabets("evaluation", root)
n = sum(1 for p in folder.rglob("*.png"))
print(n)
"""


def make_archive(path, alphabets=12, characters=12, drawers=4):
    """A zip shaped like images_evaluation.zip: folder entries and
    images_evaluation/<alphabet>/<character>/<id>_<drawer>.png files."""
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("images_evaluation/", "")
        for a in range(alphabets):
            z.writestr("images_evaluation/alphabet{:02d}/".format(a), "")
            for c in range(characters):
                d = "images_evaluation/alphabet{:02d}/character{:02d}/".format(a, c)
                z.writestr(d, "")
                for k in range(1, drawers + 1):
                    z.writestr(d + "{:04d}_{:02d}.png".format(c, k), b"x" * 64)
    return alphabets * characters * drawers


def test_concurrent_extraction_into_an_empty_root_gives_every_job_the_whole_folder(tmp_path):
    root = tmp_path / "data"
    (root / "omniglot-py").mkdir(parents=True)
    archive = root / "omniglot-py" / "images_evaluation.zip"
    n_files = make_archive(archive)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    go = tmp_path / "go"
    env = dict(os.environ, PYTHONPATH=str(omniglot.REPO))
    jobs = [subprocess.Popen([sys.executable, "-c", CHILD, str(root), digest, str(go)],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
            for _ in range(JOBS)]
    time.sleep(5)  # every job has imported torch and is waiting
    go.touch()
    results = [j.communicate(timeout=120) for j in jobs]
    errors = [err for j, (out, err) in zip(jobs, results) if j.returncode != 0]
    assert not errors, errors[0]
    assert [int(out) for out, _ in results] == [n_files] * JOBS
    # Nothing left behind but the archive and the folder.
    assert sorted(p.name for p in (root / "omniglot-py").iterdir()) == \
        ["images_evaluation", "images_evaluation.zip"]


def test_a_half_downloaded_archive_is_never_where_another_job_looks(tmp_path, monkeypatch):
    root = tmp_path / "data"
    archive = root / "omniglot-py" / "images_evaluation.zip"
    source = tmp_path / "source.zip"
    make_archive(source, alphabets=2, characters=2, drawers=2)
    seen = []

    def fake_urlretrieve(url, filename):
        # Halfway through the download, another job looks for the archive.
        Path(filename).write_bytes(source.read_bytes()[:10])
        seen.append(archive.is_file())
        Path(filename).write_bytes(source.read_bytes())

    monkeypatch.setattr(omniglot.urllib.request, "urlretrieve", fake_urlretrieve)
    monkeypatch.setitem(omniglot.ALPHABETS_SHA256, "evaluation",
                        hashlib.sha256(source.read_bytes()).hexdigest())
    folder = omniglot.download_alphabets("evaluation", root)
    assert seen == [False]
    assert len(list(folder.rglob("*.png"))) == 8
