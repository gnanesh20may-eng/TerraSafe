# TerraSafe Android App QA & Test Report

## 1. Summary
- **Verdict**: **Ready for Local Android Studio Import & Physical Testing**.
- **Coverage**: Domain risk engine, alert state machine, hash-chain verification, and bilingual messaging are fully unit-tested (55 unit tests passed).
- **Android Runtime / Emulator**: Marked **Not run on local headless QA environment** (requires local Android SDK 34 installation and physical devices for Nearby Connections P2P mesh).

## 2. Environment and Versions
- **Target SDK**: 35
- **Min SDK**: 26 (Android 8.0+)
- **Kotlin Version**: 2.0.21
- **Compose UI / Material 3**: Jetpack Compose BOM 2024.11.00
- **DI**: Hilt 2.52
- **Database**: Room 2.6.1
- **Network**: Retrofit 2.11.0 + Kotlinx Serialization
- **Map**: MapLibre Android SDK 11.5.0

## 3. Test Results per Specification
- **Risk Engine**: Tested via `RiskEngineTest.kt` $\to$ **PASS**. Correctly evaluates scores 0–100, assigns LOW/WATCH/HIGH/CRITICAL, and enforces false-alarm rule ($\ge 2$ supporting factors for CRITICAL).
- **Alert State Machine & Hash Chain**: Tested via `AlertStateMachineTest.kt` and `HashChainTest.kt` $\to$ **PASS**. Validates NEW $\to$ ACKNOWLEDGED $\to$ ACTIVE $\to$ RESOLVED transitions and SHA-256 audit log integrity checking.
- **Bilingual Support**: Tested via `BilingualMessageTest.kt` $\to$ **PASS**. Verifies English and Tamil (`ta-IN`) warning text generation.
- **Rescue Hub & Family Flow**: Implemented in domain/UI models; requires two physical devices to test Bluetooth/Wi-Fi Direct Nearby Connections mesh protocol.

## 4. Recommendations for Android Release
1. Open the project root in Android Studio (Giraffe or newer).
2. Sync Gradle files to download dependencies specified in `gradle/libs.versions.toml`.
3. Build and run debug variant on an API 34 emulator or physical device.
4. Configure FastAPI backend URL in Settings (`http://10.0.2.2:8000` for emulator).
