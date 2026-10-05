"""Create a short-lived local API token from JWT_SECRET in the environment."""

from __future__ import annotations

import argparse

from backend.app.security import ROLES, create_access_token


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--role", required=True, choices=sorted(ROLES))
    args = parser.parse_args()
    try:
        token = create_access_token(args.subject, args.role)
    except (RuntimeError, ValueError) as exc:
        parser.error(str(exc))
    print(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
