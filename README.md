# FileMover

[![Version](https://img.shields.io/badge/version-1.1.2-blue.svg)](https://github.com/1110101/FileMover/releases)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> 🚧 **Work in Progress** • Mostly AI Vibe Coded

An automated Windows system tray application that keeps your downloads folder organized. FileMover monitors incoming downloads and automatically sorts files into designated target folders based on file extensions after a configurable wait time.

🇩🇪 **Auf Deutsch:** Eine Windows-Systray-Anwendung zum automatischen Sortieren und Verschieben von Dateien basierend auf Dateiendungen mit konfigurierbarer Verzögerung.

---

## 🎯 Why This Exists

I vibe coded this for me, as there was no other tool with that feature set. It works, the code is probably ugly, but we have 2026.

---

## 💡 How It Works

1. **File Detection:** FileMover instantly detects new files in your downloads or any monitored folder.
2. **Configurable Wait Time:** Instead of moving files instantly, FileMover waits a set delay such as 5 minutes so you can open or view downloaded files immediately without them disappearing.
3. **Automatic Sorting:** Once the timer expires, files are moved automatically to your configured target folders like Documents, Pictures, or Software.

---

## ✨ Features

- 🖥️ **System Tray Integration:** Runs quietly in the background with quick tray access.
- 🔄 **Real-Time Monitoring:** Uses watchdog for real-time filesystem change detection.
- 🟢 **AutoMove & Test Run:** Toggle automatic moving on or off or run test mode before moving files.
- ⏳ **Flexible Wait Timers:** Set custom delay times from 1 to 60 minutes per file.
- 📁 **Multi-Rule Support:** Configure separate source and target rules with custom extension filters.
- 🔒 **File Lock & Safety Checks:** Skips locked files currently in use and prevents identical source and target loops.
- 🚀 **Windows Autostart:** Optional autostart with Windows startup.
- 💾 **Registry Storage:** All settings are stored natively in HKEY_CURRENT_USER\Software\FileMover\Config.

---

## 📦 Installation

### Option 1: Installer
Download `FileMover-1.1.2-Setup.exe` from [Releases](https://github.com/1110101/FileMover/releases) for a complete setup with Start Menu shortcuts and uninstaller support.

### Option 2: Portable Executable
Download `FileMover.exe` from [Releases](https://github.com/1110101/FileMover/releases) to run directly without installation.

### Option 3: Building from Source
```bash
# Clone the repository
git clone https://github.com/1110101/FileMover.git
cd FileMover

# Run with uv
uv run move.py

# Or install standard dependencies & run
pip install -r requirements.txt
python move.py
```

---

## 🧪 Running Tests

FileMover includes a comprehensive integration test suite running on Python 3.13 / `uv`:

```bash
uv run tests/test_integration.py
```

---

## 📄 License

Distributed under the [MIT License](LICENSE).
