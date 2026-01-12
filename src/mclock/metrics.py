from __future__ import annotations
import numpy as np
import pandas as pd


def mae(y_true: pd.Series, y_pred: pd.Series) -> float:
    v = (y_true - y_pred).abs().dropna()
    return float(v.mean())


def max_abs_diff(y_true: pd.Series, y_pred: pd.Series) -> float:
    v = (y_true - y_pred).abs().dropna()
    return float(v.max())


def pearson_r(y_true: pd.Series, y_pred: pd.Series) -> float:
    df = pd.concat([y_true, y_pred], axis=1).dropna()
    if df.shape[0] < 2:
        return float("nan")
    return float(np.corrcoef(df.iloc[:, 0], df.iloc[:, 1])[0, 1])