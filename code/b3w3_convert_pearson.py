"""c-pearson (Dryad doi:10.5061/dryad.54tp8q5; Pearson et al. 2017 Front Neurosci) -> iEEG-BIDS DERIVATIVE dataset.

Source: bart.hdf5 (pandas/PyTables tables written by Python 2 pandas; read here with h5py, b3w3_pt.py).
README: LFP 'recorded at 1kHz, decimated and stored here at 200Hz' -> resampled: derivative. 4 recordings have a 4 ms
(250 Hz) time step. Per (patient, dataset) the LFP channel tables (time, voltage in V) are put on a common grid
(index = round(time / step)) and written as BrainVision IEEE_FLOAT_32 in µV (float64 -> float32; error reported);
samples missing for a channel are NaN. Behaviour (events tables) -> events.tsv, one row per trial; artifact
censoring intervals (censor tables) -> extra events rows with the channel. Spike times (56 sorted units) are not
converted (no BIDS-iEEG representation); they stay in sourcedata/bart.hdf5 together with everything else.
Usage: python b3w3_convert_pearson.py <sourcedata_dl> <bids_root>
"""
import hashlib, json, os, shutil, sys
import numpy as np, h5py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b3w3_common import wtsv, wjson, write_vhdr, sha256_file
from b3w3_pt import read_table

SRC, OUT = sys.argv[1], sys.argv[2]
f = h5py.File(os.path.join(SRC, "bart.hdf5"), "r")
report = {"recordings": [], "no_lfp": []}
EVCOLS = ["trial", "trial_type", "is_control", "this_balloon", "ctrltime", "points", "inflate_time", "result", "score", "banked", "popped",
          "outcome", "start inflating", "stop inflating", "trial_start", "trial_over", "trial_start_time", "rt", "this_run"]
scans = {}
for pt in sorted(f["events"], key=lambda x: int(x[1:])):
    for ds in sorted(f["events"][pt], key=lambda x: int(x[1:])):
        if pt not in f["lfp"] or ds not in f["lfp"][pt]:
            report["no_lfp"].append(f"{pt}/{ds}"); continue
        chans = sorted(f["lfp"][pt][ds], key=lambda x: int(x[1:]))
        tabs = {c: read_table(f["lfp"][pt][ds][c]) for c in chans}
        steps = sorted({round(float(np.median(np.diff(t["time"]))), 6) for t in tabs.values()})
        assert len(steps) == 1, (pt, ds, steps)
        dt = steps[0]; fs = round(1.0 / dt, 6)
        idx = {c: np.round(t["time"] / dt).astype(np.int64) for c, t in tabs.items()}
        offgrid = max(float(np.max(np.abs(t["time"] - idx[c] * dt))) for c, t in tabs.items())
        i0 = min(int(v.min()) for v in idx.values()); i1 = max(int(v.max()) for v in idx.values())
        n = i1 - i0 + 1
        X = np.full((n, len(chans)), np.nan, dtype=np.float64)
        dup = 0
        for k, c in enumerate(chans):
            ii = idx[c] - i0
            dup += len(ii) - len(np.unique(ii))
            X[ii, k] = tabs[c]["voltage"] * 1e6
        X32 = X.astype(np.float32)
        fin = np.isfinite(X)
        err = float(np.max(np.abs(X32[fin].astype(np.float64) - X[fin]))) if fin.any() else 0.0
        nmiss = int((~fin).sum())
        sub = f"sub-{int(pt[1:]):02d}"; run = int(ds[1:])
        D = os.path.join(OUT, sub, "ieeg"); os.makedirs(D, exist_ok=True)
        stem = f"{sub}_task-bart_run-{run}"
        np.ascontiguousarray(X32).astype("<f4").tofile(os.path.join(D, stem + "_ieeg.eeg"))
        write_vhdr(os.path.join(D, stem + "_ieeg"), len(chans), fs, chans, ["µV"] * len(chans),
                   comment=f"b3w3_convert_pearson.py: bart.hdf5 /lfp/{pt}/{ds}/<channel> voltage x 1e6, float32; time 0 = sample {i0} x {dt} s")
        ev = read_table(f["events"][pt][ds])
        if "trial" not in ev:
            ev["trial"] = ev["index"]
            report.setdefault("trial_from_index", []).append(f"{pt}/{ds}")
        rows = []
        t0 = i0 * dt
        for i in range(len(ev["trial"])):
            g = lambda k: (ev[k][i].decode() if isinstance(ev[k][i], bytes) else ev[k][i].item()) if k in ev else None
            si, so = g("start inflating"), g("stop inflating")
            rows.append([round(si - t0, 6), round(so - si, 6) if so is not None and si is not None else None, "balloon",
                         int(round((si - t0) * fs)), "n/a"] + [g(k) for k in EVCOLS])
        cens = 0
        if pt in f["censor"] and ds in f["censor"][pt]:
            for c in sorted(f["censor"][pt][ds], key=lambda x: int(x[1:])):
                ct = read_table(f["censor"][pt][ds][c])
                for a, b in zip(ct["start"], ct["stop"]):
                    rows.append([round(float(a) - t0, 6), round(float(b - a), 6), "censored", int(round((float(a) - t0) * fs)), c] + [None] * len(EVCOLS))
                    cens += 1
        rows.sort(key=lambda r: (r[0], r[2]))
        wtsv(os.path.join(D, stem + "_events.tsv"), ["onset", "duration", "trial_type", "sample", "channel"] + [("balloon_type" if k == "trial_type" else k.replace(" ", "_")) for k in EVCOLS], rows)
        wtsv(os.path.join(D, stem + "_channels.tsv"), ["name", "type", "units", "low_cutoff", "high_cutoff", "sampling_frequency", "group", "status", "status_description", "description"],
             [[c, "SEEG", "µV", "n/a", "n/a", fs, "n/a", "good", "n/a",
               "intraoperative STN local field potential, channel %s of the release (%s)" % (c[1:], "32-channel microwire array" if len(chans) == 32 else "single microelectrode")] for c in chans])
        wjson(os.path.join(D, stem + "_ieeg.json"), {
            "TaskName": "bart",
            "TaskDescription": "Self-paced balloon analogue risk task: the patient stops an inflating balloon to bank points before it pops; balloon colour gives the risk level; gray balloons = no reward; control trials stop automatically (article, README).",
            "SamplingFrequency": fs, "PowerLineFrequency": 60,
            "SoftwareFilters": {"Decimation": {"Description": "README: LFP recorded at 1 kHz, decimated and stored at 200 Hz; this recording's time step is %.3f s (%.0f Hz)" % (dt, fs)}},
            "HardwareFilters": "n/a",
            "iEEGReference": "n/a (not stated in the release)",
            "Manufacturer": "Plexon; FHC (article: Plexon MAP system and FHC Guideline 4000)",
            "RecordingType": "continuous", "RecordingDuration": n / fs,
            "SEEGChannelCount": len(chans), "ECOGChannelCount": 0,
            "ElectricalStimulation": False,
        })
        scans.setdefault(sub, []).append([f"ieeg/{stem}_ieeg.vhdr", "n/a"])
        import mne
        rr = mne.io.read_raw_brainvision(os.path.join(D, stem + "_ieeg.vhdr"), preload=False, verbose="error")
        k = min(2000, n)
        A = rr.get_data(start=0, stop=k) * 1e6; B = X[:k].T
        rt = bool(rr.n_times == n and rr.ch_names == chans and np.allclose(A[np.isfinite(B)], B[np.isfinite(B)], rtol=1e-6, atol=1e-3))
        report["recordings"].append(dict(patient=pt, dataset=ds, sub=sub, run=run, channels=chans, sfreq=fs, n_samples=n, time0=t0, offgrid_max=offgrid,
                                         duplicate_samples=dup, missing_values=nmiss, float32_max_abs_err_uV=err, n_trials=len(ev["trial"]), n_censor=cens, roundtrip_ok=rt))
        print(stem, len(chans), n, fs, "t0", t0, "offgrid", offgrid, "dup", dup, "miss", nmiss, "err", err, "trials", len(ev["trial"]), "cens", cens, "rt", rt, flush=True)
for sub, r in scans.items():
    wtsv(os.path.join(OUT, sub, f"{sub}_scans.tsv"), ["filename", "acq_time"], sorted(r))
n_units = sum(len(f["spikes"][p][d][c]) for p in f["spikes"] for d in f["spikes"][p] for c in f["spikes"][p][d])
report["spike_units"] = n_units
SD = os.path.join(OUT, "sourcedata", "dryad-54tp8q5"); os.makedirs(SD, exist_ok=True)
for fn in ("bart.hdf5", "README_for_bart.md"):
    shutil.copy(os.path.join(SRC, fn), os.path.join(SD, fn))
report["sourcedata_sha256"] = {fn: sha256_file(os.path.join(SD, fn)) for fn in ("bart.hdf5", "README_for_bart.md")}
os.makedirs(os.path.join(OUT, "code"), exist_ok=True)
for fn in (__file__, os.path.join(os.path.dirname(os.path.abspath(__file__)), "b3w3_common.py"), os.path.join(os.path.dirname(os.path.abspath(__file__)), "b3w3_pt.py")):
    shutil.copy(fn, os.path.join(OUT, "code", os.path.basename(fn)))
json.dump(report, open(os.path.join(OUT, "code", "conversion_report.json"), "w"), indent=1, default=str)
R_ = report["recordings"]
print(json.dumps({"recordings": len(R_), "rt_all": all(r["roundtrip_ok"] for r in R_), "hours": sum(r["n_samples"] / r["sfreq"] for r in R_) / 3600,
                  "max_err_uV": max(r["float32_max_abs_err_uV"] for r in R_), "missing": sum(r["missing_values"] for r in R_),
                  "dup": sum(r["duplicate_samples"] for r in R_), "no_lfp": report["no_lfp"], "spike_units": n_units}, indent=1))
print("CONVERT_DONE")
