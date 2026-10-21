# E8b sources

E8b sets the model's study list to the length people study in the Mnemonic Similarity Task and builds a second set of lures closer to the studied item. This file records what the human task is, checked in the full texts below. Quotes are exact. The human rates E8b compares against (young adults' Table 2 in Stark and colleagues 2013) and every lesion source are in `docs/e8_sources.md` and are not repeated here.

## The task

In the **Mnemonic Similarity Task** (MST), a person studies a series of pictures of everyday objects once, then sees **repeats** (the same picture), **lures** (a similar picture never shown) and **foils** (new pictures), and answers old, similar or new for each.

## Stark, Yassa, Lacy and Stark 2013

*A task to assess behavioral pattern separation (BPS) in humans: Data from healthy aging and mild cognitive impairment.* Neuropsychologia 51:2442-2449 (title, volume and pages checked on Crossref). doi 10.1016/j.neuropsychologia.2012.12.014. Read in the PubMed Central full text, PMC3675184, which carries no journal page numbers, so quotes are located by section.

**Study list and test list** (Materials and Methods, the paragraph describing the BPS-O, the paper's name for the task):

> "The BPS-O ( Figure 1 ) consisted of a series of 192 color photographs of everyday objects on a white background. In the first phase, participants engaged in an indoor/outdoor judgment for each picture via a button press (128 items total, 2s each, 0.5s ISI). Immediately following the encoding task, participants were given instructions regarding a surprise recognition memory test in which they identified each item as "Old", "Similar", or "New" via button press (192 items total – 64 repeated items, 64 lure items, and 64 foil items; 2s each, 0.5s ISI)."

So people study 128 pictures once and are tested on 192: 64 repeats, 64 lures and 64 foils. Every studied picture comes back once, either as itself or as the source of a lure.

**What a lure is** (Introduction, describing the task):

> "One-third of the images in the test phase are exact repetitions of images presented in the study phase (targets); one-third of the images are new images not previously seen (foils); and one-third of the images are perceptually similar to those seen during the study phase, but not identical (lures)."

**How lures are sorted by similarity** (Results, the paragraph on lure bins):

> "In previous development of the task, we rank-ordered the lures by level of mnemonic similarity to the targets by assessing the probability of producing false alarms to the lures (calling them "old") for each lure item using a large, independent population of young participants ( Yassa, … Stark, 2010c ). In that study, the stimuli were divided into 5 lures bins, with the more mnemonically similar lures in lure bin 1 (L1) and the least mnemonically similar lure items in lure bin 5 (L5). The same assignment of lure stimuli to lure bins was used here."

**Where the materials come from** (Discussion): "We have developed a stand-alone version of the BPS-O for free download at http://darwin.bio.uci.edu/~cestark/bpso/bpso.html to be used by other research groups interested in examining pattern separation." That address was not opened here; the counts above come from the paper itself.

## Yassa, Lacy, Stark, Albert, Gallagher and Stark 2011 (cited as 2010c)

*Pattern separation deficits associated with increased hippocampal CA3 and dentate gyrus activity in nondemented older adults.* Hippocampus 21:968-979 (checked on Crossref; Stark and colleagues 2013 cite its 2010 online version as Yassa and colleagues 2010c). doi 10.1002/hipo.20808. Read in the PubMed Central full text, PMC3010452, located by section.

**The same list lengths** (Materials and Methods, "Mnemonic Similarity Task"):

> "Participants viewed 128 pictures of common objects (2000 ms each, 500 ms inter-stimulus-interval). After a delay of several minutes, participants were shown 64 of the studied objects, 64 new objects, and 64 lure items that were similar to but not identical to studied objects."

**How the lures were made and rated** (same section):

> "In order to norm the stimuli, we tested 114 college-age undergraduates to generate a mnemonic similarity rating for each pair (rather than a simple perceptual similarity rating). Figure 1 shows examples of lower-similarity and higher-similarity pairs as determined by their probability of responding "old" to an item when the lure version was presented. In constructing the stimuli this way, we were able to present stimuli with no delta-input (repetitions), large amounts of delta-input (new items), and known, variable amounts of delta-input (lures). Lure trials were then sorted into five bins based on the degree of mnemonic similarity."

Figure 1 legend: "Sample behavioral task stimuli ranked in order of mnemonic similarity with highly dissimilar object pairs at the far left and highly similar object pairs at the far right."

## What E8b takes from these

- **List length.** The human study list is 128 pictures, tested with 64 repeats, 64 lures and 64 foils. E8 already used this mix (half the studied items return as repeats, half as lure sources, and as many foils as each), so E8b's main list is 128 drawings with the same mix.
- **Lure construction.** Human lures are pictures of a similar object, photographed separately, and their similarity is a behavioural measure: how often young people call the lure old. No source gives a physical or pixel measure of how close a lure is to its studied picture, so no number from the human lures sets E8b's closer lures. E8b builds them by distorting the studied drawing itself and sorts them by vision-code similarity, a stand-in, as E8's bins were.

## Not found

- **Pixel or feature similarity of MST lures to their studied pictures.** The sources give only the behavioural similarity (false-alarm rates), and per-bin rates appear only in figures (see `docs/e8_sources.md`).
