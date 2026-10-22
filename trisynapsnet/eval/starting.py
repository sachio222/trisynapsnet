"""E8c: a familiarity signal read from CA3's starting state.

E8b's model, unchanged, with a third readout (docs/e8c_protocol.md):

R3, the starting state's recurrent support. When a test drawing arrives,
the perforant path drives CA3 and its most driven cells fire: the starting
state, before any attractor step. R3 is the mean recurrent input each of
those cells receives from the other active cells through CA3's stored
synapses, as a share of the most it could receive (every other active cell
potentiated onto it):

    R3 = (sum over j in A of sum over i in A of W[i, j]) / (|A| (|A| - 1))

with A the starting state's active cells and W[i, j] the synapse from cell
i onto cell j. With clipped binary synapses this is the share of the
starting state's own cell pairs whose synapse is potentiated; it is the
energy of the state in a Hopfield network with the sign reversed, the
quantity familiarity models read before any retrieval (Bogacz, Brown and
Giraud-Carrier 2001). It uses only the synapses and the cells now firing,
never a list of stored memories.

R3s, logged and scored beside it: E8b's self-support (R2's formula) of the
same starting state, the signal E8b logged as "cue self-support".

R1 (CA1 comparator) and R2 (self-support of the settled state) are E8b's
and are computed exactly as there; E8b's runner is not changed, so E8b's
results stay reproducible, and this module carries its own runner.

E8c is judged on lists built only from evaluation drawings that E8b's
128-drawing evaluation lists never used (`--pool e8b-unused`), with seeds
E8b never used; calibration stays on background lists built as in E8b.

Commands:
    python -m trisynapsnet.eval.starting run --split background
    python -m trisynapsnet.eval.starting run --split evaluation --pool e8b-unused --first-seed 100
    python -m trisynapsnet.eval.starting probe

Results go to results/e8c_*.json; scripts/make_e8c_table.py scores them.
"""

import argparse
import json
import platform
import time
from pathlib import Path

import torch

from trisynapsnet.data import omniglot
from trisynapsnet.eval import behaviour as bh
from trisynapsnet.eval import ca1space, ca3space
from trisynapsnet.eval import recognition as rc

RESULTS = rc.RESULTS
READOUTS = ("r1", "r2", "r3", "r3s")
# Arms where CA3's recurrent synapses take part: every starting-state and
# settled-state readout has a signal. Without recurrent synapses, or
# without CA3, there is nothing for R2, R3 or R3s to read.
RECURRENT_ARMS = ("intact", "no_dg") + tuple("pp_keep{:g}".format(f) for f in rc.PP_KEEP)
POOLS = ("all", "e8b-unused")
RESUME_KEYS = rc.RESUME_KEYS + ("pool",)
# E8b's 128-drawing evaluation lists: 10 seeds, 8 lists each (docs/e8b_protocol.md).
E8B_MAIN = {"split": "evaluation", "load": 128, "per_char": 1, "seeds": range(10), "lists": 8}


def start_support(W, states):
    """R3's signal: the mean recurrent input an active cell receives from the
    other active cells, as a share of the most it could receive.

    W[i, j] is the synapse from cell i onto cell j. For each state, with A
    its active cells and n = |A|:
        sum over j in A of sum over i in A of W[i, j]
        ---------------------------------------------
                         n (n - 1)
    0 when no two active cells are connected by a potentiated synapse, or
    when fewer than two cells are active; 1 when every pair is.
    """
    A = (states > 0).float()
    n = A.sum(dim=1)
    within = ((A @ W) * A).sum(dim=1)
    pairs = n * (n - 1)
    return torch.where(pairs > 0, within / pairs.clamp_min(1), torch.zeros_like(within))


class Memory(rc.Memory):
    """E8b's memory, with the starting-state readouts read off the same
    perforant cue that R1 and R2 then settle from."""

    @torch.no_grad()
    def recall(self, codes, arms):
        sig, ca3 = super().recall(codes, arms)
        n = codes.shape[0]
        sig["r3"], sig["r3s"] = {}, {}
        for arm in arms:
            if arm in RECURRENT_ARMS:
                cue = ca3[arm][0]
                sig["r3"][arm] = start_support(self.ca3.W, cue)
                sig["r3s"][arm] = rc.self_support(self.ca3.W, cue)
            elif arm == "vc_baseline":
                sig["r3"][arm] = sig["r1"][arm].clone()
                sig["r3s"][arm] = sig["r1"][arm].clone()
            else:
                sig["r3"][arm] = torch.zeros(n)
                sig["r3s"][arm] = torch.zeros(n)
        return sig, ca3

    def describe(self, state, paired):
        """E8b's description, plus two list lookups logged only, never used
        to decide: the largest share of the starting state's cells shared
        with any one stored pattern, and the share shared with the studied
        drawing's own pattern (-1 for foils)."""
        d = super().describe(state, paired)
        cue = (state[0] > 0).float()
        d["cue_nearest_overlap"] = rc.nearest_overlap(cue, self.stored).tolist()
        S = (self.stored > 0).float()
        on = cue.sum(dim=1).clamp_min(1)
        own = torch.full((cue.shape[0],), -1.0)
        has = paired >= 0
        own[has] = (cue[has] * S[paired[has]]).sum(dim=1) / on[has]
        d["cue_paired_overlap"] = own.tolist()
        return d


# ---------------------------------------------------------------- the held-out pool

def e8b_main_drawings(n_characters, spec=E8B_MAIN):
    """Every (character, drawer) that E8b's 128-drawing evaluation lists
    studied or tested, rebuilt from the same list generators."""
    used = set()
    for seed in spec["seeds"]:
        for i in range(spec["lists"]):
            lst = bh.build_list(n_characters, spec["load"], spec["per_char"],
                                ca3space.generator("e8 list", spec["split"], spec["load"],
                                                   spec["per_char"], seed, i))
            for c, d in lst["study"].tolist() + lst["test"].tolist():
                used.add((c, d))
    return used


def available_drawers(n_characters, excluded, drawers=omniglot.N_DRAWERS):
    """{character: sorted drawers not in excluded}."""
    return {c: [d for d in range(1, drawers + 1) if (c, d) not in excluded]
            for c in range(n_characters)}


def build_list_from(available, load, gen):
    """bh.build_list with one drawing per character, drawn only from
    `available` ({character: drawers}).

    Studied characters need two available drawings (one studied, one spare
    in case it becomes a lure source); foil characters need one. Half the
    studied drawings, chosen at random, come back as repeats; each of the
    other half has a lure, another available drawer's drawing of the same
    character. Returns the same dict as bh.build_list.
    """
    if load % 2:
        raise ValueError("load must be even")
    two = [c for c in sorted(available) if len(available[c]) >= 2]
    if len(two) < load:
        raise ValueError("only {} characters have two available drawings".format(len(two)))
    perm = torch.randperm(len(two), generator=gen).tolist()
    studied = [two[i] for i in perm[:load]]
    chosen = set(studied)
    one = [c for c in sorted(available) if available[c] and c not in chosen]
    if len(one) < load // 2:
        raise ValueError("not enough characters left for foils")
    fperm = torch.randperm(len(one), generator=gen).tolist()
    foil_chars = [one[i] for i in fperm[:load // 2]]
    study, spare = [], {}
    for c in studied:
        ds = available[c]
        order = [ds[i] for i in torch.randperm(len(ds), generator=gen).tolist()]
        study.append([c, order[0]])
        spare[c] = order[1:]
    halves = torch.randperm(load, generator=gen)
    repeats, lures = sorted(halves[:load // 2].tolist()), sorted(halves[load // 2:].tolist())
    test, types, paired = [], [], []
    for i in repeats:
        test.append(list(study[i]))
        types.append(0)
        paired.append(i)
    for i in lures:
        c = study[i][0]
        test.append([c, spare[c][0]])
        types.append(1)
        paired.append(i)
    for c in foil_chars:
        ds = available[c]
        d = ds[torch.randint(len(ds), (1,), generator=gen).item()]
        test.append([c, d])
        types.append(2)
        paired.append(-1)
    return {"study": torch.tensor(study), "test": torch.tensor(test),
            "types": torch.tensor(types), "paired": torch.tensor(paired)}


def make_list(pool, n_characters, available, split, load, per_char, seed, i):
    gen = ca3space.generator("e8 list" if pool == "all" else "e8c list", split, load, per_char,
                             seed, i)
    if pool == "all":
        return bh.build_list(n_characters, load, per_char, gen)
    if per_char != 1:
        raise ValueError("the held-out pool is built for one drawing per character")
    return build_list_from(available, load, gen)


# ---------------------------------------------------------------- the runner

def run_list(codes, lst, seed, baseline, arms, cfg, close=None):
    """rc.run_list with this module's Memory and readouts."""
    study = codes.dense([codes.index(c, d) for c, d in lst["study"].tolist()])
    test = codes.dense([codes.index(c, d) for c, d in lst["test"].tolist()])
    types, paired = lst["types"].clone(), lst["paired"].clone()
    level = torch.zeros(len(types), dtype=torch.long)
    if close is not None:
        ccodes, clevel, cpaired = close
        test = torch.cat([test, ccodes.float()])
        types = torch.cat([types, torch.full((len(clevel),), 3, dtype=types.dtype)])
        paired = torch.cat([paired, cpaired])
        level = torch.cat([level, clevel])
    out = {"signal": {r: {} for r in READOUTS}, "ca3": {}, "types": types.tolist(),
           "paired": paired.tolist(), "level": level.tolist()}
    shared = rc.Study(study, seed, cfg)
    shared.share_plateaus(test, baseline, cfg, seed)
    groups = ([(None, [a for a in arms if a in rc.SHARED_ARMS])]
              if any(a in rc.SHARED_ARMS for a in arms) else [])
    groups += [(a, [a]) for a in arms if a in rc.STUDY_ARMS]
    for lesion, group in groups:
        mem = Memory(study, seed, baseline, cfg, shared, lesion=lesion)
        sig, states = mem.recall(test, group)
        for arm in group:
            for r in READOUTS:
                out["signal"][r][arm] = sig[r][arm].tolist()
            if arm in states and arm in rc.CA3_ARMS:
                out["ca3"][arm] = mem.describe(states[arm], paired)
        del mem
    out["similarity"] = bh.lure_similarity(test, study, paired).tolist()
    return out


def default_out(args):
    return RESULTS / "e8c_{}_n{}_d{}.json".format(args.split, args.load, args.per_char)


def cmd_run(args):
    torch.set_num_threads(args.threads)
    if args.lists is None:
        args.lists = bh.lists_per_seed(args.load)
    if args.pool == "e8b-unused" and args.split != "evaluation":
        raise SystemExit("the held-out pool is defined on the evaluation alphabets")
    cfg = rc.scaled_model(args.denominator)
    out = Path(args.out) if args.out else default_out(args)
    seeds = list(range(args.first_seed, args.first_seed + args.seeds))
    recorded = bh.recorded_args(args)
    recorded.pop("func", None)
    record = None
    if out.is_file():
        record = json.loads(out.read_text())
        mismatch = [k for k in RESUME_KEYS if record["args"].get(k) != recorded.get(k)]
        if mismatch:
            raise SystemExit("{} was made with other settings ({})".format(
                omniglot.portable(out), ", ".join(mismatch)))
        if set(seeds) <= set(record["seeds_done"]):
            print("Every seed is done already: {}".format(omniglot.portable(out)))
            return record
    done = set(record["seeds_done"]) if record else set()
    per_seed = record["per_seed"] if record else {}
    codes = bh.Codes(bh.encode_split(args.split))
    available = None
    if args.pool == "e8b-unused":
        available = available_drawers(codes.n_characters, e8b_main_drawings(codes.n_characters))
    baseline = ca1space.background_reference(str(bh.CACHE))[0]
    magnitudes = None
    encoder = None
    if args.close:
        lv = json.loads((RESULTS / "e8b_lure_levels.json").read_text())
        magnitudes = [x["magnitude"] for x in lv["levels"]]
        encoder = rc.Encoder(args.split, args.checkpoint)
    print("E8c {} pool {} load {}, {} lists per seed, seeds {}, arms {}, model 1/{} "
          "(DG {}, CA3 {}, CA1 {}); done {}".format(
              args.split, args.pool, args.load, args.lists, seeds, " ".join(args.arms),
              args.denominator, cfg["dg_units"], cfg["ca3_units"], cfg["ca1_units"],
              sorted(done)), flush=True)
    start = time.time()
    for seed in seeds:
        if seed in done:
            continue
        items = {"types": [], "paired": [], "level": [], "test": [], "similarity": [],
                 "signal": {r: {a: [] for a in args.arms} for r in READOUTS}, "ca3": {}}
        for i in range(args.lists):
            lst = make_list(args.pool, codes.n_characters, available, args.split, args.load,
                            args.per_char, seed, i)
            close = None
            if args.close:
                close = rc.closer_lures(encoder, codes, lst, magnitudes,
                                        ca3space.generator("e8b distort", args.split, args.load,
                                                           args.per_char, seed, i))
            res = run_list(codes, lst, seed * 1000 + i, baseline, args.arms, cfg, close=close)
            n_main = len(lst["types"])
            for key in ("types", "paired", "level"):
                items[key] += res[key]
            items["test"] += lst["test"].tolist() + [[-1, -1]] * (len(res["types"]) - n_main)
            items["similarity"] += bh.round_list(res["similarity"])
            for r in READOUTS:
                for arm in args.arms:
                    items["signal"][r][arm] += bh.round_list(res["signal"][r][arm])
            for arm, d in res["ca3"].items():
                slot = items["ca3"].setdefault(arm, {k: [] for k in d})
                for k, v in d.items():
                    slot[k] += bh.round_list(v) if isinstance(v[0], float) else v
        per_seed[str(seed)] = items
        done.add(seed)
        print("seed {} done ({:.0f} s, peak {:.2f} GB)".format(
            seed, time.time() - start, rc.peak_rss_gb()), flush=True)
        record = {"experiment": "e8c", "args": recorded, "model": cfg,
                  "types": list(rc.TYPES), "readouts": list(READOUTS),
                  "lure_magnitudes": magnitudes, "seeds_done": sorted(done),
                  "per_seed": per_seed, "complete": done >= set(seeds),
                  "machine": platform.platform(), "torch": torch.__version__,
                  "seconds": (record or {}).get("seconds", 0.0) + time.time() - start,
                  "peak_rss_gb": max((record or {}).get("peak_rss_gb", 0.0), rc.peak_rss_gb())}
        start = time.time()
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix(".tmp")
        tmp.write_text(json.dumps(record))
        tmp.replace(out)
    print("Wrote {}".format(omniglot.portable(out)), flush=True)
    return record


def cmd_pool(args):
    """How many evaluation drawings and characters the held-out pool has."""
    codes = bh.Codes(bh.encode_split("evaluation"))
    used = e8b_main_drawings(codes.n_characters)
    avail = available_drawers(codes.n_characters, used)
    sizes = [len(v) for v in avail.values()]
    summary = {"characters": codes.n_characters, "drawings": codes.n_characters * omniglot.N_DRAWERS,
               "used_by_e8b_main": len(used), "held_out": sum(sizes),
               "characters_with_two": sum(s >= 2 for s in sizes),
               "characters_with_one": sum(s >= 1 for s in sizes)}
    print(json.dumps(summary))
    return summary


def build_parser():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="command", required=True)
    po = sub.add_parser("pool", help="size of the held-out evaluation pool, no model run")
    po.set_defaults(func=cmd_pool)
    r = sub.add_parser("run", help="one condition, every seed")
    r.add_argument("--split", default="background", choices=list(bh.SPLITS))
    r.add_argument("--pool", default="all", choices=list(POOLS))
    r.add_argument("--load", type=int, default=rc.HUMAN_LOAD)
    r.add_argument("--per-char", type=int, default=1)
    r.add_argument("--lists", type=int, default=None)
    r.add_argument("--arms", nargs="+", default=list(rc.ARMS), choices=list(rc.ARMS))
    r.add_argument("--seeds", type=int, default=10)
    r.add_argument("--first-seed", type=int, default=0)
    r.add_argument("--threads", type=int, default=2)
    r.add_argument("--denominator", type=int, default=rc.DENOMINATOR)
    r.add_argument("--no-close", dest="close", action="store_false",
                   help="skip the closer-lure set")
    r.add_argument("--checkpoint", default=str(omniglot.DEFAULT_CHECKPOINT))
    r.add_argument("--cache-dir", default=str(bh.CACHE))
    r.add_argument("--out", default=None)
    r.set_defaults(func=cmd_run)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    main()
