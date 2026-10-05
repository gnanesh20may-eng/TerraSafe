from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.core.auth import issue_token


def main() -> int:
    parser = argparse.ArgumentParser(description="Issue a short-lived local JWT for a trusted operator.")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--role", required=True, choices=("admin", "district_officer", "field_responder", "public"))
    args = parser.parse_args()
    try:
        print(issue_token(args.subject, args.role))
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
