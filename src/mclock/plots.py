from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def scatter_compare(df: pd.DataFrame, xcol: str, ycol: str, out_png: Path, alpha: float = 0.5) -> None:
    out_png.parent.mkdir(parents=True, exist_ok=True)

    x = df[xcol]
    y = df[ycol]

    mn = float(min(x.min(), y.min()))
    mx = float(max(x.max(), y.max()))

    plt.figure(figsize=(4.8, 4.8))
    plt.scatter(x, y, alpha=alpha)
    plt.plot([mn, mx], [mn, mx])
    plt.xlabel(xcol)
    plt.ylabel(ycol)
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()