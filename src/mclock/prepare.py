# src/mclock/prepare.py
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from mclock.config import load_config
from mclock.logger import setup_logging
from mclock.rutils import run_r_script  # 既にある想定 or 後で分離
from mclock.io.geo import (
    parse_series_matrix_to_df,
    make_beta_matrix,
    extract_sample_metadata_with_geoparse,
)


def run_prepare(
    config_path: str,
    force: bool = False,
    skip_r: bool = False,
    skip_metadata: bool = False,
) -> None:
    # ---- load config ----
    cfg = load_config(config_path)

    # ---- logging ----
    logger = logging.getLogger(__name__)

    logger.info("prepare_inputs started")
    logger.info(f"Config: {config_path}")

    # ---- GSE ----
    raw_dir = cfg.root / "data" / "raw" / "GSE40279"
    series_matrix_gz = raw_dir / "GSE40279_series_matrix.txt.gz"

    # ---- ensure dirs ----
    cfg.beta_csv.parent.mkdir(parents=True, exist_ok=True)
    cfg.coef_csv.parent.mkdir(parents=True, exist_ok=True)
    cfg.agep_csv.parent.mkdir(parents=True, exist_ok=True)
    cfg.sample_metadata_csv.parent.mkdir(parents=True, exist_ok=True)

    # ---- Step 1: beta ----
    if cfg.beta_csv.exists() and not force:
        logger.info(f"Skip beta (exists): {cfg.beta_csv}")
    else:
        logger.info("Parsing GEO series matrix")

        df_raw = parse_series_matrix_to_df(series_matrix_gz)
        df_beta = make_beta_matrix(df_raw)
        df_beta.to_csv(cfg.beta_csv)
        logger.info(f"Written beta: {cfg.beta_csv}")

    # ---- Step 2: metadata ----
    if skip_metadata:
        logger.info("Skip metadata")
    elif cfg.sample_metadata_csv.exists() and not force:
        logger.info(f"Skip metadata (exists): {cfg.sample_metadata_csv}")
    else:
        df_meta = extract_sample_metadata_with_geoparse(raw_dir)
        df_meta.to_csv(cfg.sample_metadata_csv)
        logger.info(f"Written metadata: {cfg.sample_metadata_csv}")

    # ---- Step 3/4: R ----
    if skip_r:
        logger.info("Skip R steps")
        return

    scripts_dir = cfg.root / "scripts"

    r_export_coef_script = scripts_dir / "export_horvath_coeff_from_wateRmelon.R"
    r_run_agep_script = scripts_dir / "run_agep_on_beta.R"

    if r_export_coef_script.exists() and (force or not cfg.coef_csv.exists()):
        run_r_script(
            r_export_coef_script,
            ["--out", str(cfg.coef_csv)],
            logger,
        )

    if r_run_agep_script.exists() and (force or not cfg.agep_csv.exists()):
        run_r_script(
            r_run_agep_script,
            ["--beta", str(cfg.beta_csv), "--out", str(cfg.agep_csv)],
            logger,
        )

    logger.info("prepare_inputs finished successfully")