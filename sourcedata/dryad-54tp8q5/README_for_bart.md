# Data for Local Fields in Human Subthalamic Nucleus Track the Lead-up to Impulsive Choices

This [HDF5](https://www.hdfgroup.org/) file contains data from the linked paper [Local Fields in Human Subthalamic Nucleus Track the Lead-up to Impulsive Choices](https://www.frontiersin.org/articles/10.3389/fnins.2017.00646/full). Code to reproduce all figures and results is available at [https://github.com/jmxpearson/bart_analysis](https://github.com/jmxpearson/bart_analysis).

# Usage
Datasets in the file are written using the [Pandas](https://pandas.pydata.org/) library. We recommend using this to read datasets in as Pandas DataFrames:

```python
import pandas as pd
dbname = '/bart.hdf5'
lfplist = pd.read_hdf(dbname, '/meta/lfplist')
```

Once sets are read in as DataFrames, they can be explored and used (as in the analysis code). 

# Organization of the data
HDF5 files are organized hierarchically like a file system. For usage of this data, see the code, but briefly, the file is organized as:

- `meta`: Metadata for the dataset. Includes:
    - `censlist`: Table of valid (patient, dataset, channel) tuples.
    - `evlist`: Table of (patient, dataset) pairs.
    - `lfplist`: Table containing one row per valid (patient number, dataset, lfp channel) combination. This is used in selecting which data to load from the `/lfp` group.
    - `spklist`: Table containing one row per valid (patient number, dataset, recording channel, sorted unit). Used in selecting which data to load from the `/spikes` group.

- `censor`: Censoring information for the dataset. Indicates data that were artifactual or otherwise bad. Structure under this group is organized as `/p<patient number>/d<dataset number>/c<channel number>`. Tables list patient, dataset, channel, start, and stop times for each censored epoch.

- `events`: Tables containing behavioral data from the experiment. Directory structure is `/p<patient number>/d<dataset number>`. Datasets are Pandas DataFrames with columns:
    - `trial`: Unique trial number (0-indexed).
    - `trial_start_time`: Start time of trial (in seconds) recorded by PsychoPy.
    - `this_balloon`: Unique "balloon" number for this dataset. Since trials could not be failed, this is equal to `trial` + 1.
    - `trial_type`: Balloon color/risk level. Levels:
        - 1: low risk (yellow)
        - 2: medium risk (orange)
        - 3: high risk (red)
        - 4: no reward (gray)
    - `is_control`: Boolean indicating whether or not the trial was a control trial (no voluntary stop).
    - `ctrltime`: Computer-generated random inflate time (used on control trials only).
    - `points`: Points earned each trial.
    - `inflate_time`: Time (seconds) for which the balloon inflated before popping or being stopped. 
    - `this_run`: *Unused.*
    - `result`: Outcome of trial: 
        - 'banked': Success (points earned, balloon stopped).
        - 'popped': Balloon popped (no points).
    - `rt`: *Unused.*
    - `score`: Accumulated score.
    - `banked`: Time at which participant stopped balloon's inflation (in seconds since task start) or `NaN` if balloon popped.
    - `outcome`: Time (in seconds since task start) at which the trial outcome was displayed on screen.
    - `popped`: Same as `banked` but recorded if balloon popped and `NaN` if stopped successfully.
    - `start inflating`: Time (in seconds since task start) at which balloon started inflating.
    - `stop inflating`: Time (in seconds since task start) at which balloon stopped inflating.
    - `trial_over`: Time (in seconds since task start) at which the trial ended.
    - `trial_start`: Time (in seconds since task start) at which the trial began.
    - `patient`: Patient number.
    - `dataset`: Dataset number for this patient.

- `lfp`: Local field potentials. Recorded at 1kHz, decimated and stored here at 200Hz. Structure is again `/p<patient number>/d<dataset number>/c<channel number>`. Tables include columns for patient, dataset, channel, time, and voltage reading.

- `spikes`: Action potential (spike) times for isolated single units. Structure inside this group is `/p<patient number>/d<dataset number>/c<channel number>/u<unit number>`. Tables include columns for patient, dataset, channel, unit, and spike time.




