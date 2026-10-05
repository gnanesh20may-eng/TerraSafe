# P2 ingestion, dynamic risk, and forecast baseline

## Source adapters

`build_ingestors()` constructs a local fixture adapter for each configured
source: Open-Meteo, GPM IMERG, SMAP, ERA5-Land, USGS earthquakes, NASA FIRMS,
and IMD/MOSDAC. Every fixture is tagged `mock: true` and carries a `MOCK`
source label. The async HTTP adapter is opt-in, uses a timeout, bounded retries,
`Retry-After`, minimum request spacing, and an in-memory TTL cache. Live
provider credentials and endpoint configuration are passed at runtime; no
secret is stored in source.

The Open-Meteo forecast adapter uses hourly precipitation and soil-moisture
fields. Separate adapters cover its forecast, ensemble, historical forecast,
and historical archive endpoints; historical live requests require an
inclusive `start_date` and `end_date` in `YYYY-MM-DD` format. The USGS adapter
requests FDSN GeoJSON with ISO-8601 UTC time bounds.
Other live sources currently need operator-provided normalized JSON endpoints;
this is **not** a product-specific NetCDF/HDF/CSV reader for NASA or IMD data.
FIRMS requires a NASA MAP_KEY, and NASA Earthdata products require the
appropriate Earthdata access configuration. Keep mock mode enabled unless a
provider-specific normalizer, provenance, units, and licensing have been
verified.

Official documentation consulted:

- [Open-Meteo Forecast API](https://open-meteo.com/en/docs)
- [Open-Meteo Ensemble API](https://open-meteo.com/en/docs/ensemble-api)
- [Open-Meteo Historical Forecast API](https://open-meteo.com/en/docs/historical-forecast-api)
- [USGS FDSN Event Web Service](https://earthquake.usgs.gov/fdsnws/event/1/)
- [NASA FIRMS Area API](https://firms.modaps.eosdis.nasa.gov/api/area/)
- [NASA Earthaccess](https://earthaccess.readthedocs.io/en/latest/)
- [NASA GPM IMERG](https://gpm.nasa.gov/data/imerg)
- [MAPIE split-conformal quick start](https://mapie.readthedocs.io/en/latest/content/getting-started/quick-start/)
- [SHAP documentation](https://shap.readthedocs.io/en/latest/)

## Dynamic risk calculations

`antecedent_rainfall()` reports rainfall totals for 1h, 24h, 72h, 7d, and 30d,
including observed-hour coverage; missing readings are never treated as zero.
Intensity-duration checks use configurable `I = a * D**(-b)` parameters. The
defaults are demonstration values, not local warning thresholds.

`infinite_slope_factor_of_safety()` applies a transparent infinite-slope
equation using explicitly supplied soil depth, unit weight, friction angle,
cohesion, and saturation. Unless measured site parameters are supplied, its
result is only a scenario estimate. `hybrid_dynamic_risk()` combines static
susceptibility and available rainfall, slope-stability, soil-moisture, and
earthquake trigger components into a weighted 0–1 **index**, not a calibrated
probability. The Green/Yellow/Orange/Red cutoffs are provisional.

## Forecast uncertainty and explanations

`forecast_risk_horizons()` produces transparent 24/48/72-hour trigger-based
outlooks. It is a deterministic baseline, not a trained Temporal Fusion
Transformer or LSTM. `mapie_regression_intervals()` wraps a fitted
scikit-learn-compatible regressor with MAPIE split conformalization. A
forecast-only interval is omitted when adequate held-out calibration data are
not supplied. Conformal coverage requires calibration/forecast exchangeability
and does not make these synthetic or biased observations operationally safe.

`explain_with_shap()` returns model-native SHAP contributions when SHAP is
available, otherwise explicitly reports that no SHAP explanation was produced.
`constrained_counterfactuals()` reports bounded model-sensitivity scenarios;
they are not causal explanations or intervention advice. Deterministic
plain-language explanations remain available without an AI service.

## Drift and retraining

The feature PSI report is a drift signal, not proof of model degradation.
`retraining_recommendation()` only returns an operator-review recommendation;
it does not launch training or promote a replacement model. Retraining must
use licensed, provenance-tracked observations and spatially held-out
validation.

`export_classifier_to_onnx()` exports a fitted scikit-learn-compatible
classifier to ONNX when `skl2onnx` conversion support is installed. The ONNX
artifact is an inference artifact only; validate numerical parity and runtime
compatibility before deploying it.

## Safety and provenance

No real rainfall, soil-moisture, earthquake, fire, or IMD/MOSDAC feed was
queried to create the fixtures. Synthetic input/output is labeled, and all
scores remain experimental. LandSense is a decision-support tool, not a
replacement for official IMD, NDMA, or GSI warnings.
