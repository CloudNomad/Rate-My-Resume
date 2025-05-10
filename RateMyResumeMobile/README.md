# Rate My Resume Mobile App

A cross-platform mobile application for analyzing and improving resumes using AI.

## Features

- 📱 Works on both Android and iOS
- 📄 Upload and analyze PDF resumes
- 📊 Get detailed resume scores and feedback
- 💡 Receive improvement suggestions
- 🔍 Industry-specific analysis
- 📤 Share results with others

## Prerequisites

- Node.js (v14 or later)
- npm or yarn
- Expo CLI
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Run on your device:
- Scan the QR code with the Expo Go app (Android) or Camera app (iOS)
- Or press 'a' for Android emulator or 'i' for iOS simulator

## Development

The app is built with:
- React Native
- Expo
- TypeScript
- React Navigation

## Project Structure

```
src/
  ├── screens/          # Screen components
  │   ├── HomeScreen.tsx
  │   ├── AnalysisScreen.tsx
  │   └── ResultsScreen.tsx
  ├── components/       # Reusable components
  ├── navigation/       # Navigation configuration
  ├── services/        # API and other services
  └── utils/           # Utility functions
```

## Building for Production

1. Create an Expo account and log in:
```bash
expo login
```

2. Build for Android:
```bash
expo build:android
```

3. Build for iOS:
```bash
expo build:ios
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
