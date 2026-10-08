[![DOI](https://img.shields.io/badge/DOI-10.82901%2Fnemar.nm000401-blue)](https://doi.org/10.82901/nemar.nm000401)

# Subthalamic LFP during the balloon analogue risk task (Pearson et al., 2017) - DERIVATIVE

Intraoperative recordings from the subthalamic nucleus (STN) of patients with Parkinson's disease during DBS
implantation (Duke University Medical Center) while they played a self-paced balloon analogue risk task (BART).
Single microelectrodes, and in a subset (article: 7 datasets) a 32-channel Pt/Ir microwire array.

THIS IS A DERIVATIVE DATASET: the LFP in the release was "recorded at 1kHz, decimated and stored here at 200Hz"
(release README); it is not the raw acquisition.

## Source
- Dryad: John M. Pearson, Patrick T. Hickey, Shivanand P. Lad, Michael L. Platt, Dennis A. Turner. Data from: Local fields in human subthalamic nucleus track the lead-up to impulsive
  choices. doi:10.5061/dryad.54tp8q5 (version 1, 2018-08-07). License: CC0 1.0 (Dryad).
- Article: Front Neurosci 11:646 (2017), doi:10.3389/fnins.2017.00646 (PMC5703842). Code: https://github.com/jmxpearson/bart_analysis
- Both Dryad files were downloaded through the Dryad API and matched the Dryad md5 digests and sizes.

## Contents
- `sub-<nn>/ieeg/sub-<nn>_task-bart_run-<dataset>_ieeg.*`: 17 recordings of 14 patients (`sub-<nn>` =
  patient p<nn> of bart.hdf5; `run` = its dataset number, e.g. the two sides of a bilateral implantation), 4.33 h.
  Channels `c<k>` = channel numbers of the release (1 channel, or 32 for the microwire arrays). Values: the release
  voltages (V) x 1e6 as float32 µV (max absolute rounding error 0.49 µV). Time zero = time 0 of the release LFP tables.
- Sampling: 200 Hz (5 ms step) except sub-17 run-1, sub-21 run-1, sub-24 run-1, sub-25 run-1 (4 ms step, 250 Hz), as measured from the
  time columns; the README states 200 Hz for all.
- `events.tsv`: one `balloon` row per trial with every behavioural column of the release (onset = 'start inflating'),
  plus `censored` rows with the artifact intervals per channel from /censor. Event times are used as stored; the
  release does not state explicitly that behaviour and LFP share the time axis (both are in seconds from the task
  start in the authors' analysis).
- Behaviour tables without LFP (patient/dataset): p10/d1, p25/d2 (behaviour and, for p10, spikes only; in sourcedata).
- Spike times of 56 sorted units (/spikes) are NOT converted (BIDS-iEEG has no spike format); they are in
  `sourcedata/dryad-54tp8q5/bart.hdf5` (the complete, unchanged release file) with README_for_bart.md.
- No electrode coordinates are released; `electrodes.tsv` lists the channels with x, y, z = n/a.

## Participants
15 patients (5 female, 10 male) per the article; its Table 1 gives age bands, disease duration, LEDD and surgery side
per row, without patient numbers, so they are not assigned to subjects here.

## Privacy
bart.hdf5 holds patient numbers, times in seconds and behaviour only; no names or dates were found. The file is
included unchanged.

## Additional metadata and localisation (added 2026-10-08)

Compiled after the upload from the article, its supplement and the source deposit (each statement names its source). Text and sidecar metadata only; no data file was changed.

Sources: P = Pearson, Hickey, Lad, Platt, Turner 2017, Front Neurosci 11:646, doi:10.3389/fnins.2017.00646 (PMC5703842). R = deposit README_for_bart.md. F = bart.hdf5 metadata (Voyager Job).

**Recording.** Plexon MAP system with FHC Guideline 4000. For single-electrode recordings, the high-pass (spike) and low-pass (LFP) signals were recorded; for the 32-channel arrays, LFP came from all 32 channels and high-pass from the 16 most active (P). LFP was recorded at 1 kHz and stored decimated to 200 Hz (R). The time step is 4 ms (250 Hz) in p17/d1, p21, p24 and p25 (measured from the file; atlas note). Spikes were sorted offline with WaveClus (P). Censoring tables mark artifactual epochs (R).

**Electrodes.** Single-channel tungsten microelectrodes (Frederick Haer) were used for STN localisation. In 7 datasets (16.2, 17.2, 18.1, 20.1, 22.1, 23.1, 30.1), after mapping, a 32-channel Pt/Ir microwire array (35 µm wires, Ad-Tech) was passed to the STN through an outer cannula and slowly advanced (P).

**Reference.** Not stated in P. For analysis, the mean across channels was subtracted at each time point (P, LFP preprocessing).

**Localisation.** The STN was targeted indirectly (X 11-12 mm from midline, Y 2 mm behind the AC-PC midpoint, Z 4 mm below AC-PC), refined on FLAIR, and its borders were defined by single-unit mapping (aim: at least 5.5-6 mm of STN multi-unit activity, typically 2-3 passes). Data were mostly collected during localisation, with the electrode left at a well-isolated unit. Both sides were recorded in subjects 14, 16 and 17. 55 of 56 units were judged to be within STN boundaries; one was probably in SNr. The microwire positions are "distributed at random throughout STN" (P, Methods/Results/Discussion). No per-channel coordinates, depths or hemispheres are published or present in F.
