# Changelog

All notable changes to FileMover will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-13

### Added
- 🖥️ System tray integration for background operation
- ⏱️ Configurable delay-based file moving with timer per file
- 🚀 Windows autostart functionality
- 🔄 Real-time folder monitoring with watchdog
- 🎛️ Auto-Move toggle to enable/disable automatic moving
- 🧪 Dry Run mode for testing without moving files
- 📁 Multiple move rules with file extension filtering
- 💾 Persistent configuration in Windows Registry
- 📝 Activity log in GUI
- ⚡ Manual "Move Now" function for immediate moving
- 🔒 File lock checking to prevent moving files in use
- 📐 Resizable GUI with expandable lists and logs
- 🐛 Automatic crash logging for debugging
- 🎨 Modern UI with color-coded status messages
- 📊 Queue status display for waiting files
- 🏗️ PyInstaller build script for creating standalone .exe
- 📚 Comprehensive documentation (README, QUICKSTART)

### Technical
- Thread-safe architecture with tkinter in main thread and pystray in background thread
- Flag-based GUI control for cross-thread communication
- Registry-based configuration storage
- Individual timers for each queued file
- DPI-aware GUI for high-resolution displays
- Comprehensive error handling with user feedback

### Security
- Registry access validation on startup
- File lock checking before moving
- Safe error handling without data loss

[1.0.0]: https://github.com/1110101/FileMover/releases/tag/v1.0.0

