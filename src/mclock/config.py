from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml


# =========================
# Dataclasses
# =========================

@dataclass(frozen=True)
class Config:
    """
    Configuration for the pipeline stage (predict + compare + figs).
    Parsed from config/default.yaml.
    """
    root: Path

    # inputs
    beta_csv: Path
    agep_csv: Path
    coef_csv: Path
    sample_metadata_csv: Path

    # outputs
    results_dir: Path
    figs_dir: Path
    run_name: str

    # compare
    sample_id_column: str
    agep_age_column: str

    # horvath
    adult_age: float
    intercept_label: str
    fill_missing_cpg: float

    # logging
    log_level: str


@dataclass(frozen=True)
class PrepConfig:
    """
    Configuration for the prepare stage (raw -> processed).
    We keep it minimal: it mainly needs paths and logging level.
    """
    root: Path

    beta_csv: Path
    agep_csv: Path
    coef_csv: Path
    sample_metadata_csv: Path

    results_dir: Path
    run_name: str
    log_level: str


# =========================
# Helpers
# =========================

def _require_map(d: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(d, Mapping):
        raise ValueError(f"Expected '{name}' to be a mapping, got: {type(d).__name__}")
    return d


def _require_key(m: Mapping[str, Any], key: str, where: str) -> Any:
    if key not in m:
        raise KeyError(f"Missing required key '{where}.{key}' in config.")
    return m[key]


def _as_path(root: Path, p: str) -> Path:
    # YAML is relative to repo root in your design
    return root / p


# =========================
# Loaders
# =========================

def load_config(config_path: str = "config/default.yaml") -> Config:
    """
    Load full pipeline Config from YAML.
    This expects the YAML structure like:
      paths: {beta_csv, agep_csv, coef_csv, sample_metadata_csv}
      outputs: {results_dir, figs_dir, run_name}
      compare: {sample_id_column, agep_age_column}
      horvath: {adult_age, intercept_label, fill_missing_cpg}
      logging: {level}
    """
    root = Path(".").resolve()
    cfg_path = root / config_path
    data: Any = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    data = _require_map(data, "config root")

    paths = _require_map(_require_key(data, "paths", "root"), "paths")
    outputs = _require_map(_require_key(data, "outputs", "root"), "outputs")
    compare = _require_map(_require_key(data, "compare", "root"), "compare")
    horvath = _require_map(_require_key(data, "horvath", "root"), "horvath")
    logging_cfg = _require_map(_require_key(data, "logging", "root"), "logging")

    beta_csv = _as_path(root, str(_require_key(paths, "beta_csv", "paths")))
    agep_csv = _as_path(root, str(_require_key(paths, "agep_csv", "paths")))
    coef_csv = _as_path(root, str(_require_key(paths, "coef_csv", "paths")))
    sample_metadata_csv = _as_path(root, str(_require_key(paths, "sample_metadata_csv", "paths")))

    results_dir = _as_path(root, str(_require_key(outputs, "results_dir", "outputs")))
    figs_dir = _as_path(root, str(_require_key(outputs, "figs_dir", "outputs")))
    run_name = str(_require_key(outputs, "run_name", "outputs"))

    sample_id_column = str(_require_key(compare, "sample_id_column", "compare"))
    agep_age_column = str(_require_key(compare, "agep_age_column", "compare"))

    adult_age = float(_require_key(horvath, "adult_age", "horvath"))
    intercept_label = str(_require_key(horvath, "intercept_label", "horvath"))
    fill_missing_cpg = float(_require_key(horvath, "fill_missing_cpg", "horvath"))

    log_level = str(_require_key(logging_cfg, "level", "logging")).upper()

    return Config(
        root=root,
        beta_csv=beta_csv,
        agep_csv=agep_csv,
        coef_csv=coef_csv,
        sample_metadata_csv=sample_metadata_csv,
        results_dir=results_dir,
        figs_dir=figs_dir,
        run_name=run_name,
        sample_id_column=sample_id_column,
        agep_age_column=agep_age_column,
        adult_age=adult_age,
        intercept_label=intercept_label,
        fill_missing_cpg=fill_missing_cpg,
        log_level=log_level,
    )


def load_prep_config(config_path: str = "config/default.yaml") -> PrepConfig:
    """
    Load PrepConfig for prepare stage.
    Uses the same YAML, but only picks what prepare needs.
    """
    cfg = load_config(config_path)
    return PrepConfig(
        root=cfg.root,
        beta_csv=cfg.beta_csv,
        agep_csv=cfg.agep_csv,
        coef_csv=cfg.coef_csv,
        sample_metadata_csv=cfg.sample_metadata_csv,
        results_dir=cfg.results_dir,
        run_name=cfg.run_name,
        log_level=cfg.log_level,
    )