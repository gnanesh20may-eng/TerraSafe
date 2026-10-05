"""Command-line entry point for the synthetic Nilgiris P1 pilot."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from backend.app.ml.susceptibility import train_and_export
from backend.app.ml.synthetic_data import generate_nilgiris_pilot


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", default="Nilgiris, Tamil Nadu")
    parser.add_argument(
        "--bounds",
        nargs=4,
        type=float,
        metavar=("WEST", "SOUTH", "EAST", "NORTH"),
        default=(76.2, 11.1, 76.9, 11.6),
        help="Synthetic area extent in WGS84 longitude/latitude coordinates.",
    )
    parser.add_argument("--grid-size", type=int, default=40)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=Path("ml/data/generated"))
    parser.add_argument("--no-mlflow", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    pilot = generate_nilgiris_pilot(
        grid_size=args.grid_size,
        seed=args.seed,
        region=args.region,
        bounds=tuple(args.bounds),
    )
    result = train_and_export(
        pilot,
        output_dir=args.output_dir,
        seed=args.seed,
        log_to_mlflow=not args.no_mlflow,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
