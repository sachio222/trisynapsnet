"""E1d: CA3's capacity when DG and CA3 codes are sparser.

E1c ran CA3 with 4.4% of its cells active, AHA's share, at every size, and
found that the number of memories CA3 holds per cell falls as the network
grows. Classic theory expects that at a fixed share of active cells. It
expects capacity per cell to hold or grow only when the number of active
cells grows slowly, about with the logarithm of the cell count. E1d
repeats E1c's CA3 test with the share of active cells in DG and CA3 as a
parameter:

    4.4   AHA's share, 10 of 225 cells
    2     the share of granule cells active in rat dentate gyrus
    1     1% of cells
    log   k = round(c log2 n) active cells, with c set so that k = 20,
          2%, at 1,000 cells

Any share that gives fewer than 3 active cells is raised to 3.

Patterns, damage, cues, settling and scores are E1c's, from
trisynapsnet/eval/ca3space.py, with the same seeds. Sparser codes hold
far more memories, up to about a million at 16,000 cells, so this harness
changes how patterns are kept, never what is computed:

    * each pattern is a list of its k active cells, and E1c's random
      patterns are drawn a chunk at a time from the same random stream;
    * the local rules store a running count of how often each pair of
      cells fired together, which gives both rules' weights exactly and
      lets each load add only its new patterns;
    * the ideal lookup compares states with the stored patterns a chunk at
      a time.

For random patterns, the first seed runs loads up a fixed grid until exact
recall falls below 5%, and the other seeds run the same loads. Every
choice is listed in docs/e1d_protocol.md.

Example:
    python -m trisynapsnet.eval.sparsecodes --source random --units 1000 \\
        --sparsity 2 --rule willshaw --seeds 10
"""

import argparse
import json
import math
import platform
import time
from pathlib import Path

import torch

from trisynapsnet.data import omniglot
from trisynapsnet.eval import ca3space

REPO = Path(__file__).resolve().parents[2]

RULES = ca3space.RULES
SPARSITIES = ("4.4", "2", "1", "log")
SHARES = {"4.4": 10 / 225, "2": 0.02, "1": 0.01}
# Log-scaled codes: k = c log2(n), with k = 20 (2%) at 1,000 cells.
LOG_C = 20 / math.log2(1000)
MIN_K = 3
SIZES = (225, 1000, 4000, 16000)
# Loads: 1, 1.5, 2, 3, 5 and 7 per power of ten, from 20 to a million.
GRID = tuple(int(m * 10 ** e) for e in range(1, 7) for m in (1, 1.5, 2, 3, 5, 7)
             if 20 <= m * 10 ** e <= 1_000_000) + (1_000_000,)
# Random patterns stop climbing the grid after the first load at or past
# MIN_STOP_LOAD where exact recall falls below STOP_BELOW: from clean cues
# for the local rules, and from cues missing 40% of their cells for the
# pseudo-inverse, whose clean cues stay exact up to the cell count.
STOP_BELOW, MIN_STOP_LOAD = 0.05, 100
# Rows of patterns made dense at once: about 16 million cells.
CHUNK_CELLS = 2 ** 24


def active_cells(n, sparsity):
    """(k, raised): active cells for n cells at a share, and whether the
    floor of MIN_K raised it. Shares round half up, as damage counts do."""
    if sparsity == "log":
        k = ca3space.count(LOG_C * math.log2(n), 1)
    else:
        k = ca3space.count(SHARES[sparsity], n)
    return max(k, MIN_K), k < MIN_K


def dense(idx, n):
    """0/1 patterns, (rows, n), from each row's active cells."""
    return torch.zeros(idx.shape[0], n).scatter_(1, idx, 1.0)


def rows_per_chunk(n):
    return max(1, CHUNK_CELLS // n)


class RandomPool:
    """E1c's random patterns, drawn a chunk at a time as loads grow.

    take(p) returns the active cells of the first p patterns, the same
    patterns ca3space.random_patterns(p, n, k, generator("random", n, k,
    seed)) makes: torch draws the same stream however it is split.
    """

    def __init__(self, n, k, seed, chunk_rows=None):
        self.n, self.k = n, k
        self.generator = ca3space.generator("random", n, k, seed)
        self.chunk_rows = chunk_rows or rows_per_chunk(n)
        self.chunks, self.size, self._joined = [], 0, None

    def take(self, p):
        while self.size < p:
            m = min(self.chunk_rows, p - self.size)
            keys = torch.rand(m, self.n, generator=self.generator)
            self.chunks.append(keys.argsort(dim=1)[:, :self.k])
            self.size += m
            self._joined = None
        if self._joined is None:
            self._joined = torch.cat(self.chunks) if self.chunks else torch.empty(0, self.k)
        return self._joined[:p]


class PairCounts:
    """How often each pair of cells fired together over the stored patterns.

    C[i, j] counts patterns with both cells on (C[i, i] counts each cell),
    s[i] counts patterns with cell i on, p counts patterns. Counts are
    whole numbers below 2^24, so float32 holds them exactly.
    """

    def __init__(self, n, chunk_rows=None):
        self.n = n
        self.C = torch.zeros(n, n)
        self.s = torch.zeros(n, dtype=torch.float64)
        self.p = 0
        self.chunk_rows = chunk_rows or rows_per_chunk(n)

    def add(self, idx):
        for chunk in idx.split(self.chunk_rows):
            X = dense(chunk, self.n)
            self.C.addmm_(X.T, X)
            self.s += X.sum(dim=0).double()
            self.p += chunk.shape[0]


def weights(counts, rule, k):
    """A local rule's CA3 weights from pair counts.

    willshaw    W = clip(C, 0, 1), as clip(sum of x x^T, 0, 1).
    covariance  W = (C - a s_i - a s_j + p a^2) / n with a = k / n, which is
                sum of (x - a)(x - a)^T / n written out, computed in float64.
    Both with no self-connections, as in trisynapsnet/model/modules.py.
    """
    n = counts.n
    if rule == "willshaw":
        W = (counts.C > 0).float()
    elif rule == "covariance":
        a = k / n
        W = torch.empty(n, n)
        s = counts.s
        step = rows_per_chunk(n)
        for r0 in range(0, n, step):
            r1 = min(n, r0 + step)
            block = counts.C[r0:r1].double() - a * (s[r0:r1, None] + s[None, :]) + counts.p * a * a
            W[r0:r1] = (block / n).float()
    else:
        raise ValueError("Pair counts serve the local rules only, not {}".format(rule))
    W.fill_diagonal_(0)
    return W


def nearest(on, idx, right_sim, chunk_rows=None):
    """The ideal lookup over stored patterns kept as active-cell lists.

    For each row of `on`: the lookup's credit, scored as in ca3space.lookup
    (1 over the number tied for nearest when the right pattern is among
    them), and whether some stored pattern has all its cells on.

    Args:
        on: (rows, n) bool states.
        idx: (p, k) active cells of the stored patterns.
        right_sim: (rows,) cells shared with the right pattern.
    """
    n = on.shape[1]
    chunk_rows = chunk_rows or rows_per_chunk(n)
    x = on.float()
    best = torch.full((on.shape[0],), -1.0)
    ties = torch.zeros(on.shape[0])
    full = torch.zeros(on.shape[0], dtype=torch.bool)
    k = idx.shape[1]
    for chunk in idx.split(chunk_rows):
        sims = x @ dense(chunk, n).T
        top = sims.max(dim=1).values
        count = (sims == top[:, None]).sum(dim=1).float()
        ties = torch.where(top > best, count, torch.where(top == best, ties + count, ties))
        best = torch.maximum(best, top)
        full |= (sims == k).any(dim=1)
    credit = (right_sim.float() == best).float() / ties
    return credit, full


def score(cue_on, final_on, right, idx, target, chunk_rows=None):
    """ca3space.score for patterns kept as active-cell lists.

    Args:
        cue_on, final_on: (cues, n) bool.
        right: (cues, n) the right stored pattern for each cue, 0/1.
        idx: (p, k) active cells of every stored pattern.
        target: (cues,) unused beyond its length, kept for symmetry.
    """
    right = right > 0
    k = float(idx.shape[1])
    cue_sim = (cue_on & right).sum(dim=1)
    final_sim = (final_on & right).sum(dim=1)
    both = torch.cat([cue_on, final_on])
    credit, full = nearest(both, idx, torch.cat([cue_sim, final_sim]), chunk_rows)
    m = cue_on.shape[0]
    return {
        "exact": (final_on == right).all(dim=1).float(),
        "overlap_cue": cue_sim.float() / k,
        "overlap_final": final_sim.float() / k,
        "stray_cue": (cue_on & ~right).sum(dim=1).float() / k,
        "stray_final": (final_on & ~right).sum(dim=1).float() / k,
        "ident_cue": credit[:m],
        "ident_final": credit[m:],
        "on_stored": (full[m:] & (final_on.sum(dim=1).float() == k)).float(),
        "active_final": final_on.sum(dim=1).float(),
    }


@torch.no_grad()
def run_load(rule, idx, n, k, seed_parts, counts=None, conditions=ca3space.CONDITIONS,
             max_cues=ca3space.MAX_CUES):
    """ca3space.run_load for patterns kept as active-cell lists.

    Args:
        rule: CA3 rule.
        idx: (p, k) active cells of the stored patterns.
        n, k: cells and active cells.
        seed_parts: as in ca3space.run_load; the rule stays out of it.
        counts: PairCounts of exactly these patterns, for the local rules.

    Returns one dict per condition, as ca3space.run_load does.
    """
    p = idx.shape[0]
    ca3 = ca3space.build_ca3(rule, n, k)
    if rule == "pinverse":
        ca3.train(ca3space.code(rule, dense(idx, n)), method=rule)
    else:
        if counts is None or counts.p != p:
            raise ValueError("The local rules need pair counts of exactly the stored patterns")
        ca3.W, ca3.rule = weights(counts, rule, k), rule

    pick = ca3space.generator("cues", *seed_parts)
    target = (torch.randperm(p, generator=pick)[:max_cues] if p > max_cues
              else torch.arange(p))
    right = dense(idx[target], n)
    cues = torch.cat([ca3space.damage(right, r, s, ca3space.generator("damage", r, s, *seed_parts))
                      for r, s in conditions])
    targets = target.repeat(len(conditions))
    rights = right.repeat(len(conditions), 1)

    state, info = ca3.settle(ca3space.code(rule, cues),
                             generator=ca3space.generator("settle", *seed_parts))
    scores = score(cues > 0, state > 0, rights, idx, targets)
    scores["iterations"] = info["iterations"].float()
    scores["fixed"] = info["fixed"].float()

    m = len(target)
    out = []
    for i, (r, s) in enumerate(conditions):
        rows = slice(i * m, (i + 1) * m)
        out.append({"remove": r, "add": s, "cues": m,
                    "scores": {name: v[rows].mean().item() for name, v in scores.items()}})
    return out


def usage_cv(idx, n):
    """How unevenly patterns use the cells: the coefficient of variation
    (standard deviation over mean) of how many patterns each cell is in."""
    use = torch.bincount(idx.flatten(), minlength=n).double()
    return (use.std(unbiased=False) / use.mean()).item()


def duplicates(idx):
    return idx.shape[0] - torch.unique(idx.sort(dim=1).values, dim=0).shape[0]


def should_stop(rule, load, rows):
    """Whether random patterns stop climbing the load grid after this load."""
    if load < MIN_STOP_LOAD:
        return False
    cond = (0.4, 0.0) if rule == "pinverse" else (0.0, 0.0)
    row = [r for r in rows if (r["remove"], r["add"]) == cond][0]
    return row["scores"]["exact"] < STOP_BELOW


def candidate_loads(source, rule, n, available, max_load=None):
    """The grid loads a run may visit, in order.

    The pseudo-inverse stays below n, where its weights become the identity
    matrix. Drawings stop at the characters available and include that
    load.
    """
    top = max_load or GRID[-1]
    loads = [g for g in GRID if g <= top]
    if source == "drawings":
        loads = [g for g in loads if g < available] + ([available] if available <= top else [])
    if rule == "pinverse":
        loads = [g for g in loads if g < n]
    return loads


def drawing_pool(vc, n, k, seed):
    """DG's patterns for every drawing, as active-cell lists, in E1c's order."""
    X, _ = ca3space.drawing_patterns(vc, n, k, seed)
    return X.topk(k, dim=1).indices


def build_parser():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--source", required=True, choices=["random", "drawings"])
    p.add_argument("--split", default="evaluation", choices=["evaluation", "background"])
    p.add_argument("--rule", required=True, choices=RULES)
    p.add_argument("--units", type=int, default=225, help="DG and CA3 cells")
    p.add_argument("--sparsity", required=True, choices=SPARSITIES)
    p.add_argument("--seeds", type=int, default=10)
    p.add_argument("--loads", type=int, nargs="+", default=None,
                   help="fixed loads instead of the grid")
    p.add_argument("--max-load", type=int, default=None, help="highest grid load")
    p.add_argument("--threads", type=int, default=3)
    p.add_argument("--device", default="auto", help="device for the one-off vision encoding")
    p.add_argument("--checkpoint", default=str(omniglot.DEFAULT_CHECKPOINT))
    p.add_argument("--data-dir", default=str(omniglot.DEFAULT_DATA),
                   help="Omniglot folder with the background alphabets")
    p.add_argument("--eval-data-dir", default=str(omniglot.LOCAL_DATA),
                   help="folder with the evaluation alphabets")
    p.add_argument("--out", default=None)
    return p


def default_out(args, k):
    tag = args.source if args.source == "random" else "drawings_{}".format(args.split)
    return REPO / "results" / "e1d_ca3_{}_{}_{}_{}.json".format(tag, args.rule, args.units, k)


def _summarise(rows):
    for row in rows:
        row["summary"] = {m: ca3space.summarise(v) for m, v in row["per_seed"].items()}


def main(argv=None):
    args = build_parser().parse_args(argv)
    torch.set_num_threads(args.threads)
    n = args.units
    k, raised = active_cells(n, args.sparsity)
    out = Path(args.out) if args.out else default_out(args, k)

    available, data = None, None
    if args.source == "drawings":
        root = args.data_dir if args.split == "background" else args.eval_data_dir
        data = ca3space.encoded_characters(args.split, args.device, checkpoint=args.checkpoint,
                                           root=root)
        available = data["vc"].shape[0]

    record = json.loads(out.read_text()) if out.is_file() else None
    if record is not None and record.get("complete") and len(record["seeds"]) >= args.seeds:
        print("Keep {}".format(omniglot.portable(out)))
        return
    if record is None:
        notes = []
        if raised:
            notes.append("{}% of {:,} cells is under {} cells, so this run uses {}.".format(
                args.sparsity, n, MIN_K, MIN_K))
        if args.rule == "pinverse":
            notes.append("Pseudo-inverse loads stay below {:,}, where its weights become the "
                         "identity matrix.".format(n))
        if args.source == "drawings":
            notes.append("The {} alphabets hold {:,} characters, the highest load.".format(
                args.split, available))
        record = {
            "experiment": "e1d_ca3space", "source": args.source,
            "split": args.split if args.source == "drawings" else None,
            "rule": args.rule, "units": n, "k": k, "sparsity": args.sparsity,
            "k_raised": raised, "log_c": LOG_C, "characters_available": available,
            "loads": sorted(set(args.loads)) if args.loads else None,
            "seeds": [], "seconds_per_seed": [], "rows": [], "notes": notes,
            "settings": {"gain": ca3space.GAIN, "iterations": ca3space.ITERS,
                         "bipolar_update": round(ca3space.PAPER_UPDATE * n / ca3space.PAPER_UNITS),
                         "cue_weight": 0.0, "start": "cue", "max_cues": ca3space.MAX_CUES,
                         "draw_seed": 0, "stop_below": STOP_BELOW,
                         "min_stop_load": MIN_STOP_LOAD, "grid": list(GRID)},
            "checkpoint": omniglot.portable(args.checkpoint) if data else None,
            "machine": platform.platform(), "torch": torch.__version__,
            "complete": False,
        }

    rows_by_key = {(r["load"], r["remove"], r["add"]): r for r in record["rows"]}
    for seed in range(len(record["seeds"]), args.seeds):
        start = time.time()
        if args.source == "random":
            pool = RandomPool(n, k, seed)
        else:
            pool_idx = drawing_pool(data["vc"], n, k, seed)
            reference = RandomPool(n, k, seed)
        counts = PairCounts(n) if args.rule != "pinverse" else None
        fixed = record["loads"]
        loads = fixed or candidate_loads(args.source, args.rule, n, available, args.max_load)
        adaptive = fixed is None and args.source == "random"
        done, results = 0, []
        for load in loads:
            idx = pool.take(load) if args.source == "random" else pool_idx[:load]
            if counts is not None:
                counts.add(idx[done:load])
            done = load
            t = time.time()
            parts = (args.source, args.split if args.source == "drawings" else "-", n, k, load, seed)
            rows = run_load(args.rule, idx, n, k, parts, counts=counts)
            extra = {"usage_cv": usage_cv(idx, n), "duplicates": duplicates(idx),
                     "seconds": time.time() - t}
            if args.source == "drawings":
                extra["random_usage_cv"] = usage_cv(reference.take(load), n)
            results.append((load, rows, extra))
            print("seed {:>2} load {:>7,}  exact {}  ({:.0f} s)".format(
                seed, load, " ".join("{:.2f}".format(r["scores"]["exact"]) for r in rows),
                time.time() - start), flush=True)
            if adaptive and should_stop(args.rule, load, rows):
                break
        if fixed is None:
            record["loads"] = [load for load, _, _ in results]
        for load, rows, extra in results:
            for row in rows:
                key = (load, row["remove"], row["add"])
                if key not in rows_by_key:
                    rows_by_key[key] = {"load": load, "remove": row["remove"], "add": row["add"],
                                        "cues": row["cues"], "duplicates": [], "usage_cv": [],
                                        "seconds": [], "per_seed": {m: [] for m in row["scores"]}}
                    if "random_usage_cv" in extra:
                        rows_by_key[key]["random_usage_cv"] = []
                    record["rows"].append(rows_by_key[key])
                entry = rows_by_key[key]
                for m, v in row["scores"].items():
                    entry["per_seed"][m].append(v)
                for name in ("duplicates", "usage_cv", "seconds", "random_usage_cv"):
                    if name in extra:
                        entry[name].append(extra[name])
        record["seeds"].append(seed)
        record["seconds_per_seed"].append(time.time() - start)
        record["complete"] = len(record["seeds"]) >= args.seeds
        _summarise(record["rows"])
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(record, indent=2))
    print("Wrote {}".format(omniglot.portable(out)))


if __name__ == "__main__":
    main()
