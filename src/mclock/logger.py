from __future__ import annotations
import logging
from pathlib import Path
from datetime import datetime


def setup_logging(log_dir: Path, run_name: str, level: str = "INFO") -> Path:
    """
    Configure root logger to write both console and file logs.

    Log format includes:
      - datetime
      - level
      - logger name
      - message
    """
    log_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = log_dir / f"{run_name}_{ts}.log"

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear existing handlers (important for notebook / repeated runs)
    for h in list(root.handlers):
        root.removeHandler(h)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(formatter)

    root.addHandler(ch)
    root.addHandler(fh)

    logging.getLogger(__name__).info("Logging initialized")
    logging.getLogger(__name__).info(f"Log file: {log_path}")

    return log_path