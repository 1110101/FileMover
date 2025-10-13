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
echo [1/4] Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/4] Cleaning previous build...
if exist build rmdir /s /q build
if exist dist\move.exe del /q dist\move.exe

echo.
echo [3/4] Building executable with PyInstaller...
pyinstaller move.spec
if errorlevel 1 (
    echo Error: Build failed
    pause
    exit /b 1
)

echo.
echo [4/4] Build complete!
echo.
echo Executable location: dist\move.exe
echo.
echo ========================================
echo   Build Successful!
echo ========================================
pause

