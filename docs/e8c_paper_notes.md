# Framing notes for the paper that follows E8c

Working notes, not a draft. They fix the purpose, one sentence the paper keeps verbatim, and the argument that sentence introduces, and they mark which claims still need a source read in full before they go in.

## Working purpose

Which hippocampal mechanisms make human recognition memory err in the specific ways people err?

In field terms: people show **false recognition** of items similar to ones they studied, and their **mnemonic discrimination** (telling a studied item from a similar new one, measured in the Mnemonic Similarity Task by the lure discrimination index) falls as lures grow more similar, with age, and with hippocampal dysfunction. The standard account traces these errors to the balance between **pattern separation** in the dentate gyrus, which stores similar experiences as distinct patterns, and **pattern completion** in CA3, which rebuilds a stored pattern from part of it through attractor dynamics. The paper asks which of these mechanisms, built from measured parts, produce people's errors and which do not.

## The sentence, verbatim

"Any system can be accurate, but only the right mechanism makes the right mistakes."

## The argument it introduces, in the paper's voice

Accuracy cannot pick the mechanism. On lures made by distorting the studied drawing, the vision network alone, with no hippocampus, tells look-alikes apart about twice as well as people do: its lure discrimination index is 0.77, against 0.36 for young adults. A model can therefore match or beat people's accuracy for reasons that have nothing to do with how the brain does it.

People's mistakes have a shape. The more similar a lure is to a studied item, the more often people call it old. Older adults call more lures old than young adults do, 54.6% against 40.3%, while their hit rates barely change (82.2% against 81.2%), and people with mild cognitive impairment call more still, 64.9%. These errors are thought to come from the balance of pattern separation in the dentate gyrus and pattern completion in CA3: input loss to the dentate gyrus and CA3 with age is thought to tip that balance toward completion, so a similar new item brings back the old memory.

A model that produces that shape from measured parts could predict how memory fails, for whom and under what damage. The errors have to come out of the circuit, never from added noise and never from decision thresholds tuned to hit them. In this work the only values set to human data are the young adults' hit and correct-rejection rates, which fix the two response criteria; every error rate is a prediction.

## Claims and their sources

| Claim | Status | Source, or what is missing |
|---|---|---|
| The vision network alone has LDI 0.77 against people's 0.36 | Measured, with a scope limit | `results/e8b.md`: vision-code baseline LDI 0.768 on closer lures (distorted studied drawings). On other-drawer lures its LDI is 0.235, below people's, and in E8 it was 0.422. The paper must say "on lures made by distorting the studied drawing" or give both lure sets. People's 0.360: Stark and colleagues 2013, Table 2 (read). |
| More similar lures are called old more often | Read | Stark, Kirwan and Stark 2019 (lure bin 1 "elicit false alarms quite often", bin 5 "very few"); Stark and colleagues 2013, Results. Per-bin human rates appear only in figures, so the paper gives the direction, not numbers. |
| Older adults call more lures old, 54.6% against 40.3% | Read | Stark and colleagues 2013, Table 2 (ages 60 to 74 against 20 to 39). Hits 82.2% against 81.2%; correct rejections of foils fall more, 73.4% against 82.0%, so the paper says only that hit rates barely change. |
| The age gap is smallest for the most similar lures | Read | Yassa, Lacy and colleagues 2011, Hippocampus, Discussion. |
| Errors rise further with hippocampal damage | **Not supported as worded** | The one lesion study read found no rise: patients with hippocampal damage called lures old as often as controls (0.38 against 0.37) and called more lures new (Kirwan and colleagues 2012). A patient with a lesion mostly of the dentate gyrus had an LDI close to zero with normal recognition of repeats and foils (Baker and colleagues 2016, read for E8, `docs/e8_sources.md`). Higher p(old \| lure) is read only for mild cognitive impairment (64.9%, Stark and colleagues 2013; Bakker and colleagues 2012), which is not a lesion. Suggested wording: "and people with mild cognitive impairment call more still"; for lesions, "hippocampal damage lowers lure discrimination". |
| The errors come from the balance of pattern separation in DG and pattern completion in CA3 | Read, as an account | Yassa and Stark 2011; Wilson and colleagues 2006; Yassa, Mattfeld and colleagues 2011; Stark and colleagues 2019. The paper should present it as the field's account, not as established mechanism. |
| Input loss with age tips the balance toward completion | Read, as an account, with cautions | Wilson and colleagues 2006 (rat synapse counts, recurrent synapses spared); Yassa, Muftuler and Stark 2010 (human perforant-path imaging, no percentage loss); Smith and colleagues 2000 (loss tracks impairment, not age alone). Needs a read human source for the size of loss before the paper gives one; none was found. |
| Only the hit and correct-rejection rates are set to human data | True of E8 to E8c | `docs/e8b_protocol.md`, `docs/e8c_protocol.md`. If the paper uses older adults' criteria (E8c item 21), it must name those two rates as well. |

## Terms to keep straight

- People remember, learn and recall; circuits and synapses store.
- "Attractor dynamics" is the process, "pattern completion" its outcome.
- "Familiarity" in the paper means the dual-process sense (Yonelinas 2002) or the network-energy signal; say which, and say that the literature places the energy readout in perirhinal cortex (`docs/e8c_sources.md`).
