@echo off
REM PDF OCR Metadata Extractor Runner
REM This batch file sets up and runs the PDF metadata extractor

echo ====================================
echo PDF OCR Metadata Extractor
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found: 
python --version

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo.
echo Checking/Installing required packages...
echo.

REM Install requirements
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install required packages
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ====================================
echo Starting PDF Processing...
echo ====================================
echo.

REM Run the main script
python pdf_ocr_extractor.py

if errorlevel 1 (
    echo.
    echo ERROR: Script execution failed
    echo Check the log file 'pdf_extractor.log' for details
) else (
    echo.
    echo ====================================
    echo Processing completed successfully!
    echo Check the output folder for results
    echo ====================================
)

echo.
echo Press any key to exit...
pause >nul
