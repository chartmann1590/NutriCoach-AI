# NutriCoach Mobile App (Flutter)

This document covers the NutriCoach Flutter mobile app: features, installation, configuration, and manual build steps for Android, iOS, Web, and Windows.

## Overview

- Tech stack: Flutter (Dart), platforms: Android, iOS, Web, Windows.
- Path: `nutrition_ai_mobile/`
- Purpose: Client for the NutriCoach server (Flask).
- Server dependency: Connects to the NutriCoach backend (Docker default: `http://localhost:5001`).

## Current Features

- Authentication: Register and login.
- Server Configuration: Set API base URL on first launch (or via Server Setup screen).
- Dashboard: Overview and quick links.
- Food Search: Query foods via server API.
- Manual Food Entry: Create food logs (posts to `/api/logs`).

Notes:
- Photo logging and barcode scanning are not yet implemented; use manual entry and search.

## Prerequisites

- Flutter SDK (3.x recommended): https://flutter.dev/docs/get-started/install
- Platform toolchains (Android Studio, Xcode, or Windows Desktop toolchain)
- Running NutriCoach server (Docker):
  - `docker compose up -d`
  - App: `http://localhost:5001`
  - API Docs: `http://localhost:5001/api/docs`

## Configuration

- Use an API base URL reachable by your device/emulator:
  - Physical device: `http://<your-computer-LAN-ip>:5001` (e.g., `http://192.168.1.20:5001`)
  - Android emulator: `http://10.0.2.2:5001`
  - iOS simulator: `http://localhost:5001` (if server runs on same Mac)

## Installation & Usage

### Android (Debug)
```bash
cd nutrition_ai_mobile
flutter pub get
flutter run -d android
```

### iOS (Debug)
```bash
cd nutrition_ai_mobile
flutter pub get
flutter run -d ios
```

### Web (Debug)
```bash
cd nutrition_ai_mobile
flutter pub get
flutter run -d chrome --web-port 5173
```

### Windows (Debug)
```bash
cd nutrition_ai_mobile
flutter pub get
flutter run -d windows
```

## Manual Build (Release)

### Android APK
```bash
cd nutrition_ai_mobile
flutter pub get
flutter build apk --release
# Output: build/app/outputs/flutter-apk/app-release.apk
```

### Android App Bundle
```bash
flutter build appbundle --release
# Output: build/app/outputs/bundle/release/app-release.aab
```

### iOS (Archive)
```bash
cd nutrition_ai_mobile
flutter pub get
flutter build ios --release
# Then open ios/Runner.xcworkspace in Xcode and Archive
```

### Web
```bash
cd nutrition_ai_mobile
flutter pub get
flutter build web --release
# Output: build/web/
```

### Windows
```bash
cd nutrition_ai_mobile
flutter pub get
flutter build windows --release
# Output: build/windows/runner/Release/
```

## App Structure

```
nutrition_ai_mobile/
├── lib/
│   ├── main.dart
│   ├── models/
│   ├── screens/
│   ├── services/
│   ├── widgets/
│   └── utils/
├── android/ ios/ windows/ web/
├── pubspec.yaml
└── README.md
```

## Connecting to the Server

- API base URL must point to the Flask server root (client prefixes `/api`).
- Examples:
  - Local Docker: `http://localhost:5001`
  - Android Emulator: `http://10.0.2.2:5001`
  - Physical device: `http://<LAN-ip>:5001`

## Troubleshooting

- 401 or redirects: Log in via the mobile app; ensure server is reachable.
- Connection errors: Verify server runs and network paths are correct.
- Web build CORS: Configure hosting/reverse proxy to allow requests to the server origin.
- SSL: For production, serve the backend behind HTTPS and configure the app base URL accordingly.

## Roadmap

- Photo logging and barcode scanning.
- Offline caching and synchronization.
- Notifications and reminders.

---

Server references:
- App: http://localhost:5001
- Swagger UI: http://localhost:5001/api/docs
- OpenAPI: http://localhost:5001/openapi.yaml
