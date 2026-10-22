"""E8c: the starting-state readout R3, the held-out evaluation pool and the
runner that adds R3 to E8b's readouts."""

import inspect

import pytest
import torch

from trisynapsnet.eval import behaviour as bh
from trisynapsnet.eval import recognition as rc
from trisynapsnet.eval import starting as st
from trisynapsnet.model import modules

from test_behaviour import fake_codes, sparse_codes


def clipped(patterns, n):
    W = torch.zeros(n, n)
    for pat in patterns:
        for i in pat:
            for j in pat:
                if i != j:
                    W[i, j] = 1.0
    return W


# ------------------------------------------------------------ R3's signal

def test_start_support_by_hand():
    # Cells 0-2 store one pattern, cells 2-4 another (clipped binary).
    W = clipped(([0, 1, 2], [2, 3, 4]), 6)
    states = torch.zeros(5, 6)
    states[0, [0, 1, 2]] = 1   # a stored pattern: all 6 ordered pairs potentiated
    states[1, [0, 1, 3]] = 1   # a mixture: only 0<->1 (2 of 6)
    states[2, [5]] = 1         # one cell: no pairs
    states[3, [0, 1]] = 1      # part of a stored pattern: 2 of 2
    states[4, [0, 3, 5]] = 1   # no potentiated pair
    s = st.start_support(W, states)
    assert s.tolist() == pytest.approx([1.0, 2 / 6, 0.0, 1.0, 0.0])


def test_start_support_differs_from_self_support_on_shared_cells():
    # Cell 2 belongs to both stored patterns. Self-support divides by all
    # potentiated input onto the active cells, so the shared cell's extra
    # input from pattern B lowers it; R3 counts only pairs inside the state.
    W = clipped(([0, 1, 2], [2, 3, 4]), 6)
    state = torch.zeros(1, 6)
    state[0, [0, 1, 2]] = 1
    assert st.start_support(W, state).item() == pytest.approx(1.0)
    assert rc.self_support(W, state).item() == pytest.approx(6 / 8)


def test_start_support_reads_only_synapses_and_firing():
    assert list(inspect.signature(st.start_support).parameters) == ["W", "states"]


def test_start_support_grows_with_overlap_with_a_stored_pattern():
    ca3 = modules.CA3(200, k=10, start="cue")
    pats = torch.zeros(5, 200)
    for p in range(5):
        pats[p, p * 20:p * 20 + 10] = 1
    ca3.train(pats, "willshaw")
    values = []
    for keep in (10, 8, 5, 2):
        state = torch.zeros(1, 200)
        state[0, :keep] = 1                 # keep cells of pattern 0
        state[0, 150:150 + 10 - keep] = 1   # the rest from cells no pattern uses
        values.append(st.start_support(ca3.W, state).item())
    assert values == sorted(values, reverse=True)
    assert values[0] == pytest.approx(1.0)
    assert values[-1] == pytest.approx(2 / 90)


# ------------------------------------------------------------ the runner

def test_memory_adds_starting_state_readouts_and_keeps_e8bs():
    dim, seed = 2000, 5
    cfg = rc.scaled_model(4000)
    study = sparse_codes(10, dim, 80, seed=7)
    shared = rc.Study(study, seed, cfg)
    base = torch.zeros(dim)
    old = rc.Memory(study, seed, base, cfg, shared)
    new = st.Memory(study, seed, base, cfg, shared)
    s_old, _ = old.recall(study, list(rc.SHARED_ARMS))
    s_new, states = new.recall(study, list(rc.SHARED_ARMS))
    # R1 and R2 are E8b's, unchanged.
    for r in ("r1", "r2"):
        for arm in rc.SHARED_ARMS:
            assert torch.equal(s_old[r][arm], s_new[r][arm])
    # R3 and R3s come from the perforant cue, before any attractor step.
    cue = new.pp.cue(study)
    assert torch.equal(states["intact"][0], cue)
    assert torch.allclose(s_new["r3"]["intact"], st.start_support(new.ca3.W, cue))
    assert torch.allclose(s_new["r3s"]["intact"], rc.self_support(new.ca3.W, cue))
    # Studied drawings start on most of their own pattern.
    assert s_new["r3"]["intact"].mean() > 0.5
    # Nothing to read without recurrent synapses or without CA3.
    for r in ("r3", "r3s"):
        assert torch.all(s_new[r]["no_recurrent"] == 0) and torch.all(s_new[r]["no_ca3"] == 0)
        assert torch.equal(s_new[r]["vc_baseline"], s_new["r1"]["vc_baseline"])


def test_run_list_gives_every_readout_for_every_arm():
    codes, _ = fake_codes(n_characters=40, dim=600)
    lst = bh.build_list(codes.n_characters, 10, 1, torch.Generator().manual_seed(4))
    cfg = rc.scaled_model(8000)
    src = lst["paired"][lst["types"] == 1]
    study = codes.dense([codes.index(c, d) for c, d in lst["study"].tolist()])
    close = (torch.cat([study[src]] * 5), torch.arange(1, 6).repeat_interleave(len(src)),
             torch.cat([src] * 5))
    out = st.run_list(codes, lst, 3, torch.zeros(600), list(rc.ARMS), cfg, close=close)
    old = rc.run_list(codes, lst, 3, torch.zeros(600), list(rc.ARMS), cfg, close=close)
    for r in st.READOUTS:
        assert set(out["signal"][r]) == set(rc.ARMS)
        assert all(len(v) == 40 for v in out["signal"][r].values())
    for r in rc.READOUTS:
        assert out["signal"][r] == old["signal"][r]
    r3 = torch.tensor(out["signal"]["r3"]["intact"])
    assert r3.min() >= 0 and r3.max() <= 1
    # R3s is what E8b logged as the cue's self-support.
    assert out["signal"]["r3s"]["intact"] == pytest.approx(out["ca3"]["intact"]["cue_support"])
    # The logged list lookups: foils have no paired pattern; repeats start
    # on part of their own pattern, never more than the whole of it.
    own = torch.tensor(out["ca3"]["intact"]["cue_paired_overlap"])
    types = torch.tensor(out["types"])
    assert torch.all(own[types == 2] == -1)
    assert torch.all((own[types == 0] > 0) & (own[types == 0] <= 1))
    near = torch.tensor(out["ca3"]["intact"]["cue_nearest_overlap"])
    assert torch.all(near[types == 0] >= own[types == 0] - 1e-6)


# ------------------------------------------------------------ the held-out pool

def test_e8b_main_drawings_are_the_lists_e8b_built():
    spec = dict(st.E8B_MAIN, seeds=range(2), lists=2)
    used = st.e8b_main_drawings(300, spec)
    again = set()
    for seed in range(2):
        for i in range(2):
            lst = bh.build_list(300, 128, 1, bh.ca3space.generator(
                "e8 list", "evaluation", 128, 1, seed, i))
            again |= {tuple(x) for x in lst["study"].tolist() + lst["test"].tolist()}
    assert used == again


def test_lists_from_the_pool_use_only_available_drawings():
    excluded = {(c, d) for c in range(300) for d in range(1, 21) if (c * 7 + d) % 5}
    avail = st.available_drawers(300, excluded)
    lst = st.build_list_from(avail, 128, torch.Generator().manual_seed(0))
    for c, d in lst["study"].tolist() + lst["test"].tolist():
        assert (c, d) not in excluded
    types, paired = lst["types"], lst["paired"]
    assert (types == 0).sum() == 64 and (types == 1).sum() == 64 and (types == 2).sum() == 64
    study = lst["study"].tolist()
    test = lst["test"].tolist()
    # Repeats are the studied drawing; lures the same character by another drawer.
    for t, p, item in zip(types.tolist(), paired.tolist(), test):
        if t == 0:
            assert item == study[p]
        elif t == 1:
            assert item[0] == study[p][0] and item[1] != study[p][1]
    # Foils are characters never studied; every studied character is distinct.
    studied = {c for c, _ in study}
    assert len(studied) == 128
    assert not studied & {c for (c, _), t in zip(test, types.tolist()) if t == 2}
    # The same generator gives the same list.
    again = st.build_list_from(avail, 128, torch.Generator().manual_seed(0))
    assert torch.equal(again["test"], lst["test"])


def test_pool_lists_refuse_when_too_few_characters():
    avail = {c: [1, 2] for c in range(100)}
    with pytest.raises(ValueError):
        st.build_list_from(avail, 128, torch.Generator().manual_seed(0))


def test_background_lists_are_e8bs_lists():
    # Calibration lists on the background alphabets are built exactly as
    # E8b built them, so R1 and R2 there reproduce E8b's signals.
    lst = st.make_list("all", 900, None, "background", 128, 1, 3, 2)
    ref = bh.build_list(900, 128, 1, bh.ca3space.generator("e8 list", "background", 128, 1, 3, 2))
    assert torch.equal(lst["test"], ref["test"]) and torch.equal(lst["study"], ref["study"])


# ------------------------------------------------------------ the table script

def load_table_script():
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "scripts" / "make_e8c_table.py"
    spec = importlib.util.spec_from_file_location("make_e8c_table", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def synthetic_record(seeds=(0, 1), n=40, seed=0):
    """Every arm and readout: repeats high, foils low, closer lures graded
    by level, other-drawer lures in between; no signal where the readout
    reads CA3's recurrent synapses and the arm has none."""
    g = torch.Generator().manual_seed(seed)
    per_seed = {}
    for s in seeds:
        types = [0] * n + [1] * n + [2] * n + [3] * (5 * n)
        level = [0] * (3 * n) + [lv for lv in range(1, 6) for _ in range(n)]
        base = torch.cat([0.8 + 0.1 * torch.rand(n, generator=g),
                          0.3 + 0.3 * torch.rand(n, generator=g),
                          0.1 * torch.rand(n, generator=g),
                          torch.cat([0.7 - 0.12 * lv + 0.1 * torch.rand(n, generator=g)
                                     for lv in range(5)])])
        sig = {}
        for r in ("r1", "r2", "r3", "r3s"):
            sig[r] = {}
            for arm in rc.ARMS:
                if r != "r1" and arm in ("no_recurrent", "no_ca3"):
                    sig[r][arm] = [0.0] * len(types)
                else:
                    shrink = 0.8 if arm.startswith("pp_keep") else 1.0
                    sig[r][arm] = (base * shrink).tolist()
        per_seed[str(s)] = {"types": types, "level": level,
                            "similarity": [1.0] * n + [0.7] * n + [None] * n + [0.9] * (5 * n),
                            "signal": sig, "ca3": {}}
    return {"args": {"arms": list(rc.ARMS)}, "per_seed": per_seed, "seeds_done": list(seeds),
            "complete": True}


def test_table_script_calibrates_scores_and_tables_every_readout():
    tb = load_table_script()
    rec = synthetic_record()
    cal = tb.calibrate(rec, synthetic_record(), [0.46, 0.54, 0.6, 0.66])
    assert cal["reproduces_e8b"] == {"r1": 0.0, "r2": 0.0}
    assert set(cal["thresholds"]["r3"]) == set(rc.ARMS) - {"no_recurrent", "no_ca3"}
    assert set(cal["older"]["r3"]) == set(tb.OLDER_ARMS)
    assert cal["thresholds"]["r3"]["intact"]["feasible"]
    fixed, own, older = tb.score_all(rec, cal)
    s = fixed[("r3", "close")]["intact"]
    # The young-adult criteria give 81.2% old to repeats and 82% new to foils.
    assert s["rates repeat old"]["mean"] == pytest.approx(0.812, abs=1e-3)
    assert s["rates foil new"]["mean"] == pytest.approx(0.820, abs=1e-3)
    o = older[("r3", "close")]["intact"]
    assert o["rates foil new"]["mean"] == pytest.approx(0.734, abs=1e-3)
    assert fixed[("r3", "close")]["no_recurrent"]["rates lure new"]["mean"] == 1.0
    preds = tb.predictions(cal, fixed, older, {("r1", "drawer", "rec"): 0.0})
    keys = [k for k, _, _ in preds]
    assert keys[0] == "1" and "3" in keys and "5b" in keys and keys[-1] == "7"
    text = tb.tables(cal, fixed, own, older, preds)
    assert text.startswith("## Tables") and "Older adults' criteria" in text


def test_reproduction_check_finds_a_changed_signal():
    tb = load_table_script()
    a, b = synthetic_record(), synthetic_record()
    b["per_seed"]["1"]["signal"]["r2"]["intact"][3] += 0.25
    assert tb.reproduction_check(a, b)["r2"] == pytest.approx(0.25)
