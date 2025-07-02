# FileSorter

This project includes a PDF OCR Metadata Extractor designed to extract company and contact information from PDF files. It uses OCR to process scanned documents or PDFs without selectable text and saves the extracted data into CSV files.

## Features

- Extracts text from PDF files, using OCR (Tesseract) when necessary.
- Identifies key information like emails, phone numbers, URLs, addresses.
- Organizes extracted data into company and contact records.
- Saves data into timestamped CSV files.
- Configurable processing options (e.g., max PDFs, pages to scan, OCR settings).

## Change Logging

This system incorporates a change logging mechanism to track modifications made by the PDF OCR Metadata Extractor.

**How it Works:**

- Whenever the extractor creates or updates the company or contact CSV files, a log entry is recorded.
- Each log entry includes:
    - A timestamp (YYYY-MM-DD HH:MM:SS)
    - The full path of the file that was changed
    - A description of the change (e.g., "Created/updated company data with X records.")
- These logs are stored in a file named `change_log.txt` located in the configured output folder (`FOLDER_OUT` in `config.py`).

**Accessing Change History:**

The `change_logger.py` module provides a function `get_change_history(file_path)` which can be used programmatically to retrieve all log entries pertaining to a specific file.

**Purpose:**

This logging provides a traceable history of data generation and modification, which can be useful for:
- Auditing when specific data files were created or updated.
- Understanding the sequence of data processing if multiple runs occur.
- Debugging or identifying when changes to source PDFs might have led to different outputs over time.

It is important to note that this log tracks *when files are written by the script*. It does not version the content of the CSV files themselves. For full version control of the output data, consider using a dedicated version control system like Git for the output directory, or implementing a more sophisticated data versioning strategy.