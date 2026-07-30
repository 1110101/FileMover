# Changelog

All notable changes to FileMover will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-07-30

### Fixed
- **System Tray Quit Action:** Resolved background thread deadlock and Tkinter thread-safety issues during application shutdown.
- **File Lock Timestamp Preservation:** Fixed file lock check (`_is_file_unlocked`) altering `mtime` and causing infinite watchdog trigger loops.

### Added
- **Comprehensive Integration Test Suite:** Added 8 end-to-end automated integration tests in `tests/test_integration.py` running on Python 3.13 / `uv`.
- **Validation:** Added validation preventing identical source and target folder configurations.
- **Extension Normalization:** Extensions without leading dots (e.g. `pdf`) are now automatically normalized to `.pdf`.

### Changed
- **Settings & Actions UI Redesign:** Grouped `Wait Time` setting with `Save` button, renamed `Auto-Move` to `AutoMove`, converted `Dry Run` mode to `Test Run` button, and removed redundant label parentheses.
- **CI/CD Integration:** Registered integration test suite execution in GitHub Actions build workflow.
- **Documentation:** Trimmed AI-generated slop from `README.md` and `index.html` for clearer, conciser documentation.

## [1.0.0] - 2025-10-22

### Added
- System tray integration for background operation
- Configurable delay-based file moving with timer per file
- Windows autostart functionality
- Real-time folder monitoring with watchdog
- Auto-Move toggle to enable/disable automatic moving
- Dry Run mode for testing without moving files
- Multiple move rules with file extension filtering
- Persistent configuration in Windows Registry
- Activity log in GUI
- Manual "Move Now" function for immediate moving
- File lock checking to prevent moving files in use
- Resizable GUI with expandable lists and logs
- Automatic crash logging for debugging
- Modern UI with color-coded status messages
- Queue status display for waiting files
- Windows installer (Inno Setup) with uninstaller
- GitHub Actions automated build pipeline
- Start menu shortcuts and optional desktop icon
- Registry cleanup option during uninstallation

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

[1.1.0]: https://github.com/1110101/FileMover/releases/tag/v1.1.0
[1.0.0]: https://github.com/1110101/FileMover/releases/tag/v1.0.0

