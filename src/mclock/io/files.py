from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def read_beta(path: Path) -> pd.DataFrame:
    """
    Read CpG x Sample beta matrix CSV.

    Expected format:
      - index column: CpG IDs
      - columns: GSM sample IDs
    """
    logger.info(f"Loading beta matrix: {path}")
    df = pd.read_csv(path, index_col=0)
    logger.info(f"Beta matrix loaded: shape={df.shape}")
    return df


def read_agep(path: Path, sample_id_column: str) -> pd.DataFrame:
    """
    Read agep output CSV and index by sample_id_column.

    If sample_id_column is missing, falls back to the first column as index.
    """
    logger.info(f"Loading agep results: {path}")
    df = pd.read_csv(path)

    if sample_id_column in df.columns:
        df = df.set_index(sample_id_column)
        logger.info(f"agep results indexed by column: {sample_id_column}")
    else:
        # fallback: first column
        df = df.set_index(df.columns[0])
        logger.warning(
            f"sample_id_column='{sample_id_column}' not found. "
            f"Using first column as index: {df.index.name}"
        )

    logger.info(f"agep results loaded: shape={df.shape}")
    return df


def read_coefficients(
    path: Path,
    intercept_label: str = "(Intercept)",
) -> tuple[float, pd.Series]:
    """
    Read Horvath coefficient table.

    Supported column sets:
      - term, weight   (exported from wateRmelon runtime)
      - CpG,  Coef     (older / alternative format)

    Returns:
      intercept (float)
      weights (pd.Series indexed by CpG)
    """
    logger.info(f"Loading coefficients: {path}")
    df = pd.read_csv(path)

    # normalize header lookup (case-insensitive)
    cols_lower = {c.strip().lower(): c for c in df.columns}

    def _pick(*names: str) -> str | None:
        for n in names:
            key = n.strip().lower()
            if key in cols_lower:
                return cols_lower[key]
        return None

    # choose schema
    c_term = _pick("term", "cpg", "probe", "id")
    c_w = _pick("weight", "coef", "coefficient", "beta")

    if c_term is None or c_w is None:
        raise ValueError(
            "Coefficient CSV must contain either (term, weight) or (CpG, Coef). "
            f"Got columns: {list(df.columns)}"
        )

    # ensure term is string (sometimes read as categorical/object already)
    df[c_term] = df[c_term].astype(str)

    # intercept
    intercept_rows = df.loc[df[c_term] == intercept_label, c_w]
    if intercept_rows.empty:
        raise ValueError(
            f"Intercept label '{intercept_label}' not found in column '{c_term}'. "
            f"Example head terms: {df[c_term].head(5).tolist()}"
        )
    intercept = float(intercept_rows.iloc[0])

    # weights (exclude intercept)
    w = (
        df.loc[df[c_term] != intercept_label, [c_term, c_w]]
        .set_index(c_term)[c_w]
        .astype(float)
    )

    logger.info(
        f"Coefficients loaded: term_col='{c_term}', weight_col='{c_w}', "
        f"n_cpg={len(w)}, intercept={intercept:.6f}"
    )
    return intercept, w


def write_csv(df: pd.DataFrame, path: Path, index: bool = True) -> None:
    """Write a DataFrame to CSV with directory creation and logging."""
    path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Writing CSV: {path}")
    df.to_csv(path, index=index)
    logger.info("CSV written")