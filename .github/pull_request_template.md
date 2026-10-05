## Summary

<!-- Describe the change and why it is needed. -->

## Feature status

Mark every affected feature in the UI and `docs/status.md` as LIVE, DEMO,
SIMULATED, SCAFFOLD, or MISSING.

## Validation

- [ ] `pytest backend/tests -q`
- [ ] `npm run build` (when a frontend package is present)
- [ ] `git -c core.whitespace=cr-at-eol diff --check`
- [ ] No secrets, generated datasets, or model artifacts added

## Safety and data

- [ ] Not represented as a replacement for official IMD/NDMA/GSI warnings
- [ ] Provider mode, provenance, and any manual/login-only steps are documented
- [ ] Any alerts or rescue behavior is labeled DEMO/SIMULATED unless verified
