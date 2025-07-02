@echo off
REM Tesseract OCR Setup Script
REM This script helps install Tesseract OCR for Windows

echo ====================================
echo Tesseract OCR Setup
echo ====================================
echo.

echo This script will help you set up Tesseract OCR for the PDF extractor.
echo.
echo IMPORTANT: You need to manually download and install Tesseract from:
echo https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo After installation, you may need to add Tesseract to your PATH or
echo modify the pdf_ocr_extractor.py file to specify the Tesseract path.
echo.

REM Check if Tesseract is already installed
tesseract --version >nul 2>&1
if not errorlevel 1 (
    echo Tesseract is already installed:
    tesseract --version
    echo.
    echo You're ready to run the PDF extractor!
    goto :end
)

echo Tesseract not found in PATH.
echo.
echo Please follow these steps:
echo 1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
echo 2. Run the installer (recommended: install to C:\Program Files\Tesseract-OCR)
echo 3. Add Tesseract to your system PATH, or
echo 4. Update the pytesseract.pytesseract.tesseract_cmd variable in the Python script
echo.
echo Example for step 4 - add this line to pdf_ocr_extractor.py after imports:
echo pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
echo.

:end
echo Press any key to continue...
pause >nul
