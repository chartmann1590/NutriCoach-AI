# Flutter Android Build Guide

This guide provides complete instructions for building the NutriCoach Flutter mobile app for Android.

## Prerequisites

### 1. Install Flutter SDK

1. Download Flutter SDK from [https://flutter.dev/docs/get-started/install](https://flutter.dev/docs/get-started/install)
2. Extract to a location like `C:\flutter` (avoid paths with spaces)
3. Add Flutter to your system PATH:
   - Windows: Add `C:\flutter\bin` to your PATH environment variable
   - macOS/Linux: Add `export PATH="$PATH:/path/to/flutter/bin"` to your shell profile

### 2. Install Android Development Tools

1. **Install Android Studio** from [https://developer.android.com/studio](https://developer.android.com/studio)
2. **Install Android SDK** through Android Studio:
   - Open Android Studio
   - Go to `File > Settings > Appearance & Behavior > System Settings > Android SDK`
   - Install at least Android API level 31 (Android 12)
3. **Accept Android Licenses**:
   ```bash
   flutter doctor --android-licenses
   ```

### 3. Verify Installation

Run Flutter doctor to check your setup:
```bash
flutter doctor
```

Expected output should show checkmarks for:
- Flutter SDK
- Android toolchain
- Android Studio (optional warning about bundled Java is okay)

## Building the Android APK

### Step 1: Navigate to Flutter Project

```bash
cd nutrition_ai_mobile
```

### Step 2: Get Dependencies

```bash
flutter pub get
```

### Step 3: Build APK

Choose one of the following build options:

#### Option A: Build Universal APK (Recommended)
```bash
flutter build apk
```
- Creates a single APK that works on all Android architectures
- Larger file size (~19MB)
- Located at: `build/app/outputs/flutter-apk/app-release.apk`

#### Option B: Build Split APKs (Smaller Size)
```bash
flutter build apk --split-per-abi
```
- Creates separate APKs for different architectures (arm64-v8a, armeabi-v7a, x86_64)
- Smaller individual file sizes
- Located at: `build/app/outputs/flutter-apk/`

#### Option C: Build Debug APK (Development)
```bash
flutter build apk --debug
```
- Includes debugging information
- Faster build time
- Only use for testing

### Step 4: Install APK

#### Install via ADB (Android Debug Bridge)
```bash
# Enable USB debugging on your Android device first
flutter install

# Or install specific APK file
adb install build/app/outputs/flutter-apk/app-release.apk
```

#### Install via File Transfer
1. Copy the APK file to your Android device
2. Enable "Install from Unknown Sources" in Android Settings
3. Tap the APK file to install

## Troubleshooting

### Common Issues and Solutions

#### 1. "Access is denied" or Permission Errors
**Problem**: File permission issues with `.dart_tool` directory

**Solution**:
```bash
# Clean the project
flutter clean

# Remove problematic directories (Windows)
rmdir /s /q .dart_tool
rmdir /s /q build

# Or run as administrator
# Then rebuild
flutter pub get
flutter build apk
```

#### 2. "Parameter format not correct" Warning
**Problem**: Windows-specific Gradle warning (can be safely ignored)

**Solution**: The build will still complete successfully despite this warning.

#### 3. "Unable to find bundled Java version"
**Problem**: Android Studio Java configuration issue

**Solutions**:
- Update Android Studio to latest version
- Or set JAVA_HOME environment variable to your JDK installation
- Or use Flutter without Android Studio: `flutter build apk --no-android-studio-required`

#### 4. Build Fails with Gradle Error
**Problem**: Gradle build issues

**Solutions**:
```bash
# Navigate to android directory
cd android

# Clean Gradle
./gradlew clean

# Go back and rebuild
cd ..
flutter build apk
```

#### 5. Out of Memory Error
**Problem**: Not enough memory for build process

**Solution**: Add to `android/gradle.properties`:
```properties
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
```

### Alternative Build Methods

#### Using Android Studio
1. Open `nutrition_ai_mobile/android` in Android Studio
2. Select `Build > Build Bundle(s) / APK(s) > Build APK(s)`
3. APK will be generated in `app/build/outputs/apk/release/`

#### Using Gradle Directly
```bash
cd nutrition_ai_mobile/android
./gradlew assembleRelease
```

## Build Configuration

### App Signing (Production)
For production releases, configure app signing in `android/app/build.gradle`:

```gradle
android {
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
        }
    }
}
```

### Build Variants
- **Release**: Optimized, minified APK for production
- **Debug**: Unoptimized APK with debugging enabled
- **Profile**: Performance profiling enabled

## Performance Tips

### Optimizing Build Time
1. **Use Build Cache**:
   ```bash
   flutter build apk --build-cache
   ```

2. **Enable Gradle Daemon**:
   Add to `android/gradle.properties`:
   ```properties
   org.gradle.daemon=true
   org.gradle.parallel=true
   org.gradle.configureondemand=true
   ```

3. **Use Local Properties**:
   Create `android/local.properties` with Android SDK path:
   ```properties
   sdk.dir=C:/Users/YourName/AppData/Local/Android/Sdk
   ```

### Reducing APK Size
1. **Enable Proguard** (already enabled in release builds)
2. **Use Split APKs** for different architectures
3. **Remove Unused Resources**:
   ```gradle
   android {
       buildTypes {
           release {
               shrinkResources true
               minifyEnabled true
           }
       }
   }
   ```

## Testing the APK

### Basic Functionality Test
1. Install APK on Android device/emulator
2. Launch NutriCoach app
3. Test key features:
   - User registration/login
   - Server configuration
   - Food search and logging
   - Photo capture
   - Notifications

### Performance Testing
```bash
# Profile app performance
flutter build apk --profile
flutter run --profile -d <device-id>
```

## Deployment

### Google Play Store
1. Build signed release APK
2. Test thoroughly on multiple devices
3. Upload to Google Play Console
4. Fill out store listing information
5. Submit for review

### Direct Distribution
1. Host APK file on secure server
2. Provide download link to users
3. Include installation instructions
4. Consider using APK signing for security

## Additional Resources

- [Flutter Documentation](https://flutter.dev/docs)
- [Android Developer Guide](https://developer.android.com/guide)
- [Flutter Android Deployment](https://flutter.dev/docs/deployment/android)
- [Troubleshooting Flutter](https://flutter.dev/docs/testing/debugging)

## Support

If you encounter issues not covered in this guide:
1. Check Flutter doctor output: `flutter doctor -v`
2. Review build logs for specific error messages
3. Search Flutter GitHub issues
4. Ask questions on Flutter Discord/Stack Overflow