# AGENTS.md

## Project Overview
Multi-platform 2FA (TOTP) authenticator. Secrets stored locally only, no network communication.

## Directory Structure
- `android/` - Android app (Uni-app Vue 3)
- `windows/` - Windows desktop app (Python + PyQt5)

## Windows Component
- **Entry**: `windows/main.py`
- **Dependencies**: `pip install -r windows/requirements.txt`
- **Build**: Use PyInstaller to package as .exe

## Android Component
- **Framework**: Uni-app (Vue 3) + HBuilderX (not native Android/Gradle)
- **Dependencies**: `cd android && npm install` (only `crypto-js@^4.2.0`)
- **Build**: Requires HBuilderX IDE for Android APK generation
- **Key Code**: `android/utils/totp.js` (custom TOTP implementation)

## Important Notes
- No CI workflows or automated tests
- No lint/typecheck configuration found
- Android app has known ~5 second latency (adjustable in UI)
