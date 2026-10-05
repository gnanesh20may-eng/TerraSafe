from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.services.data_health import check_all_sources, render_markdown_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Check registered source health and write docs/data_health.md.")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--output", type=Path, default=Path("docs/data_health.md"))
    args = parser.parse_args()
    report = check_all_sources(timeout=args.timeout)
    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_markdown_report(report), encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "generated_at": report["generated_at"],
        "counts": {
            status: sum(source["status"] == status for source in report["sources"])
            for status in ("WORKING", "MANUAL", "FAILED", "NEEDS_REVIEW")
        },
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())