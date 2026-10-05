# Alerts and SOS

## Storage

`DATABASE_URL` defaults to local SQLite (`sqlite:///./terrasafe.db`); PostgreSQL is selected by setting a PostgreSQL SQLAlchemy URL. The first Alembic revision creates `alerts`, `alert_events`, and `sos_reports`. Apply it with `python -m alembic upgrade head` from the project directory. PostGIS columns and the rest of the proposed normalized product schema have not been implemented.

## Alert lifecycle

New alerts start in `CREATED`. The current permitted transitions are:

```text
CREATED -> APPROVED -> SENT -> DELIVERED -> ACKNOWLEDGED -> RESOLVED
```

Creation requires `admin` or `district_officer`; approval is limited to those roles. The persistence service rejects invalid transitions and records each event with a SHA-256 previous-hash link. Hash-chain verification detects accidental or unsophisticated edits; it is not a digital signature, trusted timestamp, or protection against a database administrator rewriting the whole chain.

`SENT` is a mock state only: the event detail explicitly says no push, SMS, WhatsApp, email, or voice was sent. There is no cooldown, dedupe worker, automatic escalation, real adapter, or retry queue. CAP output uses `status=Test` and is not an official warning.

## SOS

`POST /sos` accepts a message and optional coordinate pair and persists an OPEN report. It returns a MOCK delivery label. `GET /sos` requires a signed role token for an administrator, district officer, or field responder. No emergency service or contact is notified. Protect the local SQLite file and configure TLS, retention, access logging, consent, and operational escalation procedures before any pilot handling personal location data.

## JWT operations

Set a strong random `JWT_SECRET` in an untracked `.env`. Tokens are signed with the configured `JWT_ALGORITHM` and expire according to `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`. A trusted local operator may run `python scripts/issue_token.py --subject operator-id --role district_officer`; avoid shell history, screenshots, or logs containing the printed token. There is no login service, user table, token revocation, refresh, or external identity provider. Do not expose token issuance to public users.

CORS defaults to the two local frontend origins and can be configured via `CORS_ALLOWED_ORIGINS`. Production deployment must set an explicit origin allowlist.

## What-if and route simulation

`POST /api/v1/simulate` runs a clearly tagged DEMO weighted heuristic with hypothetical values. It is not a forecast. The route endpoint only finds the closest configured demo shelter by great-circle distance; it does not have road geometry, slope/hazard overlays, closures, or a safest-route algorithm. Do not use it for evacuation decisions.
