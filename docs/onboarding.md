# Developer onboarding

TerraSafe is an experimental landslide decision-support prototype. It is **not
a replacement for official IMD, NDMA, or GSI warnings**. Synthetic data, local
fixtures, and unvalidated risk estimates must not guide safety decisions.

## Requirements

- Python 3.11+ and Git.
- Windows PowerShell 5.1+ or a POSIX shell.
- Node.js/npm only if working on the frontend; this checkout currently has no
  frontend package manifest or build command.

## Setup

From the repository root in PowerShell:

```powershell
.\scripts\setup.ps1
.\.venv\Scripts\Activate.ps1
python -m pytest backend/tests -q
```

On macOS/Linux:

```bash
./scripts/setup.sh
source .venv/bin/activate
python -m pytest backend/tests -q
```

The scripts create a local `.venv` if one is absent. PowerShell setup uses
Python 3.11 via the Windows `py` launcher. If that version is not installed,
install it or create the environment with an available compatible interpreter
before running the script. No credentials or external datasets are required
for the existing tests.

## Windows tree-model DLL / Application Control limitation

Some Windows installations block native tree-model dependencies such as
LightGBM or XGBoost through Windows Application Control or DLL policy. Do not
disable the policy or download untrusted DLLs. Treat optional tree-model import
or training failure as a capability limitation and use the supported
LogisticRegression baseline instead. The P1 synthetic training experiment and
P2 helper tests are not field validation.

## Colab workaround

If approved local policy blocks optional native tree-model packages, a
maintainer may run a future, explicitly labeled notebook in Google Colab with
the repository code and permitted data. Notebooks are not included or run in
this checkout. Do not upload private, restricted, or personally identifying
data to Colab; do not present notebook output as an operational model without
provenance, spatially independent evaluation, calibration, and domain review.

## Contribution workflow

Open a pull request with the provided template. Add or update focused tests,
run the checks for the changed area, and update `docs/status.md` and
`docs/run_log.md`. Mark each feature LIVE, DEMO, SIMULATED, SCAFFOLD, or
MISSING; report only observed outputs. Never commit `.env` files, secrets,
generated datasets, or trained model artifacts.
