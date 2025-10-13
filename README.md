# FileMover

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/1110101/FileMover/releases)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Windows system tray application for automatic file organization based on file extensions with configurable delay-based moving.

**Full Disclosure: Core logic self coded, all other stuff like GUI, Systray, Registry was vibe coded with gemini and cursor**

---

**🇩🇪 Für deutschsprachige Nutzer:** FileMover ist eine Windows-Anwendung, die automatisch Dateien basierend auf Dateiendungen verschiebt. Die App kann im System Tray laufen und Ordner in Echtzeit überwachen. Haupt-Usecase ist das Verwalten und Organisieren des Downloadordners.

---

## Description

FileMover monitors source folders in real-time and automatically moves files with specific extensions to target folders after a configurable wait time. The application runs in the background in the system tray and offers an optional GUI for configuration.

Mainly written to automatically move files out of a overflowing download folder.

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

### Option 1: Pre-built .exe (Recommended for End Users)

**No Python or installation needed!**

1. Go to [Releases](https://github.com/1110101/FileMover/releases)
2. Download the latest `move.exe`
3. Run the `.exe` directly - done! 🎉

The application will start immediately in the system tray.

### Option 2: From Source (For Developers)

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

**With the .exe:**
```
Double-click move.exe
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

## Example Workflow

1. Source folder: `D:/Downloads`
2. Target folder: `D:/Documents/PDFs`
3. Extensions: `.pdf`
4. Delay: `5` minutes
5. **Result**: When a PDF file appears in Downloads, it will be automatically moved to `D:/Documents/PDFs` after 5 minutes

**Why Delay?** Right after downloading you usually just want to open the file right away. This would be not possible then, also the chrome download history cannot find the file then.

## Building the .exe Yourself (Optional)

If you want to build the `.exe` yourself:

**Automatically with Build Script:**
```bash
build.bat
```

**Manually:**
```bash
pip install -r requirements.txt
pyinstaller move.spec
```

The `.exe` will be created in the `dist/` folder.

**Note:** Usually you can simply use the pre-built `.exe` from the [Releases](https://github.com/1110101/FileMover/releases)!

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

