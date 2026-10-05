# Model Artifact Directory

Model artifacts are not committed. `scripts/fetch_models.py --manifest <reviewed-manifest.json>` downloads HTTPS artifacts only after validating the manifest SHA-256 and refusing files larger than 200 MiB.

Joblib uses Python pickle serialization and can execute code while loading. Only load artifacts from a trusted, reviewed publisher and independently verify the manifest source. A checksum detects mismatch; it does not prove a publisher is trustworthy.

No exported model is currently present. The inference module therefore uses an explicitly labelled synthetic LogisticRegression fallback for local demonstration; this is not a validated landslide model.
