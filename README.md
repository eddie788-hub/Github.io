# ForensicSignalAPK

Defensive Android BLE forensic signal prototype.

## Features

- Native Android BLE scanning
- Apple / Find My-style manufacturer detection
- Signal strength monitoring
- Range modes: Close, Normal, Wide, Deep
- Profile cards
- Security cards with risk grading
- Local evidence vault
- JSONL append-only event logging
- CSV export
- Chain-of-custody log
- Basic report export

## Build

Open this folder in Android Studio, then run:

```bash
./gradlew assembleDebug
```

APK output:

```text
app/build/outputs/apk/debug/app-debug.apk
```

## Permissions

Android 12+ needs nearby-device Bluetooth permissions.
Location permission may be needed on some devices for BLE scanning.

## Notes

This is a defensive prototype. BLE identifiers can rotate. Battery/status data is heuristic only.
