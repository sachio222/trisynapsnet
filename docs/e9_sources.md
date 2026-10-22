# E9 sources

E9 lets DG drive CA3 at recall as well as at storage, keeps entorhinal input on during attractor dynamics, and sets both inputs' strengths from measured synaptic values. This file records what the literature says about DG activity at test, the timing and duration of the two inputs, and the synaptic strengths, with the arguments against DG input at retrieval. Every quote is exact and was checked against the saved text. Titles, authors, journals, volumes and pages were checked on Crossref. Where a text carries no page numbers, quotes are located by section.

"Found" names the search that located the source and "Read" the retrieval that returned the text, both through the treg service. Most sources were read in full for the research proposal behind E9 (`reports/2026-10-21-recognition-errors-proposal/`) with treg's `exa.web.contents.get`; the searches that first located them were not recorded, and this file says so for each. Two sources are new for E9: Suzuki, Miller and Desimone (1997), found with `tinyfish.web.search.publications`, and Mormann and colleagues (2008), found with `exa.web.search.publications`, both read with `exa.web.contents.get`. Sources E9 uses that earlier sources files already record: Stark and colleagues 2013 and Baker and colleagues 2016 (`docs/e8_sources.md`); Bakker and colleagues 2008 and Norman and O'Reilly 2003 (`docs/e8c_sources.md`); Watson and colleagues 2025 and Ramirez-Amaya and colleagues 2013 (`docs/e8b_protocol.md`).

## DG at test

### Neunuebel and Knierim 2014

*CA3 retrieves coherent representations from degraded input: direct evidence for CA3 pattern completion and dentate gyrus pattern separation.* Neuron 81:416-427. doi 10.1016/j.neuron.2013.11.017. Found: not recorded (proposal research). Read: `exa.web.contents.get`, PMC author manuscript without pages.

- Summary: "We simultaneously recorded activity from CA3 and DG of behaving rats when local and global reference frames were placed in conflict. CA3 showed a coherent population response to the conflict (pattern completion), even though its DG inputs were severely disrupted (pattern separation)."

**E9 uses**: DG is active and separating at test while CA3 completes, the observation a silent DG at recall contradicts.

### Berron and colleagues 2016

*Strong evidence for pattern separation in human dentate gyrus.* Journal of Neuroscience 36:7569-7579. doi 10.1523/JNEUROSCI.0518-16.2016. Found: not recorded (proposal research). Read: `exa.web.contents.get`, journal full text without pages.

- Abstract: with 7-tesla fMRI and multivariate pattern analysis, "the DG subregion specifically sustains representations of similar scenes that are less overlapping than in other hippocampal (e.g., CA3) and medial temporal lobe regions (e.g., entorhinal cortex)".

**E9 uses**: human DG holds separated representations of similar items, the human counterpart of DG separating at test.

### Denny and colleagues 2014

*Hippocampal memory traces are differentially modulated by experience, time, and adult neurogenesis.* Neuron 83:189-201. doi 10.1016/j.neuron.2014.05.018. Found: not recorded (proposal research). Read: `exa.web.contents.get`, PMC author manuscript.

- Results, Figure 5F: "optogenetic inhibition of DG neurons impaired expression of the fear memory as evidenced by the lower percent of freezing in context A in ArcCreERT2(+) mice when compared with ArcCreERT2(−) mice (Figure 5F) (p = 0.02)"; "when optogenetic inhibition ceased, freezing levels were comparable in both groups (Figure 5F)".

**E9 uses**: silencing at test the DG cells active during learning impairs recall in mice.

### Bernier and colleagues 2017

*Dentate gyrus contributes to retrieval as well as encoding: evidence from context fear conditioning, recall, and extinction.* Journal of Neuroscience 37:6359-6371. doi 10.1523/JNEUROSCI.3029-16.2017. Found: not recorded (proposal research). Read: `exa.web.contents.get`, full text without pages.

- Abstract: "(2) inhibition during recall did not impair fear expression in the training context, unless mice had to distinguish between similar feared and neutral contexts".

**E9 uses**: DG output at recall matters when similar contexts must be told apart, the situation lures create.

### Nakashiba and colleagues 2012

*Young dentate granule cells mediate pattern separation, whereas old granule cells facilitate pattern completion.* Cell 149:188-201. doi 10.1016/j.cell.2012.01.046. Found: not recorded (proposal research). Read: `exa.web.contents.get`, PMC author manuscript.

- Summary: "We created a transgenic mouse in which output of old GCs was specifically inhibited while leaving a substantial portion of young GCs intact"; "Furthermore, mutant mice exhibited deficits in rapid pattern completion."

**E9 uses**: granule-cell output contributes to recall by pattern completion.

### Kheirbek and colleagues 2013 (against)

*Differential control of learning and anxiety along the dorsoventral axis of the dentate gyrus.* Neuron 77:955-968. doi 10.1016/j.neuron.2012.12.038. Found: not recorded (proposal research). Read: `exa.web.contents.get`, PMC author manuscript.

- Abstract: "we demonstrate that GCs in the dorsal DG control exploratory drive and encoding, not retrieval, of contextual fear memories."

**E9 uses**: evidence against a role for DG at retrieval, reported beside the evidence for it.

### Treves and Rolls 1992 (against)

*Computational constraints suggest the need for two distinct input systems to the hippocampal CA3 network.* Hippocampus 2:189-199. doi 10.1002/hipo.450020209. Found: not recorded (proposal research; also cited in `docs/e3_protocol.md`). Read: `exa.web.contents.get`, scanned full text with journal pages.

- p. 196: "One implication is that during retrieval, or at least while initiating retrieval, the mossy fiber input should be absent or strongly reduced with respect to its amplitude during learning, in order not to blur the signal relayed by the perforant" path (the sentence continues across a column break).

**E9 uses**: the model's current scheme, DG silent at recall, and the classic argument against what E9 tests.

### O'Reilly and McClelland 1994 (against)

*Hippocampal conjunctive encoding, storage, and recall: avoiding a trade-off.* Hippocampus 4:661-682. doi 10.1002/hipo.450040605. Found: not recorded (proposal research). Read: `exa.web.contents.get`, scanned full text with journal pages.

- p. 678: "If the mossy fiber inputs constitute too much of the total input to the active CA3 neurons, then the learning in the perforant path inputs will not be capable of making up the difference during recall, and pattern completion will suffer." (Two-column text interleaved in the scan; the sentence is reassembled from its column.)

**E9 uses**: the prediction that strong mossy input at recall harms completion, which E9 checks on repeats.

## Timing and duration of the two inputs

### Yeckel and Berger 1990

*Feedforward excitation of the hippocampus by afferents from the entorhinal cortex: redefinition of the role of the trisynaptic pathway.* PNAS 87:5832-5836. doi 10.1073/pnas.87.15.5832. Found: not recorded (proposal research). Read: abstract only, `exa.web.contents.get`.

- Abstract: "the initial monosynaptic excitation of pyramidal cells then is followed by weaker excitatory volleys transmitted through the trisynaptic pathway. In addition, we found that responses of CA3 pyramidal cells often precede those of dentate granule cells and that excitation of CA3 and CA1 pyramidal cells can occur in the absence of granule cell excitation."

**E9 uses**: the perforant path sets CA3's starting state and DG's input arrives after it. The same sentence calls the trisynaptic volleys weaker, after electrical stimulation of entorhinal axons; that bears on the mossy strength and is listed under the limits below.

### Suzuki, Miller and Desimone 1997

*Object and place memory in the macaque entorhinal cortex.* Journal of Neurophysiology 78:1062-1081. doi 10.1152/jn.1997.78.2.1062. Found: `tinyfish.web.search.publications`. Read: `exa.web.contents.get`, journal full text without pages.

- Methods (Fig. 1 legend): "Each stimulus in the sequence was presented for 500 ms".
- Results: "There was substantial variability in both the latencies (mean onset latency 181 ms; range 100–300 ms) and duration (mean duration 293 ms; range 100–420 ms)", for 36 entorhinal neurons with excitatory visual responses.
- Abstract: "some entorhinal cells had sample-specific delay activity that was maintained throughout all of the delay intervals in the sequence."

**E9 uses**: entorhinal responses to a picture last hundreds of milliseconds, the basis for keeping EC input on during attractor dynamics.

### Mormann and colleagues 2008

*Latency and selectivity of single neurons indicate hierarchical processing in the human medial temporal lobe.* Journal of Neuroscience 28:8865-8872. doi 10.1523/JNEUROSCI.1640-08.2008. Found: `exa.web.search.publications`. Read: `exa.web.contents.get`, journal full text without pages.

- Results: pictures "were displayed for 1 s each"; "Average response latencies in the parahippocampal cortex (271 ms) were significantly earlier than those in the entorhinal cortex (392 ms), hippocampus (394 ms), and amygdala (397 ms)".

**E9 uses**: human entorhinal neurons respond to pictures while they are shown, with latencies of hundreds of milliseconds. The paper does not report response durations.

## Synaptic strengths

### Guzman, Schlögl, Frotscher and Jonas 2016

*Synaptic mechanisms of pattern completion in the hippocampal CA3 network.* Science 353:1117-1123. doi 10.1126/science.aaf1836. Found: not recorded (proposal research). Read: `exa.web.contents.get`, journal PDF text (three-column layout, interleaved).

- Results: unitary CA3-CA3 EPSPs "had a mean latency of 2.3 ± 0.1 ms, a peak amplitude of 0.56 ± 0.01 mV, and a decay time constant of 80.1 ± 6.2 ms".
- Results: unitary conductance with "a peak conductance of 0.54 ± 0.12 nS".
- Results: "we estimated that 7.3 ± 1.9 coactive convergent inputs were required to initiate action potentials"; in vivo, "we estimated that 3.3 inputs would be required".

**E9 uses**: the unit of input (one recurrent synapse), in both the EPSP and the conductance ratios.

### Vyleta, Borges-Merjane and Jonas 2016

*Plasticity-dependent, full detonation at hippocampal mossy fiber–CA3 pyramidal neuron synapses.* eLife 5:e17977. doi 10.7554/eLife.17977. Found: not recorded (proposal research). Read: `exa.web.contents.get`, PMC full text without pages.

- Results: "Single unitary EPSPs had a mean latency of 1.06 ± 0.09 ms, a peak amplitude of 9.6 ± 2.4 mV, a 20–80% rise time of 3.6 ± 0.7 ms, and a decay time constant of 134 ± 10 ms (6–8 pairs; Figure 1E–I). Furthermore, single unitary EPSPs triggered action potentials with a mean probability of only 0.12 ± 0.08."
- Abstract: "Remarkably, PTP switched mossy fiber synapses into full detonators for tens of seconds."

**E9 uses**: the main mossy strength, 9.6 / 0.56 = 17.1 units.

### Jonas, Major and Sakmann 1993

*Quantal components of unitary EPSCs at the mossy fibre synapse on CA3 pyramidal cells of rat hippocampus.* Journal of Physiology 472:615-663. doi 10.1113/jphysiol.1993.sp019965. Found: not recorded (proposal research). Read: abstract only, `exa.web.contents.get`.

- Abstract: "The apparent EPSC peak conductance in normal extracellular solution (2 mM Ca2+, 1 mM Mg2+), excluding failures, was 1 nS."
- Abstract: EPSCs "were recorded in CA3 pyramidal cells of hippocampal slices of 15- to 24-day-old rats (22 degrees C)".

**E9 uses**: the lower-bound mossy strength, 1 / 0.54 = 1.9 units, from peak conductances. The conductance is from juvenile rats at room temperature.

### Baker, Perez-Rosello, Migliore, Barrionuevo and Ascoli 2011

*A computer model of unitary responses from associational/commissural and perforant path synapses in hippocampal CA3 pyramidal cells.* Journal of Computational Neuroscience 31:137-158. doi 10.1007/s10827-010-0304-x (issued online 2010). Found: not recorded (proposal research). Read: `exa.web.contents.get`, PMC full text without pages.

- Table 4, "Predicted mean response properties in passive current clamp", AMPA receptor mediated responses: associational/commissural, mean peak 0.56 ± 0.05 mV (17 cells, 8,334 synapses); perforant path, 0.34 ± 0.03 mV (17 cells, 3,984 synapses).

**E9 uses**: the perforant strength, 0.34 / 0.56 = 0.61 units. The perforant value is a model prediction, not a recording; the same model gives 0.56 mV for a recurrent synapse, so the ratio holds inside the model as well as against Guzman and colleagues' measurement.

### Henze, Wittner and Buzsáki 2002

*Single granule cells reliably discharge targets in the hippocampal CA3 network in vivo.* Nature Neuroscience 5:790-795. doi 10.1038/nn887. Found: not recorded (proposal research). Read: abstract only, `exa.web.contents.get`.

- Abstract: "Single spikes in dentate granule cells, controlled intracellularly, generally failed to discharge either interneurons or CA3 pyramidal cells. In contrast, trains of spikes effectively discharged both CA3 cell types."

**E9 uses**: a limit on the main mossy strength; the model has no spike timing, so the effective mossy input at recall lies somewhere between the conductance ratio and the potentiated synapse.

## Limits the sources set

- **Mossy strength at recall is uncertain.** Single mossy EPSPs rarely fire a CA3 cell (Vyleta and colleagues 2016; Henze, Wittner and Buzsáki 2002), and trisynaptic volleys after entorhinal stimulation were weaker than the monosynaptic one (Yeckel and Berger 1990); trains and post-tetanic potentiation make the same synapses detonators. E9 runs 17.1 and 1.9 units for this reason.
- **The perforant strength is a model prediction** (Baker and colleagues 2011).
- **EC duration is from macaque recordings with 500 ms pictures** (Suzuki, Miller and Desimone 1997). The model's rounds have no time scale, so whether EC input lasts through every round of attractor dynamics is an assumption the recordings make plausible, not a measurement.
- **DG's record of recently active cells** at test has no measured counterpart; it is AHA's stand-in, frozen at the end of study as the proposal sets it.
- **Species.** Every strength is from rat; human mossy-fibre and perforant-path unitary strengths were not found in the sources read.
