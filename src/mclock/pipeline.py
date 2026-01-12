from __future__ import annotations
import logging
from pathlib import Path
import pandas as pd

from .config import load_config
from .logger import setup_logging
from .io.files import read_beta, read_agep, read_coefficients, write_csv
from .hovarth import predict_horvath
from .metrics import mae, max_abs_diff, pearson_r
from .plots import scatter_compare


def run(config_path: str = "config/default.yaml", log_level_override: str | None = None, dry_run: bool = False) -> None:
    cfg = load_config(config_path)

    # outputs
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    cfg.figs_dir.mkdir(parents=True, exist_ok=True)

    # logging
    log_dir = cfg.results_dir / "logs"
    level = (log_level_override or cfg.log_level)
    setup_logging(log_dir=log_dir, run_name=cfg.run_name, level=level)
    logger = logging.getLogger(__name__)

    logger.info("Pipeline started")
    logger.info(f"Config: {cfg.root / config_path}")
    if dry_run:
        logger.warning("Dry-run enabled: outputs will NOT be written.")

    # load inputs
    beta = read_beta(cfg.beta_csv)
    agep = read_agep(cfg.agep_csv, sample_id_column=cfg.sample_id_column)
    intercept, w = read_coefficients(cfg.coef_csv, intercept_label=cfg.intercept_label)

    # predict
    logger.info("Predicting DNAmAge (Horvath) in Python")
    dnam_py = predict_horvath(
        beta=beta,
        w=w,
        intercept=intercept,
        adult_age=cfg.adult_age,
        fill_missing=cfg.fill_missing_cpg,
    )
    logger.info(f"Prediction complete: n_samples={dnam_py.shape[0]}")

    # compare
    if cfg.agep_age_column not in agep.columns:
        raise ValueError(
            f"agep_age_column '{cfg.agep_age_column}' not found in {cfg.agep_csv}. "
            f"Available columns: {list(agep.columns)[:20]}"
        )

    cmp = pd.concat([dnam_py, agep[cfg.agep_age_column]], axis=1).dropna()
    cmp.columns = ["DNAmAge_python", "DNAmAge_agep"]
    diff = cmp["DNAmAge_python"] - cmp["DNAmAge_agep"]

    summary = pd.DataFrame(
        [{
            "run_name": cfg.run_name,
            "n_samples_compared": int(cmp.shape[0]),
            "mae_years": mae(cmp["DNAmAge_agep"], cmp["DNAmAge_python"]),
            "max_abs_diff_years": max_abs_diff(cmp["DNAmAge_agep"], cmp["DNAmAge_python"]),
            "pearson_r": pearson_r(cmp["DNAmAge_agep"], cmp["DNAmAge_python"]),
            "mean_abs_diff_years": float(diff.abs().mean()),
        }]
    )

    # write outputs
    compare_csv = cfg.results_dir / f"{cfg.run_name}_compare.csv"
    summary_csv = cfg.results_dir / f"{cfg.run_name}_summary.csv"
    fig_png = cfg.figs_dir / f"{cfg.run_name}_scatter.png"

    if dry_run:
        logger.info(f"[dry-run] Would write compare CSV: {compare_csv}")
        logger.info(f"[dry-run] Would write summary CSV: {summary_csv}")
        logger.info(f"[dry-run] Would write figure: {fig_png}")
    else:
        write_csv(cmp, compare_csv, index=True)
        write_csv(summary, summary_csv, index=False)

        logger.info(f"Writing figure: {fig_png}")
        scatter_compare(cmp, "DNAmAge_agep", "DNAmAge_python", fig_png, alpha=0.5)
        logger.info("Figure written")

    logger.info("Pipeline finished successfully")
    logger.info(f"Outputs: {compare_csv} | {summary_csv} | {fig_png}")