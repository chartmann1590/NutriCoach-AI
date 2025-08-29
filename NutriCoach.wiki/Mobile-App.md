## Mobile App (Flutter)

Client application located at `nutrition_ai_mobile/`.

### Features
- Auth, server config, dashboard, search, manual entry, photo analysis
- Planned: coach chat, analytics, offline, notifications

### Run
```bash
cd nutrition_ai_mobile
flutter pub get
flutter run -d android   # or ios / chrome / windows
```

### Build
```bash
flutter build apk --release
flutter build appbundle --release
flutter build ios --release
flutter build web --release
flutter build windows --release
```

### Configure API Base URL
- Local: `http://localhost:5001`
- Android emulator: `http://10.0.2.2:5001`
- Device: `http://<LAN-IP>:5001`

See `docs/mobile_app.md` for more details.

