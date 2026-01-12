import argparse
from mclock.pipeline import run

def main():
    parser = argparse.ArgumentParser(description="Run Horvath DNAmAge pipeline")
    parser.add_argument("--config", type=str, default="config/default.yaml", help="Path to config YAML")
    parser.add_argument("--log-level", type=str, default=None, help="Override logging level (DEBUG/INFO/WARNING/ERROR)")
    parser.add_argument("--dry-run", action="store_true", help="Do not write outputs; only log what would happen")
    args = parser.parse_args()

    run(config_path=args.config, log_level_override=args.log_level, dry_run=args.dry_run)

if __name__ == "__main__":
    main()