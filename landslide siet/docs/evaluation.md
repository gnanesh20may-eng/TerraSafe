# Evaluation and Data-Quality Protocol

## Current evidence

The checked-in susceptibility pipeline uses deterministic synthetic cells and labels; those labels are not an event inventory. This audit did not train a model or compute performance metrics. The live weather query exercised in Phase 2 is Open-Meteo ERA5-Land reanalysis for one Nilgiris coordinate, not gauge observations. The USGS query returned an empty event feature collection for the selected 30-day window and magnitude threshold. These source checks are not model evaluation.

## Negative-sample strategy

Do not treat every location without a recorded landslide as a stable negative: inventory absence can mean incomplete reporting. For a future real dataset, first establish inventory completeness and event dates with GSI/authority partners. Exclude locations inside documented event footprints and a domain-approved spatial runout/uncertainty buffer from negative sampling; the buffer distance is intentionally not specified until local geomorphology and mapping accuracy are reviewed. Sample background locations only from areas with adequate observation coverage, match terrain and exposure support where appropriate, and retain an explicit `label_source`/`label_confidence` field. Keep uncertain/unmapped cells unlabeled or use a documented positive-unlabeled method, not forced negatives.

Synthetic negatives may be used for software tests only and must retain a `synthetic` marker. They must not be mixed into field validation or reported as scientific evidence.

## Data checks

`scripts/validate_download.py` reports WGS84 coordinate plausibility, null and duplicate coordinates, hourly field-length alignment, null/non-finite values, duplicate/unordered timestamps, and the label balance when a labeled point table is supplied to the validation helper. `check_spatial_block_leakage` verifies that train/test spatial block identifiers do not overlap. A passing structural check does not establish source accuracy, label correctness, or scientific validity.

## Validation design before deployment

- Split by non-overlapping spatial blocks and, where data permit, hold out a later time period.
- Report precision, recall, F1, ROC-AUC, PR-AUC, confusion matrix, false-alarm rate, and miss rate with denominators and confidence intervals.
- Prioritize miss-rate review and threshold calibration with local authorities; never select an operational threshold from synthetic labels.
- Compare baseline LogisticRegression with alternatives only after data governance, leakage checks, and repeatable spatial-temporal folds are in place.
- Do not claim lead time without timestamped observations, event onset, and an explicit censoring/forecast protocol.

Risk outputs are decision support, not a replacement for official IMD, NDMA, GSI, or local-authority warnings.
