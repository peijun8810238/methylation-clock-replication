from __future__ import annotations

import gzip
from pathlib import Path
from typing import Optional

import pandas as pd


# ==========================================================
# GEO series matrix parsing
# ==========================================================
def parse_series_matrix_to_df(path_gz: Path) -> pd.DataFrame:
    """
    Parse the table region of a GEO series_matrix.txt.gz file
    into a raw DataFrame.

    Parameters
    ----------
    path_gz : Path
        Path to GSE****_series_matrix.txt.gz

    Returns
    -------
    pd.DataFrame
        Raw table with columns including 'ID_REF' and GSM sample IDs.

    Raises
    ------
    FileNotFoundError
        If path_gz does not exist.
    ValueError
        If the table region cannot be found.
    """
    if not path_gz.exists():
        raise FileNotFoundError(f"Series matrix not found: {path_gz}")

    header: Optional[list[str]] = None
    rows: list[list[str]] = []

    with gzip.open(path_gz, "rt") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("!series_matrix_table_begin"):
                header_line = f.readline().rstrip("\n")
                header = header_line.split("\t")
                break

        if header is None:
            raise ValueError(
                "!series_matrix_table_begin not found. "
                "This file may not be a GEO series matrix."
            )

        for line in f:
            line = line.rstrip("\n")
            if line.startswith("!series_matrix_table_end"):
                break
            rows.append(line.split("\t"))

    return pd.DataFrame(rows, columns=header)


# ==========================================================
# Beta matrix construction
# ==========================================================
def make_beta_matrix(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Convert raw GEO series matrix DataFrame into
    a CpG x Sample beta-value matrix.

    Parameters
    ----------
    df_raw : pd.DataFrame
        Raw table returned by parse_series_matrix_to_df().
        Must contain 'ID_REF' and GSM sample columns.

    Returns
    -------
    pd.DataFrame
        Beta matrix indexed by CpG IDs with sample IDs as columns.
    """
    # Clean column names (remove quotes)
    df_raw = df_raw.copy()
    df_raw.columns = df_raw.columns.str.replace('"', "", regex=False)

    if "ID_REF" not in df_raw.columns:
        raise ValueError(
            "'ID_REF' column not found in series matrix table. "
            f"Columns head: {list(df_raw.columns)[:10]}"
        )

    # Rename CpG column and clean CpG IDs
    df_raw = df_raw.rename(columns={"ID_REF": "CpG"})
    df_raw["CpG"] = df_raw["CpG"].astype(str).str.replace('"', "", regex=False)

    # Set CpG as index
    df_beta = df_raw.set_index("CpG")

    # Convert all values to numeric (non-numeric -> NaN)
    df_beta = df_beta.apply(pd.to_numeric, errors="coerce")

    return df_beta


# ==========================================================
# Sample metadata extraction via GEOparse
# ==========================================================
def extract_sample_metadata_with_geoparse(
    raw_dir: Path,
    geo: str = "GSE40279",
) -> pd.DataFrame:
    """
    Extract sample-level metadata (age, gender) using GEOparse.

    Parameters
    ----------
    raw_dir : Path
        Directory where GEO files are stored (and where GEOparse caches data).
    geo : str, optional
        GEO series ID (default: "GSE40279").

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by sample_id (GSM),
        with columns ['age', 'gender'].

    Notes
    -----
    - 'age' is converted to numeric (years) when possible.
    - Missing or unparsable values are set to NaN.
    """
    try:
        import GEOparse
    except ImportError as e:
        raise ImportError(
            "GEOparse is required for metadata extraction. "
            "Install with: pip install GEOparse"
        ) from e

    gse = GEOparse.get_GEO(geo=geo, destdir=raw_dir)

    def extract_age_gender(gsm) -> tuple[Optional[str], Optional[str]]:
        chars = gsm.metadata.get("characteristics_ch1", [])
        age: Optional[str] = None
        gender: Optional[str] = None

        for c in chars:
            c_low = c.lower()
            if c_low.startswith("age"):
                parts = c.split(":", 1)
                if len(parts) == 2:
                    age = parts[1].strip()
            elif c_low.startswith("gender"):
                parts = c.split(":", 1)
                if len(parts) == 2:
                    gender = parts[1].strip()

        return age, gender

    rows = []
    for gsm_id, gsm in gse.gsms.items():
        age, gender = extract_age_gender(gsm)
        rows.append(
            {
                "sample_id": gsm_id,
                "age": age,
                "gender": gender,
            }
        )

    df = pd.DataFrame(rows).set_index("sample_id")

    # Convert age to numeric years
    df["age"] = pd.to_numeric(df["age"], errors="coerce")

    return df