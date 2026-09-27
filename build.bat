@echo off
echo ========================================
echo   FileMover Build Script
echo ========================================
echo.

REM Check for virtual environment and activate if present
if exist ".venv\Scripts\activate.bat" (
    echo Found virtual environment, activating...
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo Found virtual environment, activating...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found, using system Python
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo [1/5] Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/5] Running tests...
python tests\test_integration.py
if errorlevel 1 (
    echo Error: Integration tests failed! Build aborted.
    pause
    exit /b 1
)

echo.
echo [3/5] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist\move.exe del /q dist\move.exe
if exist dist\FileMover.exe del /q dist\FileMover.exe

echo.
echo [4/5] Building executable with PyInstaller...
pyinstaller move.spec --noconfirm
if errorlevel 1 (
    echo Error: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo Standalone executable created: dist\FileMover.exe

REM Locate Inno Setup Compiler
set "ISCC_PATH="
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC_PATH=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if not defined ISCC_PATH if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not defined ISCC_PATH if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"

if defined ISCC_PATH (
    echo.
    echo [5/5] Building installer with Inno Setup...
    "%ISCC_PATH%" installer.iss
    if errorlevel 1 (
        echo Warning: Installer build failed.
    ) else (
        echo.
        echo Installer created in installer_output\
    )
) else (
    echo.
    echo [5/5] Inno Setup compiler not found. Skipping installer creation.
    echo To build the installer manually, install Inno Setup 6.
)

echo.
echo ========================================
echo   Build Finished!
echo ========================================
pause
