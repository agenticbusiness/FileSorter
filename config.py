"""
Configuration file for PDF OCR Metadata Extractor
Modify these settings to customize the extraction behavior
"""

import os
from pathlib import Path

# ====================
# FOLDER CONFIGURATION
# ====================

# Input folder containing PDF files
FOLDER_IN = r"C:\Users\brenn\n8n-docker\upload-to-n8n-Waiting"

# Output folder for CSV files and logs
FOLDER_OUT = r"C:\Users\brenn\n8n-docker\upload-to-n8n-Waiting"

# ====================
# PROCESSING SETTINGS
# ====================

# Maximum number of PDFs to process (0 = process all)
MAX_PDFS = 5

# Maximum pages to scan per PDF (before TOC/Chapter 1)
MAX_PAGES_TO_SCAN = 10

# DPI for OCR image conversion (higher = better quality, slower processing)
OCR_DPI = 300

# OCR language (use tesseract language codes: 'eng', 'fra', 'deu', etc.)
OCR_LANGUAGE = 'eng'

# ====================
# TESSERACT CONFIGURATION
# ====================

# Uncomment and set if Tesseract is not in PATH
# TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_PATH = None

# ====================
# DATA EXTRACTION PATTERNS
# ====================

# Keywords to identify Table of Contents or Chapter beginnings
TOC_KEYWORDS = [
    'table of contents',
    'contents',
    'chapter 1',
    'chapter one',
    'introduction',
    'preface',
    'foreword',
    'chapter i'
]

# Regular expression patterns for data extraction
REGEX_PATTERNS = {
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phone': r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
    'url': r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
    'company_name': r'(?:Company|Corporation|Corp|Inc|LLC|Ltd|Limited)[\s\S]*?(?=\n|\r|$)',
    'address': r'\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)',
    'city_state_zip': r'([A-Za-z\s]+),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)',
    'linkedin': r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+/?',
    'job_title': r'(?:CEO|CTO|CFO|President|Vice President|VP|Director|Manager|Coordinator|Specialist|Engineer|Developer|Analyst)'
}

# ====================
# OUTPUT CONFIGURATION
# ====================

# CSV field headers for company records
COMPANY_HEADERS = [
    'Company_Name
