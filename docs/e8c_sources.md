# E8c sources

E8c reads a familiarity signal from CA3's starting state, before attractor dynamics. This file records what the literature says about novelty and familiarity signals computed from incoming input before, or apart from, recall; where those signals are placed; what a downstream population could receive; and the evidence that ties ageing to the perforant path. Every quote is exact and was checked against the saved full text. Titles, authors, journals, volumes and pages were checked on Crossref. Where a text carries no page numbers, quotes are located by section. "Found" names the search that located the source and "Read" the retrieval that returned the text, both through the treg service (endpoints `tinyfish.web.search.publications`, `exa.web.search.publications`, `exa.web.contents.get`, `treg.web.extract`, `linkup.web.fetch`). Texts marked "earlier retrieval" were read in full for E8 or E8b and located again with a treg search for E8c. The human rates and lesion findings E8c compares against are in `docs/e8_sources.md`.

## Familiarity from a recurrent network's energy, before retrieval

### Bogacz, Brown and Giraud-Carrier 2001

*Model of familiarity discrimination in the perirhinal cortex.* Journal of Computational Neuroscience 10:5-23. doi 10.1023/A:1008925909305. Found: `tinyfish.web.search.publications` (author PDF). Read: `exa.web.contents.get`, full text with journal pages.

- The energy as a familiarity signal (Appendix A, p. 15): "The value of the energy function is usually lower for stored patterns and higher for other patterns (Amit, 1989). Therefore, the value of the energy may be used for familiarity discrimination."
- No retrieval step (p. 16): "the neurons do not perform any computations (there is no relaxation), but the familiarity discrimination is done by checking the value of the energy function after delivering a pattern".
- Capacity (p. 11): "This method allows a neural network having N neurons to discriminate familiarity with 99% reliability for 0.023N 2 patterns (see Appendix A). This capacity is much greater than the standard capacity of the Hopfield network for retrieval".
- Speed (p. 13): information "needs to be processed by only two layers of neurons and so may take less than" about 10 ms, whereas associative memories that recall "require a longer relaxation process".
- How neurons could compute it (Appendix B, p. 19): "The inner part of Eq. (18), as it calculates the sum of the weights of its active synapses relative to 1/2, may be performed by a neuron."
- Location (Abstract, p. 5): "familiarity discrimination being dependent on the perirhinal cortex".

**E8c uses**: the energy of the presented pattern, read with no relaxation, as the familiarity computation (R3), and the placement of that computation in perirhinal cortex.

### Bogacz and Brown 2003

*Comparison of computational models of familiarity discrimination in the perirhinal cortex.* Hippocampus 13:494-524. doi 10.1002/hipo.10093. Found: `exa.web.search.publications`; author PDF located with `tinyfish.web.search.publications`. Read: `exa.web.contents.get`, full text (only even-page headers survive).

- Section "Capacity for Uncorrelated Input Patterns": "familiarity discrimina tion is N times easier than recall" (line break in the original).
- pp. 494-495: "If the perirhinal cortex worked similarly to the specialised models, it alone could discriminate the familiarity of many more stimuli than current neural network models indicate could be recalled".

**E8c uses**: the placement in perirhinal cortex.

### Greve, Sterratt, Donaldson, Willshaw and van Rossum 2009

*Optimal learning rules for familiarity detection.* Biological Cybernetics 100:11-19. doi 10.1007/s00422-008-0275-4. Found: `exa.web.search.publications`; PDF located with `tinyfish.web.search.publications`. Read: `exa.web.contents.get`, author manuscript without journal pages.

- Section 1.1: familiarity is measured "by the so-called energy that a certain pattern µ yields"; "unlike the Hopfield network, there is no dynamics in the network"; "Relaxing the network into an attractor state would seriously reduce the capacity of the network".

**E8c uses**: the energy read without dynamics.

### Cortes, Greve, Barrett and van Rossum 2010

*Dynamics and robustness of familiarity memory.* Neural Computation 22:448-466. doi 10.1162/neco.2009.12-08-921. Found: `tinyfish.web.search.publications`. Read: `exa.web.contents.get`, arXiv 0710.1333, full text without pages (summation signs lost in extraction).

- Section "Network Setup": the energy is written as a sum over cells of each cell's input times its state, and "One could construct an additional set of neurons that each calculate the product of h i and s i , and their activities are then summed in an output neuron to yield the energy."
- Section "Two Familiarity Discriminators": the energy at the moment the probe is loaded "can be used to discriminate between old and new stimuli"; eq. 3.2 writes it as a sum of squared overlaps with the stored patterns.
- Section "Dynamics of the Familiarity Discriminators": "after a short transient of some five time units, the two signals become similar, that is, familiarity discrimination based on energy deteriorates rapidly after stimulus presentation"; "The underlying reason is that the activity in the Hopfield network will always reach an attractor state regardless of the initial activity pattern."
- Section "Robustness of the Familiarity Discriminators to Noise": the energy at the start "will be calculated before any activity updates have occurred".
- Section "Discussion": "recollection information becomes available only when activity has settled".
- Section "Introduction": "Single-item familiarity is believed to be processed in the perirhinal cortex".

**E8c uses**: the first-pass reading, the reason the signal is lost once attractor dynamics run, the downstream population that sums each active cell's input, and the dependence on squared overlap behind prediction 2a.

### Hopfield 1982

*Neural networks and physical systems with emergent collective computational abilities.* PNAS 79:2554-2558. doi 10.1073/pnas.79.8.2554. Found: `tinyfish.web.search.publications`. Read: earlier retrieval, full text.

- p. 2558: "Familiar and unfamiliar states were distinguishable most of the time at this level of overload on the basis of the initial processing rate, which was faster for unfamiliar states. This kind of familiarity can only be read out of the system by a class of neurons or devices abstracting average properties of the processing group."

**E8c uses**: an early statement that a recurrent network's starting state carries familiarity readable by a pooling population.

## Where familiarity and novelty are placed

### Brown and Aggleton 2001

*Recognition memory: what are the roles of the perirhinal cortex and hippocampus?* Nature Reviews Neuroscience 2:51-61. doi 10.1038/35049064. Found: `tinyfish.web.search.publications`. Read: `exa.web.contents.get`, full text with its two columns interleaved in extraction; quotes rebuilt by joining fragments.

- p. 52: response reductions to repeated stimuli occur in about 25% of recorded neurons in anterior inferior temporal cortex, "notably in the perirhinal cortex, but are much less frequent" (under about 1%) in the hippocampus, and hippocampal response changes "have much longer latencies than those of perirhinal neurons".
- p. 59: a system centred on perirhinal cortex discriminates "the familiarity and recency of occurrence of individual stimulus items", one centred on the hippocampus judges "the prior occurrence of constellations of stimuli".

**E8c uses**: the evidence that places item familiarity outside the hippocampus.

### Yonelinas 2002 (abstract only)

*The nature of recollection and familiarity: a review of 30 years of research.* Journal of Memory and Language 46:441-517. doi 10.1006/jmla.2002.2864. Found: `exa.web.search.publications`. Read: abstract only, `treg.web.extract` on the publisher page; the body is paywalled and the author copy was unreachable.

- Abstract: results "provide support for models that assume that recollection relies on the hippocampus and prefrontal cortex, whereas familiarity relies on regions surrounding the hippocampus."

**E8c uses**: the definition of the dual-process split, from the abstract only.

### Norman and O'Reilly 2003

*Modeling hippocampal and neocortical contributions to recognition memory: a complementary-learning-systems approach.* Psychological Review 110:611-646. doi 10.1037/0033-295X.110.4.611. Found: `tinyfish.web.search.publications`. Read: earlier retrieval, full text.

- p. 614: "The hippocampal model is applied to recognition by computing the degree of match between retrieved information and the recall cue, minus the amount of mismatch."
- p. 622 (read in the two-column text): the hippocampal recall signal triggered by lures stays at floor until target-lure similarity is above 60%, because of pattern separation, while cortical lure familiarity "smoothly tracks target–lure similarity".

**E8c uses**: a hippocampal recognition signal computed after recall, and the prediction that pattern separation keeps lures near floor.

### Norman 2010

*How hippocampus and cortex contribute to recognition memory: revisiting the complementary learning systems model.* Hippocampus 20:1217-1227. doi 10.1002/hipo.20855. Found: `tinyfish.web.search.publications`. Read: `exa.web.contents.get`, PMC3416886, full text without pages.

- Section "Recollection vs. familiarity": "the average level of activity in region CA1 of the hippocampal model discriminates between old and new items".

**E8c uses**: summed CA1 activity as a hippocampal alternative, listed under "Not in E8c".

### Hasselmo and Schnell 1994

*Laminar selectivity of the cholinergic suppression of synaptic transmission in rat hippocampal region CA1: computational modeling and brain slice physiology.* Journal of Neuroscience 14:3898-3914. doi 10.1523/JNEUROSCI.14-06-03898.1994. Found: `tinyfish.web.search.publications`. Read: `exa.web.contents.get`, full text with journal pages.

- p. 3899: CA1 could "perform a comparison of the output of region CA3 with the current afferent input from the entorhinal cortex".
- Figure 2 legend: "The summed output of region CA 1 [...] decreases the level of cholinergic mod ulation from the medial septum."
- p. 3911: "For novel stimuli, the level of ACh increases, and network activity depends more on external input than recall activity, setting appropriate dynamics for learning."

**E8c uses**: the CA1 comparator, the septal target of the novelty signal, and acetylcholine rising for novel input.

### Hasselmo, Wyble and Wallenstein 1996

*Encoding and retrieval of episodic memories: role of cholinergic and GABAergic modulation in the hippocampus.* Hippocampus 6:693-708. doi 10.1002/(SICI)1098-1063(1996)6:6<693::AID-HIPO12>3.0.CO;2-W. Found: `exa.web.search.publications` (author PDF). Read: `exa.web.contents.get`, full text without page markers.

- Section "Feedback regulation of cholinergic modulation": "the total activity in region CA1 regulated the levels of cholinergic modulation in the network".
- Same section: "Presentation of familiar input patterns caused higher levels of activity in region CA3 due to a match with previously strengthened connections".
- Section "Region CA3 Associates Context and Item": "during retrieval the recurrent excitation should dominate over the afferent input."
- Figure 1 legend: CA1 can influence the medial septum, "allowing a mismatch between recall and input to increase ACh".

**E8c uses**: familiar input driving CA3 harder through strengthened synapses, and the CA1-to-septum route.

### Hasselmo, Bodelón and Wyble 2002

*A proposed function for hippocampal theta rhythm: separate phases of encoding and retrieval enhance reversal of prior learning.* Neural Computation 14:793-817. doi 10.1162/089976602317318965. Found: `exa.web.search.publications` (author PDF). Read: `exa.web.contents.get`, full text.

- Abstract, p. 793: encoding occurs "in the phase when synaptic input from entorhinal cortex is strong" and "synaptic currents arising from region CA3 input are weak"; "Retrieval of old associations occurs in the phase when entorhinal input is weak and synaptic input from region CA3 is strong".

**E8c uses**: the starting state as CA3 under EC drive, before recurrent input dominates.

### Hasselmo 2006

*The role of acetylcholine in learning and memory.* Current Opinion in Neurobiology 16:710-715. doi 10.1016/j.conb.2006.09.002. Found: `exa.web.search.publications`. Read: `exa.web.contents.get`, PMC2659740, full text without pages.

- Section "Muscarinic presynaptic inhibition": "In region CA3 of hippocampus, muscarinic receptors suppress excitatory transmission at recurrent connections in stratum radiatum".

### Kremin and Hasselmo 2007

*Cholinergic suppression of glutamatergic synaptic transmission in hippocampal region CA3 exhibits laminar selectivity: implication for hippocampal network dynamics.* Neuroscience 149:760-767. doi 10.1016/j.neuroscience.2007.07.007. Found: `tinyfish.web.search.publications`. Read: `exa.web.contents.get`, PMC2175389, full text without pages.

- Abstract: selective suppression of recurrent excitation allows "incoming information from the perforant path to have a predominant influence on neural activity."
- Results: at 20 µM carbachol, suppression of 52.1% in stratum lacunosum-moleculare against 84.2% in stratum radiatum.

**E8c uses**: acetylcholine favouring the perforant drive that sets the starting state over recurrent drive.

### Lisman and Grace 2005

*The hippocampal-VTA loop: controlling the entry of information into long-term memory.* Neuron 46:703-713. doi 10.1016/j.neuron.2005.05.002. Found: `tinyfish.web.search.publications`. Read: `exa.web.contents.get`, full text (HTML, by section).

- Section "The Role of the Hippocampus in Producing Novelty-Dependent Firing of VTA Cells": "The locus of novelty detection in the hippocampus is not known with certainty"; "The regions that precede CA1 (dentate and CA3) appear to have other functions"; novelty is computed in CA1, which "acts as a 'comparator' that computes novelty"; a form of novelty "can be detected in less than 100 ms".
- Abstract: "The resulting novelty signal is conveyed through the subiculum, accumbens, and ventral pallidum to the VTA".

**E8c uses**: the CA1 comparator and the downstream route of the hippocampal novelty signal.

### Lisman and Otmakhova 2001 (abstract only)

*Storage, recall, and novelty detection of sequences by the hippocampus: elaborating on the SOCRATIC model.* Hippocampus 11:551-568. doi 10.1002/hipo.1071. Found: `tinyfish.web.search.publications`. Read: abstract only, `treg.web.extract`; body paywalled.

- Abstract: "One possible site for computing mismatch is CA1, since it receives predictions from CA3 and sensory 'reality' via the perforant path."

### Kumaran and Maguire 2007

*Match-mismatch processes underlie human hippocampal responses to associative novelty.* Journal of Neuroscience 27:8517-8524. doi 10.1523/JNEUROSCI.1677-07.2007. Found: `tinyfish.web.search.publications`. Read: `exa.web.contents.get`, full text with journal pages.

- p. 8520: "our findings argue strongly against the operation of a familiarity mechanism within the hippocampus" during the processing of associative novelty.
- p. 8521: "the generation of mismatch signals can be seen to be contingent on the process of hippocampal recall".

**E8c uses**: evidence against a familiarity mechanism inside the hippocampus.

### Duncan, Ketz, Inati and Davachi 2012

*Evidence for area CA1 as a match/mismatch detector: a high-resolution fMRI study of the human hippocampus.* Hippocampus 22:389-398. doi 10.1002/hipo.20933. Found: `tinyfish.web.search.publications`. Read: `treg.web.extract`, PMC3529001, full text without pages.

- Results: "the only hippocampal subregion to display a general match/mismatch signal was area CA1".
- Introduction, mixed evidence: "selective lesion of areas CA3 and DG significantly impared rats' ability to detect displaced objects" (spelling as in the original).

### Bakker, Kirwan, Miller and Stark 2008

*Pattern separation in the human hippocampal CA3 and dentate gyrus.* Science 319:1640-1642. doi 10.1126/science.1152882. Found: `exa.web.search.publications`. Read: `treg.web.extract`, PMC2829853 author manuscript, without pages.

- Results: "the bias score of 0.15 in the CA3/DG showed that lure stimuli were treated almost exactly the same as the presentation of a novel stimulus", against 0.59 to 0.83 in CA1, subiculum and the entorhinal and parahippocampal cortices.
- Discussion: the results "are more indicative of pattern separation and completion and that they are not synonymous with various novelty codes."

**E8c uses**: the expectation that a signal read in CA3, after DG, treats most lures like new items (predictions 2b, 3 and 3b).

## Ageing, the perforant path and hippocampal damage

### Wilson, Gallagher, Eichenbaum and Tanila 2006

*Neurocognitive aging: prior memories hinder new hippocampal encoding.* Trends in Neurosciences 29:662-670. doi 10.1016/j.tins.2006.10.002. Found: `tinyfish.web.search.publications`. Read: `linkup.web.fetch`, PMC2614702 author manuscript, by section.

- Abstract: "The key point of the model is that small concurrent changes during aging strengthen the auto-associative network of the CA3 subregion at the cost of processing new information coming in from the entorhinal cortex."
- Section "Reduced connections from the EC to the hippocampus": "In aged rats, the DG receives approximately one-third fewer synaptic contacts from the EC than in young rats"; "synapses onto CA3 cells from their own recurrent collaterals are not reduced in number during aging".
- Figure 3 legend: "Thus, the CA3 of aged individuals performs excessive pattern completion."

**E8c uses**: the basis for thinning the perforant path as a stand-in for entorhinal input loss with age. The "one-third" figure is the review's summary of rat studies (its references 34 and 35); E8c takes no size of loss from it.

### Yassa, Muftuler and Stark 2010

*Ultrahigh-resolution microstructural diffusion tensor imaging reveals perforant path degradation in aged humans in vivo.* PNAS 107:12687-12691. doi 10.1073/pnas.1002113107. Found: `tinyfish.web.search.publications`. Read: earlier retrieval, full text.

- Abstract: "We find no evidence of such loss in a control pathway, the alveus".
- Results: a group difference in the perforant-path diffusion measure "(t = 2.53, P = 0.01; Fig. 3A)". The paper gives no percentage loss.

### Yassa, Mattfeld, Stark and Stark 2011

*Age-related memory deficits linked to circuit-specific disruptions in the hippocampus.* PNAS 108:8873-8878. doi 10.1073/pnas.1101567108. Found: `tinyfish.web.search.publications`. Read: earlier retrieval, full text.

- Results: perforant-path degradation "biases this network away from pattern separation and toward pattern completion" (stated as the hypothesis tested); older adults were "less likely to call lure items similar and more likely to call them old"; perforant-path integrity correlated with separation bias, r = 0.73, n = 11.

### Yassa, Lacy, Stark, Albert, Gallagher and Stark 2011

*Pattern separation deficits associated with increased hippocampal CA3 and dentate gyrus activity in nondemented older adults.* Hippocampus 21:968-979. doi 10.1002/hipo.20808. Read: earlier retrieval (E8b), full text.

- Discussion: "the age group difference was smaller in the most similar lures (L1) than the most dissimilar lures (L5)."

### Smith, Adams, Gallagher, Morrison and Rapp 2000

*Circuit-specific alterations in hippocampal synaptophysin immunoreactivity predict spatial learning impairment in aged rats.* Journal of Neuroscience 20:6587-6593. doi 10.1523/JNEUROSCI.20-17-06587.2000. Found: located through `tinyfish.web.search.publications` results that cite it. Read: `exa.web.contents.get`, full text.

- Abstract: "Comparisons based on chronological age alone failed to reveal a reliable difference in the intensity of SYN staining in any region that was examined."
- Results: staining was "reduced by ∼28% in the aged-impaired group" in CA3's perforant-path layer.

**E8c uses**: the caution that perforant-path loss tracks impairment, not age alone.

### Stark, Kirwan and Stark 2019

*Mnemonic Similarity Task: a tool for assessing hippocampal integrity.* Trends in Cognitive Sciences 23:938-951. doi 10.1016/j.tics.2019.08.003. Found: `tinyfish.web.search.publications`. Read: earlier retrieval, full text.

- Section "Hippocampal Decline with Aging": "aging leads to reduced input to the DG via the perforant path"; a bias toward pattern completion means "endorsing a similar memory probe is the same as a prior experience".
- Lure bins: "items in Lure Bin 1 are highly similar and elicit false alarms quite often while those in Lure Bin 5 are far more dissimilar and have very few false alarms".

### Stark, Yassa, Lacy and Stark 2013

Full reference and Table 2 in `docs/e8_sources.md`. Found again: `tinyfish.web.search.publications`. Table 2 gives p(old | lure) 40.3% (20 to 39), 54.6% (60 to 74) and 64.9% (mild cognitive impairment), and the older group's p(old | repeat) 82.2% and p(new | foil) 73.4%, which set item 21's criteria. Results: "we can see a clear shift in the tuning curve as a function of age, with greater changes in the input (higher lure bin numbers) needed to produce a change in the output".

### Toner, Pirogovsky, Kirwan and Gilbert 2009

*Visual object pattern separation deficits in nondemented older adults.* Learning & Memory 16:338-342. doi 10.1101/lm.1315109. Found: `tinyfish.web.search.publications`. Read: `exa.web.contents.get`, full text.

- Results: "Younger adults were more likely to label a lure stimulus as similar, whereas older adults were more likely to label a lure as old".

### Kirwan and colleagues 2012

Full reference in `docs/e8_sources.md`. Found again: `exa.web.search.publications`.

- Results: "Thus, contrary to our second prediction, patients did not respond 'old' to similar stimuli more often than control participants." Table 2: p(old | lure) 0.38 for patients, 0.37 for controls.

### Bakker and colleagues 2012

Bakker, Krauss, Albert, Speck, Jones, Stark, Yassa, Bassett, Shelton and Gallagher. *Reduction of hippocampal hyperactivity improves cognition in amnestic mild cognitive impairment.* Neuron 74:467-474. doi 10.1016/j.neuron.2012.03.023. Found: `exa.web.search.publications`. Read: `linkup.web.fetch`, PMC3351697, full text.

- Results: patients with amnestic mild cognitive impairment on placebo "incorrectly identified lure items as 'old' more often" than controls.

## Not found or not read

- **A source placing a familiarity readout in CA3's first recurrent pass.** None of the sources above does; the modelling papers treat the recurrent network abstractly and place familiarity in perirhinal cortex.
- **Which population reads CA3's first-pass recurrent drive.** Not identified in any source read.
- **Kumaran and Maguire 2009** (Trends in Cognitive Sciences 13:47-54): only the reference list was reachable.
- **Yonelinas 2002 body text** and **Lisman and Otmakhova 2001 body text**: paywalled; abstracts only.
- **Greve, Donaldson and van Rossum 2010** (Hippocampus 20:235-251), which puts familiarity and recollection in one Hopfield network: not retrieved.
- **Geinisman and colleagues 1992** (Hippocampus 2:437-444): abstract only; it reports synapse loss of 23.6% in the middle molecular layer and 22.7% in the inner molecular layer of aged rats, so the loss it measured is not specific to the perforant path. E8c takes nothing from it.
- **A measured size of perforant-path loss in humans**: Yassa and colleagues 2010 report a group difference, not a percentage.
- **A lesion study in which hippocampal damage raises p(old | lure)**: the one read (Kirwan and colleagues 2012) found no increase.
