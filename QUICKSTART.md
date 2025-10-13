# FileMover - Quick Start Guide

## Installation & Launch

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Application
```bash
python move.py
```

The app appears in the system tray (bottom right of the taskbar).

## Getting Started

### 1. Open the GUI
- **Double-click** the FileMover icon in the system tray
- Or: **Right-click** → "Open"

### 2. Set the Delay
- Default is 5 minutes
- Adjust the value (e.g., 1 minute for testing)
- Click **"Update"**

### 3. Add Your First Rule

**Example: Move PDFs from Downloads**

1. **Source Folder**: `C:\Users\YourName\Downloads`
2. **Target Folder**: `C:\Users\YourName\Documents\PDFs`
3. **File Extensions**: `.pdf`
4. Click **"Add Rule"**

### 4. Testing

**Option A: Manual Test**
- Click **"Move Now"** → Files are moved immediately

**Option B: Automatic Test**
- Place a PDF file in the Downloads folder
- Wait for the configured delay time
- The file will be moved automatically

**Check Queue:**
- Click **"Show Waiting Files"** to see pending files

## Enable Autostart

1. Open the GUI
2. Click **"Autostart: OFF"** button to enable
3. FileMover will now start automatically with Windows

## Tips

### Multiple File Types
```
.pdf, .docx, .xlsx, .pptx
```

### Organize Images
- **Source**: `C:\Users\YourName\Downloads`
- **Target**: `C:\Users\YourName\Pictures\FromDownloads`
- **Extensions**: `.jpg, .jpeg, .png, .gif, .webp`

### Organize Videos
- **Source**: `C:\Users\YourName\Downloads`
- **Target**: `C:\Users\YourName\Videos\FromDownloads`
- **Extensions**: `.mp4, .mkv, .avi, .mov`

## Build Executable

```bash
build.bat
```

The `.exe` will be in `dist\move.exe`

## Troubleshooting

**App doesn't appear in system tray:**
- Check if Python process is running (Task Manager)
- Check console output for errors

**Files are not being moved:**
- Verify that the source folder exists
- Check the "Activity Log" in the GUI
- Click "Show Waiting Files" to see queued files

**GUI not responding:**
- Close the window (app continues in tray)
- Reopen via system tray icon

## Quitting the App

**Complete shutdown:**
- **Right-click** on system tray icon
- Click **"Quit"**

**Important:** Closing the GUI window does NOT quit the app! It continues running in the background.

