from __future__ import annotations

import subprocess
import logging
from pathlib import Path
from typing import Sequence


def run_r_script(
    script_path: Path,
    args: Sequence[str],
    logger: logging.Logger,
    *,
    rscript: str = "Rscript",
    check: bool = True,
) -> None:
    """
    Run an R script via Rscript with arguments.

    Parameters
    ----------
    script_path : Path
        Path to the R script (e.g. scripts/export_horvath_coeff_from_wateRmelon.R).
    args : Sequence[str]
        Command-line arguments passed to the R script.
        Example: ["--out", "coef.csv"]
    logger : logging.Logger
        Logger instance (shared with pipeline / prepare).
    rscript : str, optional
        Rscript executable name or full path (default: "Rscript").
    check : bool, optional
        If True, raise RuntimeError when R exits with non-zero status.

    Raises
    ------
    FileNotFoundError
        If script_path does not exist.
    RuntimeError
        If R script execution fails and check=True.
    """

    if not script_path.exists():
        raise FileNotFoundError(f"R script not found: {script_path}")

    cmd = [rscript, str(script_path), *map(str, args)]
    logger.info(f"Running R command: {' '.join(cmd)}")

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )

    # ---- stdout ----
    if proc.stdout:
        logger.info("[R stdout]\n" + proc.stdout.rstrip())

    # ---- stderr ----
    # R often prints warnings to stderr, so we keep this as warning
    if proc.stderr:
        logger.warning("[R stderr]\n" + proc.stderr.rstrip())

    # ---- exit code ----
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"R script failed (exit code={proc.returncode}): {script_path}"
        )