"""E9: DG drives CA3 at recall as well as at storage.

E8c's model, with one change in the circuit (docs/e9_protocol.md): during
attractor dynamics CA3 receives, besides its recurrent input, the
perforant path's input (entorhinal input stays on while the item is in
view) and DG's response to the test drawing through the mossy fibres.

- DG responds to the test drawing through its fixed EC-to-DG weights, with
  AHA's record of recently active granule cells frozen at the end of study.
- The perforant path alone sets CA3's starting state, as in E8c; EC and DG
  input join from the first round of attractor dynamics and stay on.
- Inputs are in units of one potentiated recurrent synapse from an active
  CA3 cell: a potentiated perforant synapse from an active EC unit is worth
  0.34 / 0.56 units (Baker and colleagues 2011, Table 4; Guzman and
  colleagues 2016), and the mossy weights are rescaled to a mean of
  9.6 / 0.56 units (main; Vyleta and colleagues 2016) or 1 / 0.54 units
  (lower bound, peak conductances; Jonas, Major and Sakmann 1993).
- 68 CA3 cells fire in every round (k-winners-take-all), as in E8c.

Four conditions are recalled from the same study of each list:
    e8c      E8c's model: recurrent input only after the starting state
             (the reproduction control; its signals must equal E8c's)
    ec       EC input kept on, no DG input (the control H1 to H3 use)
    dg1.9    EC input and DG input at 1.9 units
    dg17.1   EC input and DG input at 17.1 units (the main condition)

No readout is new: R1, R2, R3 and R3s are E8c's, R1 and R2 read from the
final state reached under input. Whether a final state is a stored pattern
is logged from the stored list as a check, never used to decide.

E8c's runner is not changed; this module carries its own.

Commands:
    python -m trisynapsnet.eval.dgrecall run --split background
    python -m trisynapsnet.eval.dgrecall run --split evaluation --first-seed 200

Results go to results/e9_<split>_n<load>_d<per_char>_<condition>.json;
scripts/make_e9_table.py scores them.
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
from trisynapsnet.eval import starting as st
from trisynapsnet.model import modules

RESULTS = rc.RESULTS
READOUTS = st.READOUTS
CONDITIONS = ("e8c", "ec", "dg1.9", "dg17.1")

# Unit of input: one potentiated recurrent CA3 synapse from an active cell.
RECURRENT_EPSP_MV = 0.56        # Guzman and colleagues 2016, somatic unitary EPSP
RECURRENT_CONDUCTANCE_NS = 0.54  # Guzman and colleagues 2016, peak conductance
PERFORANT_EPSP_MV = 0.34        # Baker and colleagues 2011, Table 4 (model prediction)
MOSSY_EPSP_MV = 9.6             # Vyleta and colleagues 2016
MOSSY_CONDUCTANCE_NS = 1.0      # Jonas, Major and Sakmann 1993, excluding failures
PERFORANT_UNITS = PERFORANT_EPSP_MV / RECURRENT_EPSP_MV        # 0.607
MOSSY_UNITS_MAIN = MOSSY_EPSP_MV / RECURRENT_EPSP_MV           # 17.14
MOSSY_UNITS_LOW = MOSSY_CONDUCTANCE_NS / RECURRENT_CONDUCTANCE_NS  # 1.85

# What each condition adds to CA3's recurrent input during attractor dynamics.
SETTINGS = {"e8c": {"ec": False, "mossy": None},
            "ec": {"ec": True, "mossy": None},
            "dg1.9": {"ec": True, "mossy": MOSSY_UNITS_LOW},
            "dg17.1": {"ec": True, "mossy": MOSSY_UNITS_MAIN}}
# Arms whose CA3 runs attractor dynamics in every condition.
DYNAMIC_ARMS = ("intact", "no_recurrent", "no_dg") + tuple(
    "pp_keep{:g}".format(f) for f in rc.PP_KEEP)
# Arms with recurrent synapses for R2, R3 and R3s to read.
RECURRENT_ARMS = st.RECURRENT_ARMS
RESUME_KEYS = rc.RESUME_KEYS + ("conditions",)


# ---------------------------------------------------------------- DG at test

def end_of_study_record(dg_patterns, gamma):
    """AHA's record of recently active granule cells after the study list.

    Replays modules.InhibitionMask over the study patterns in study order
    (each cell that fires is fully inhibited, and the inhibition decays by
    gamma with every later drawing) and returns the mask DG multiplies its
    drive by, 1 - inhibition, shape (1, cells). It is the mask StreamDG
    holds after processing the study list.
    """
    phi = modules.InhibitionMask(dg_patterns.shape[1], gamma)
    for row in (dg_patterns > 0).float():
        phi.update(row[None, :])
    return phi()


def dg_response(dg, codes, mask):
    """DG's response to test drawings: the k most driven granule cells, with
    the drive scaled by the frozen record of recently active cells. The
    record does not change during the test, so items do not affect one
    another."""
    return modules.kwta(dg.drive(codes) * mask, dg.k)


def mossy_units(mossy, raw_drive, strength):
    """Mossy drive in units of a recurrent synapse: the raw drive (sum of the
    fixed weights from active granule cells) times strength / mean weight,
    so the mean weight equals `strength` and the random spread is kept."""
    return raw_drive * (strength / mossy.w.mean().item())


def perforant_units(pp, codes):
    """Perforant input to every CA3 cell during attractor dynamics, in units:
    PERFORANT_UNITS for each active EC unit on a potentiated perforant
    synapse (clipped binary; unpotentiated synapses are zero)."""
    return PERFORANT_UNITS * (pp.active(codes) @ pp.W.T)


def attractor_dynamics(W, start, external, k, n_iter):
    """Synchronous k-winners-take-all rounds from a starting state, with a
    constant external input.

    Each round every cell sums its recurrent input from the cells now active
    (state @ W) plus `external`, and the k most driven cells fire next. The
    rounds stop when no item's state changes, or after n_iter rounds, as in
    modules.CA3._settle_sparse; with external = 0 the states are exactly
    E8c's. Returns (final states, rounds that changed each item's state,
    whether each item reached a fixed point).
    """
    state = start.clone()
    ext = external if torch.is_tensor(external) else torch.zeros_like(start)
    rounds = torch.zeros(start.shape[0], dtype=torch.long)
    fixed = torch.zeros(start.shape[0], dtype=torch.bool)
    for _ in range(n_iter):
        new = modules.kwta(state @ W + ext, k)
        same = (new == state).all(dim=1)
        fixed |= same
        rounds += (~same).long()
        if torch.equal(new, state):
            break
        state = new
    return state, rounds, fixed


class Study(rc.Study):
    """E8b's shared study, plus DG's response to the test items and the mossy
    drive it sends to CA3."""

    def __init__(self, study_codes, seed, cfg):
        super().__init__(study_codes, seed, cfg)
        self.dg = rc.StreamDG(study_codes.shape[1], cfg["dg_units"], cfg["dg_k"],
                              cfg["dg_gamma"], cfg["dg_knockout"], seed=seed)
        self.dg_record = end_of_study_record(self.dg_patterns, cfg["dg_gamma"])
        self.k = cfg["ca3_k"]
        self.dg_test = None
        self.mossy_test = None

    def respond(self, test_codes):
        """DG's response to the test items and its raw mossy drive to CA3."""
        self.dg_test = dg_response(self.dg, test_codes, self.dg_record)
        self.mossy_test = self.mossy.drive(self.dg_test)
        self.dg_pattern = modules.kwta(self.mossy_test, self.k)
        return self.dg_test

    def dg_paired_overlap(self, paired):
        """Logged only: the share of each test item's DG cells that its paired
        studied drawing's DG pattern also has (-1 for foils)."""
        out = torch.full((len(paired),), -1.0)
        has = paired >= 0
        D, S = (self.dg_test > 0).float(), (self.dg_patterns > 0).float()
        out[has] = (D[has] * S[paired[has]]).sum(dim=1) / D[has].sum(dim=1).clamp_min(1)
        return out


class Memory(st.Memory):
    """E8c's memory; recall under each condition from the same study."""

    def external(self, codes, arm, condition, shared, pp_input=None):
        cfg = SETTINGS[condition]
        ext = torch.zeros(codes.shape[0], self.cfg["ca3_units"])
        if cfg["ec"]:
            ext = ext + (perforant_units(self.pp, codes) if pp_input is None else pp_input)
        if cfg["mossy"] is not None and arm != "no_dg":
            ext = ext + mossy_units(shared.mossy, shared.mossy_test, cfg["mossy"])
        return ext

    @torch.no_grad()
    def recall_conditions(self, codes, arms, conditions, shared):
        """{condition: (signals, states, dynamics)}.

        "e8c" is E8c's recall exactly (st.Memory.recall). Every other
        condition starts from the same perforant starting state and runs
        attractor dynamics under its external input.
        """
        sig0, states0 = self.recall(codes, arms)
        out = {"e8c": (sig0, states0, {})}
        n, k = codes.shape[0], self.cfg["ca3_k"]
        zeros = torch.zeros(n)
        pp_input = perforant_units(self.pp, codes)
        for c in conditions:
            if c == "e8c":
                continue
            sig = {r: {} for r in READOUTS}
            states, dyn = {}, {}
            for arm in arms:
                if arm not in DYNAMIC_ARMS:
                    for r in READOUTS:
                        sig[r][arm] = sig0[r][arm].clone()
                    continue
                cue = states0[arm][0]
                W = self.ca3.W if arm != "no_recurrent" else torch.zeros_like(self.ca3.W)
                ext = self.external(codes, arm, c, shared, pp_input)
                final, rounds, fixed = attractor_dynamics(W, cue, ext, k, self.cfg["ca3_iters"])
                sig["r1"][arm] = bh.cosine_rows(codes, self.returned(final))
                if arm in RECURRENT_ARMS:
                    sig["r2"][arm] = rc.self_support(self.ca3.W, final)
                    sig["r3"][arm] = st.start_support(self.ca3.W, cue)
                    sig["r3s"][arm] = rc.self_support(self.ca3.W, cue)
                else:
                    for r in ("r2", "r3", "r3s"):
                        sig[r][arm] = zeros.clone()
                states[arm] = (cue, final)
                dyn[arm] = {"rounds": rounds, "fixed": fixed}
            out[c] = (sig, states, dyn)
        return out

    def describe_condition(self, state, paired, dyn, shared, arm):
        """E8b's CA3 log for a condition's final state (cue size, exact
        landing, nearest-pattern overlap, the starting state's self-support),
        plus rounds, fixed point and the share of the final state's cells in
        DG's own pattern (-1 without DG). Logged only."""
        cue, final = state
        d = rc.ca3_description(cue, final, self.stored, paired)
        d["nearest_overlap"] = rc.nearest_overlap(final, self.stored).tolist()
        d["cue_support"] = rc.self_support(self.ca3.W, cue).tolist()
        d["rounds"] = dyn["rounds"].tolist()
        d["fixed"] = dyn["fixed"].int().tolist()
        if arm == "no_dg":
            d["dg_follow"] = [-1.0] * final.shape[0]
        else:
            A = (final > 0).float()
            d["dg_follow"] = ((A * shared.dg_pattern).sum(dim=1)
                              / A.sum(dim=1).clamp_min(1)).tolist()
        return d


# ---------------------------------------------------------------- one list

def run_list(codes, lst, seed, baseline, arms, cfg, close=None, conditions=CONDITIONS):
    """Every readout for every arm and condition on one list.

    Returns {"types", "paired", "level", "similarity", "dg_paired_overlap",
    "conditions": {condition: {"signal": ..., "ca3": ...}}}; the "e8c"
    entry is exactly what st.run_list gives.
    """
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
    out = {"types": types.tolist(), "paired": paired.tolist(), "level": level.tolist(),
           "conditions": {c: {"signal": {r: {} for r in READOUTS}, "ca3": {}}
                          for c in conditions}}
    shared = Study(study, seed, cfg)
    shared.share_plateaus(test, baseline, cfg, seed)
    shared.respond(test)
    groups = ([(None, [a for a in arms if a in rc.SHARED_ARMS])]
              if any(a in rc.SHARED_ARMS for a in arms) else [])
    groups += [(a, [a]) for a in arms if a in rc.STUDY_ARMS]
    for lesion, group in groups:
        mem = Memory(study, seed, baseline, cfg, shared, lesion=lesion)
        res = mem.recall_conditions(test, group, conditions, shared)
        for c in conditions:
            sig, states, dyn = res[c]
            slot = out["conditions"][c]
            for arm in group:
                for r in READOUTS:
                    slot["signal"][r][arm] = sig[r][arm].tolist()
                if arm in states and arm in rc.CA3_ARMS:
                    if c == "e8c":
                        slot["ca3"][arm] = mem.describe(states[arm], paired)
                    else:
                        slot["ca3"][arm] = mem.describe_condition(states[arm], paired, dyn[arm],
                                                                  shared, arm)
        del mem
    out["similarity"] = bh.lure_similarity(test, study, paired).tolist()
    out["dg_paired_overlap"] = shared.dg_paired_overlap(paired).tolist()
    return out


# ---------------------------------------------------------------- the runner

def out_paths(prefix, conditions):
    return {c: Path("{}_{}.json".format(prefix, c)) for c in conditions}


def default_prefix(args):
    return RESULTS / "e9_{}_n{}_d{}".format(args.split, args.load, args.per_char)


def empty_items(arms):
    return {"types": [], "paired": [], "level": [], "test": [], "similarity": [],
            "dg_paired_overlap": [],
            "signal": {r: {a: [] for a in arms} for r in READOUTS}, "ca3": {}}


def cmd_run(args):
    torch.set_num_threads(args.threads)
    if args.lists is None:
        args.lists = bh.lists_per_seed(args.load)
    cfg = rc.scaled_model(args.denominator)
    prefix = Path(args.out) if args.out else default_prefix(args)
    paths = out_paths(prefix, args.conditions)
    seeds = list(range(args.first_seed, args.first_seed + args.seeds))
    recorded = bh.recorded_args(args)
    recorded.pop("func", None)
    records = {}
    for c, path in paths.items():
        if path.is_file():
            rec = json.loads(path.read_text())
            mismatch = [k for k in RESUME_KEYS if rec["args"].get(k) != recorded.get(k)]
            if mismatch:
                raise SystemExit("{} was made with other settings ({})".format(
                    omniglot.portable(path), ", ".join(mismatch)))
            records[c] = rec
    done_sets = [set(records[c]["seeds_done"]) if c in records else set() for c in paths]
    done = set.intersection(*done_sets) if done_sets else set()
    if set(seeds) <= done:
        print("Every seed is done already: {}_*.json".format(omniglot.portable(prefix)))
        return records
    per_seed = {c: (records[c]["per_seed"] if c in records else {}) for c in paths}
    codes = bh.Codes(bh.encode_split(args.split))
    baseline = ca1space.background_reference(str(bh.CACHE))[0]
    magnitudes = None
    encoder = None
    if args.close:
        lv = json.loads((RESULTS / "e8b_lure_levels.json").read_text())
        magnitudes = [x["magnitude"] for x in lv["levels"]]
        encoder = rc.Encoder(args.split, args.checkpoint)
    print("E9 {} load {}, {} lists per seed, seeds {}, arms {}, conditions {}, model 1/{} "
          "(DG {}, CA3 {}, CA1 {}); done {}".format(
              args.split, args.load, args.lists, seeds, " ".join(args.arms),
              " ".join(args.conditions), args.denominator, cfg["dg_units"], cfg["ca3_units"],
              cfg["ca1_units"], sorted(done)), flush=True)
    start = time.time()
    for seed in seeds:
        if seed in done:
            continue
        items = {c: empty_items(args.arms) for c in args.conditions}
        for i in range(args.lists):
            lst = bh.build_list(codes.n_characters, args.load, args.per_char,
                                ca3space.generator("e8 list", args.split, args.load,
                                                   args.per_char, seed, i))
            close = None
            if args.close:
                close = rc.closer_lures(encoder, codes, lst, magnitudes,
                                        ca3space.generator("e8b distort", args.split, args.load,
                                                           args.per_char, seed, i))
            res = run_list(codes, lst, seed * 1000 + i, baseline, args.arms, cfg, close=close,
                           conditions=args.conditions)
            n_main = len(lst["types"])
            for c in args.conditions:
                it = items[c]
                for key in ("types", "paired", "level"):
                    it[key] += res[key]
                it["test"] += lst["test"].tolist() + [[-1, -1]] * (len(res["types"]) - n_main)
                it["similarity"] += bh.round_list(res["similarity"])
                it["dg_paired_overlap"] += bh.round_list(res["dg_paired_overlap"])
                cres = res["conditions"][c]
                for r in READOUTS:
                    for arm in args.arms:
                        it["signal"][r][arm] += bh.round_list(cres["signal"][r][arm])
                for arm, d in cres["ca3"].items():
                    slot = it["ca3"].setdefault(arm, {k: [] for k in d})
                    for k, v in d.items():
                        slot[k] += bh.round_list(v) if isinstance(v[0], float) else v
        elapsed = time.time() - start
        for c in args.conditions:
            per_seed[c][str(seed)] = items[c]
        done.add(seed)
        print("seed {} done ({:.0f} s, peak {:.2f} GB)".format(seed, elapsed, rc.peak_rss_gb()),
              flush=True)
        for c, path in paths.items():
            old = records.get(c) or {}
            rec = {"experiment": "e9", "condition": c, "settings": SETTINGS[c],
                   "units": {"perforant": PERFORANT_UNITS, "mossy_main": MOSSY_UNITS_MAIN,
                             "mossy_low": MOSSY_UNITS_LOW},
                   "args": recorded, "model": cfg, "types": list(rc.TYPES),
                   "readouts": list(READOUTS), "lure_magnitudes": magnitudes,
                   "seeds_done": sorted(done), "per_seed": per_seed[c],
                   "complete": done >= set(seeds), "machine": platform.platform(),
                   "torch": torch.__version__,
                   "seconds": old.get("seconds", 0.0) + elapsed,
                   "peak_rss_gb": max(old.get("peak_rss_gb", 0.0), rc.peak_rss_gb())}
            records[c] = rec
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(rec))
            tmp.replace(path)
        start = time.time()
    print("Wrote {}_*.json".format(omniglot.portable(prefix)), flush=True)
    return records


def build_parser():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run", help="every condition, every seed")
    r.add_argument("--split", default="background", choices=list(bh.SPLITS))
    r.add_argument("--load", type=int, default=rc.HUMAN_LOAD)
    r.add_argument("--per-char", type=int, default=1)
    r.add_argument("--lists", type=int, default=None)
    r.add_argument("--arms", nargs="+", default=list(rc.ARMS), choices=list(rc.ARMS))
    r.add_argument("--conditions", nargs="+", default=list(CONDITIONS), choices=list(CONDITIONS))
    r.add_argument("--seeds", type=int, default=10)
    r.add_argument("--first-seed", type=int, default=0)
    r.add_argument("--threads", type=int, default=2)
    r.add_argument("--denominator", type=int, default=rc.DENOMINATOR)
    r.add_argument("--no-close", dest="close", action="store_false",
                   help="skip the closer-lure set")
    r.add_argument("--checkpoint", default=str(omniglot.DEFAULT_CHECKPOINT))
    r.add_argument("--cache-dir", default=str(bh.CACHE))
    r.add_argument("--out", default=None, help="path prefix; one file per condition")
    r.set_defaults(func=cmd_run)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    main()
