from __future__ import annotations
import numpy as np
import pandas as pd


def horvath_invF(z: np.ndarray, adult_age: float = 20.0) -> np.ndarray:
    """
    Horvath inverse age transform.
    """
    z = np.asarray(z, dtype=float)
    age = np.empty_like(z)

    m = z < 0
    age[m] = (adult_age + 1.0) * np.exp(z[m] + np.log(adult_age + 1.0)) - 1.0
    age[~m] = (adult_age + 1.0) * z[~m] + adult_age
    return age


def predict_horvath(
    beta: pd.DataFrame,
    w: pd.Series,
    intercept: float,
    adult_age: float = 20.0,
    fill_missing: float = 0.0,
) -> pd.Series:
    """
    beta: CpG x Sample
    w: CpG -> coefficient (length 353)
    """
    # Align to 353 CpGs (order matters)
    beta_h = beta.reindex(w.index).fillna(fill_missing)

    # Linear predictor: x = Σ(beta * w) + intercept
    x = beta_h.T.dot(w) + intercept

    # Convert to age
    dnam = pd.Series(horvath_invF(x.values, adult_age=adult_age), index=x.index, name="DNAmAge_python")
    return dnam