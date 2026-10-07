"""Read Python-2-era pandas/PyTables 'table' format nodes with h5py (pandas 3 cannot). Returns dict column -> ndarray."""
import pickle
import numpy as np


def _kind(v):
    if isinstance(v, np.ndarray):
        v = v.tobytes()
    if isinstance(v, bytes):
        try:
            return pickle.loads(v, encoding="latin1")
        except Exception:
            return v
    return v


def read_table(group):
    """group: h5py Group of a pandas 'table' node (contains 'table' dataset). -> dict of columns (+ 'index')."""
    t = group["table"]
    a = t[()]
    out = {"index": a["index"]} if "index" in a.dtype.names else {}
    for name in a.dtype.names:
        if not name.startswith("values_block_"):
            if name != "index":
                out[name] = a[name]
            continue
        kind = _kind(t.attrs.get(name + "_kind"))
        cols = [c.decode() if isinstance(c, bytes) else str(c) for c in kind] if isinstance(kind, (list, tuple)) else [name]
        blk = a[name]
        if blk.ndim == 1:
            blk = blk[:, None]
        for i, c in enumerate(cols):
            out[c] = blk[:, i]
    return out
