@echo off
color 0A
title MuDream Collection Finder - Build Script

echo ========================================
echo  MuDream Collection Finder - Builder
echo ========================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [!] PyInstaller not found. Installing...
    pip install pyinstaller
    echo.
)

echo [*] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec
echo [+] Clean complete!
echo.

echo [*] Building executable...
echo [*] This may take a few minutes...
echo.

pyinstaller --onefile ^
    --windowed ^
    --name "MuDreamCollectionFinder" ^
    --add-data "collection_config.json;." ^
    mudream_collection_finder.py

if errorlevel 1 (
    echo.
    echo [!] Build FAILED! Check errors above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [+] Build SUCCESS!
echo ========================================
echo.
echo Your executable is located at:
echo dist\MuDreamCollectionFinder.exe
echo.
echo File size:
dir dist\MuDreamCollectionFinder.exe | find "MuDreamCollectionFinder.exe"
echo.
echo ========================================

pause
