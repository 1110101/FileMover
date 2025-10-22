# FileMover

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/1110101/FileMover/releases)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

<div align="center">
  
### 🌐 [**Visit Website**](https://1110101.github.io/FileMover/) | 📦 [**Download**](https://github.com/1110101/FileMover/releases)

</div>

> ⚠️ **ALPHA VERSION - WORK IN PROGRESS**  
> This software is in early development and only tested by the author. Use at your own risk. Backup important files before use.

A Windows system tray application that automatically organizes your downloads folder. Files are moved to designated folders based on their extensions after a configurable delay.

**Full Disclosure: Core logic self coded, all other stuff like GUI, Systray, Registry was vibe coded with gemini and cursor**

---

**🇩🇪 Für deutschsprachige Nutzer:** FileMover organisiert automatisch deinen Download-Ordner. PDFs, Bilder, Videos und andere Dateien werden nach einer konfigurierbaren Wartezeit automatisch in die richtigen Ordner verschoben. Die App läuft unsichtbar im System Tray.

---

## Description

**Primary Use Case: Downloads Folder Management**

Your downloads folder gets messy fast. FileMover was specifically built to solve this problem by automatically sorting incoming files based on their extensions.

**How it works:**
1. A file lands in your downloads folder (e.g., a PDF)
2. FileMover detects it instantly but waits (e.g., 5 minutes)
3. This delay lets you open the file right away without it disappearing
4. After the delay, FileMover automatically moves it to the right folder (e.g., Documents/PDFs)
5. Your downloads folder stays clean without any manual sorting!

**Why the delay?** Right after downloading, you usually want to open the file immediately. The delay ensures you can do that before the file gets moved. It also keeps your browser's download history intact.

While primarily designed for downloads folders, FileMover can monitor any folders you need to keep organized.

## Features

- 🖥️ **System Tray Integration**: Runs invisibly in the background, accessible via system tray icon
- 🚀 **Windows Autostart**: Optionally start automatically with Windows
- 🔄 **Real-Time Monitoring**: Watchdog monitors folders and detects new files instantly
- 🎛️ **Auto-Move Toggle**: Enable/disable automatic moving without deleting rules
- 🧪 **Dry Run Mode**: Test mode to preview what would be moved without actually moving files
- 📁 **Multiple Rules**: Configure as many move rules as needed
- 🎯 **File Filtering**: Filter by file extensions (e.g., `.pdf`, `.jpg`, `.docx`)
- 💾 **Persistent Configuration**: All settings stored in Windows Registry
- ⚡ **Manual Execution**: "Move Now" - immediate moving without wait time
- 🔒 **File Lock Check**: Prevents moving files that are still in use

## Requirements

- Windows Operating System (Windows 10 or higher recommended)

## Installation

### Option 1: Installer (Recommended)

**No Python or dependencies needed!**

1. Go to [Releases](https://github.com/1110101/FileMover/releases)
2. Download the latest `FileMover-*-Setup.exe` installer
3. Run the installer and follow the setup wizard
4. Features:
   - Automatic uninstaller
   - Start menu shortcuts
   - Optional desktop icon
   - Optional Windows autostart

**Note:** Windows SmartScreen may show a warning because the app is not code-signed (certificates cost $70-800/year). Click "More info" → "Run anyway". This is normal for open-source software.

### Option 2: Standalone Executable

**Portable version, no installation needed!**

1. Go to [Releases](https://github.com/1110101/FileMover/releases)
2. Download `FileMover.exe`
3. Run the `.exe` directly - done! 🎉

The application will start immediately in the system tray.

### Option 3: From Source (For Developers)

If you want to modify the code or build it yourself:

**Requirements:**
- Python 3.7 or higher

**Installation:**
```bash
git clone https://github.com/1110101/FileMover.git
cd FileMover
pip install -r requirements.txt
```

## Usage

### Starting the Application

**With the installer:**
```
Use the Start Menu shortcut or desktop icon
```

**With the standalone .exe:**
```
Double-click FileMover.exe
```

**From Source (Developers):**
```bash
python move.py
```

The app starts in the system tray (bottom right of taskbar). Click the icon for options.

### System Tray Menu

- **Open**: Opens the configuration window (alternatively: double-click on icon)
- **Quit**: Closes the application completely

### Configuration

1. **Double-click on system tray icon** or right-click → "Open"
2. In the configuration window:

#### Creating a New Rule

1. **Source Folder**: Select the source folder to monitor
2. **Target Folder**: Select the target folder where files should be moved
3. **File Extensions**: Enter file extensions (comma-separated, e.g., `.pdf, .jpg, .png`)
4. Click **"Add Rule"**

#### Settings & Actions

- **Wait Time**: Set how long to wait after file detection before moving (1-60 minutes)
  - Click **"Update"** to save
- **Auto-Move Toggle**: Enable/disable automatic moving
  - 🟢 Green = Active, files will be moved automatically
  - 🔴 Red = Inactive, files will only be queued but not moved
- **Autostart Toggle**: Enable/disable Windows autostart
  - ✓ ON = App starts with Windows
  - OFF = Manual start required

#### Actions

- **Dry Run**: Enable this mode for test runs (shows what would happen without moving files)
- **Show Waiting Files**: Display all files currently in the queue
- **Move Now**: Move all waiting files immediately (ignores timer)

#### Editing a Rule

- Double-click on a rule in the list to load it for editing

#### Deleting a Rule

- Select a rule and click **"Remove Selected"**

### Closing the GUI

Closing the window does NOT quit the app - it continues running in the system tray. To completely quit the app: Right-click on system tray icon → "Quit"

## Typical Downloads Folder Setup

**Rule 1 - PDFs:**
- Source: `C:/Users/YourName/Downloads`
- Target: `D:/Documents/PDFs`
- Extensions: `.pdf`

**Rule 2 - Images:**
- Source: `C:/Users/YourName/Downloads`
- Target: `D:/Pictures`
- Extensions: `.jpg, .jpeg, .png, .heic`

**Rule 3 - Videos:**
- Source: `C:/Users/YourName/Downloads`
- Target: `D:/Videos`
- Extensions: `.mp4, .mkv, .avi`

**Rule 4 - Archives:**
- Source: `C:/Users/YourName/Downloads`
- Target: `D:/Downloads/Archives`
- Extensions: `.zip, .rar, .7z, .tar`

**Rule 5 - Executables:**
- Source: `C:/Users/YourName/Downloads`
- Target: `D:/Software`
- Extensions: `.exe, .msi`

**Delay Setting:** 5 minutes (recommended)

**Result:** Your downloads folder automatically stays clean. Every file type goes to its designated location after you've had time to open it!

## Building Yourself (For Developers)

### Local Build

**Quick build for testing:**
```bash
build.bat
```

**Manual build:**
```bash
pip install -r requirements.txt
pyinstaller move.spec
```

The `.exe` will be created in the `dist/` folder.

### Building the Installer

**Requirements:**
- [Inno Setup 6](https://jrsoftware.org/isinfo.php) installed

**Steps:**
```bash
# 1. Build the executable
build.bat

# 2. Compile the installer
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

The installer will be created in `installer_output/`.

### Automated Builds

The project uses GitHub Actions to automatically build both the standalone executable and installer for every release:
- Triggered on Git tags (e.g., `v1.0.0`)
- Builds are published to GitHub Releases
- No need to commit `dist/` or `build/` folders

**To create a new release:**
```bash
git tag v1.0.1
git push origin v1.0.1
```

GitHub Actions will automatically build and publish the release.

## Configuration & Data Storage

Configuration is stored persistently in the Windows Registry:

**Settings** (`HKEY_CURRENT_USER\Software\FileMover\Config`):
- `move_rules` - All move rules
- `delay_minutes` - Wait time in minutes
- `auto_move_enabled` - Auto-Move toggle status

**Autostart** (`HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`):
- `FileMover` - Application path (when autostart is enabled)

**Crash Logs**: `filemover_crash.log` in the program directory

## Technical Details

- **GUI**: tkinter
- **System Tray**: pystray
- **Icons**: Pillow (PIL)
- **File Monitoring**: watchdog
- **Queue System**: Threading with individual timers per file
- **Storage**: Windows Registry (winreg)
- **Build**: PyInstaller

## Architecture

```
move.py          - Main entry point, system tray integration
gui.py           - GUI components (tkinter)
file_manager.py  - FileQueueManager, FileEventHandler, MoveRule
config.py        - Registry operations, configuration management
```

## Dependencies

- `watchdog` - File system monitoring
- `pystray` - System tray integration
- `Pillow` - Icon creation
- `tkinter` - GUI (included with Python)

## License

This project is licensed under the MIT License.

## Notes

- This application was developed for Windows
- Ensure you have write permissions for both source and target folders
- When using network drives, monitoring may be slower
- Again, almost anything was (painstakingly) vibe coded, but manually reviewed. But I'm not a python dev.

