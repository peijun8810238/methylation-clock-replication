#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mclock.config import load_prep_config
from mclock.logger import setup_logging
from mclock.prepare import run_prepare


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        prog="prepare_inputs",
        description="Prepare processed inputs (beta/metadata/coef/agep) for the DNAmAge replication pipeline.",
    )
    ap.add_argument(
        "--config",
        default="config/default.yaml",
        help="Path to YAML config (same file used by run_pipeline.py).",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Re-generate outputs even if they already exist.",
    )
    ap.add_argument(
        "--skip-r",
        action="store_true",
        help="Skip R steps (coefficients export and agep run).",
    )
    ap.add_argument(
        "--skip-metadata",
        action="store_true",
        help="Skip sample metadata extraction via GEOparse.",
    )
    return ap.parse_args()


def main() -> int:
    args = parse_args()

    cfg = load_prep_config(args.config)

    log_dir = cfg.results_dir / "logs_prepare"
    setup_logging(log_dir=log_dir, run_name=f"{cfg.run_name}_prepare", level=cfg.log_level)

    # 3) 実処理
    run_prepare(
        config_path=args.config,
        force=args.force,
        skip_r=args.skip_r,
        skip_metadata=args.skip_metadata,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())