#!/usr/bin/env python3
"""
PDF OCR Metadata Extractor
Extracts company and contact information from PDFs using OCR
"""

import os
import sys
import json
import re
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Third-party imports
try:
    import pytesseract
    from PIL import Image
    import pdf2image
    import fitz  # PyMuPDF
    import pandas as pd
    from change_logger import log_change, configure_log_file_path # Import for change logging
    import config # Import config to access CHANGE_LOG_FILE
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Please install required packages with: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_extractor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PDFMetadataExtractor:
    """Main class for extracting metadata from PDFs using OCR"""
    
    def __init__(self, folder_in: str, folder_out: str):
        self.folder_in = Path(folder_in)
        self.folder_out = Path(folder_out)
        self.ensure_folders_exist()
        
        # Company data structure
        self.company_headers = [
            'Company_Name_Location', 'Company_Name', 'Company_MAIN_Phone',
            'Company_Job_Type', 'Company_Street', 'Company_City', 'Company_State',
            'Company_Zip/Postal', 'Company_Country', 'Company_URL', 'Industry',
            'Buying_Teir', 'Billing_HQ?', 'Billing_Company_ID',
            'Billing_Main_Contact_ID (LU)', 'Billing_Main_Contact_Name (LU)',
            'ALL_Company_Contact_Emails', 'ALL_Contact_Names', 'Date_Created',
            'Hist_Company_ID_1', 'Hist_Company_ID_2'
        ]
        
        # Contact data structure
        self.contact_headers = [
            'Contact_Email', 'Contact_Name (First Last)', 'Contact_Phone_Direct',
            'Company_Name_Location', 'Company_ID (LU)', 'Industry (from MASTER Company)',
            'Contact_Greeting_Gender', 'Contact_Job_Type', 'Contact_ALL_Phones_JSON',
            'Contact_Notes', 'LinkedIn_URL', 'Contact_ID', 'Billing_Main_Contact',
            'Hist_Contact_ID_1', 'Hist_Contact_ID_2', 'Date_Created'
        ]
        
        # Regex patterns for data extraction
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            'url': r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
            'company_name': r'(?:Company|Corporation|Corp|Inc|LLC|Ltd|Limited)[\s\S]*?(?=\n|\r|$)',
            'address': r'\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)',
            'city_state_zip': r'([A-Za-z\s]+),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)'
        }
    
    def ensure_folders_exist(self):
        """Create input/output folders if they don't exist"""
        self.folder_in.mkdir(parents=True, exist_ok=True)
        self.folder_out.mkdir(parents=True, exist_ok=True)
        logger.info(f"Input folder: {self.folder_in}")
        logger.info(f"Output folder: {self.folder_out}")
    
    def get_pdf_files(self, limit: int = 5) -> List[Path]:
        """Get the first N PDF files from input folder"""
        pdf_files = list(self.folder_in.glob("*.pdf"))[:limit]
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        return pdf_files
    
    def find_toc_page(self, pdf_path: Path) -> int:
        """Find the page number where Table of Contents or Chapter 1 begins"""
        try:
            doc = fitz.open(pdf_path)
            toc_keywords = [
                'table of contents', 'contents', 'chapter 1', 'chapter one',
                'introduction', 'preface', 'foreword'
            ]
            
            for page_num in range(min(10, doc.page_count)):  # Check first 10 pages
                page = doc[page_num]
                text = page.get_text().lower()
                
                for keyword in toc_keywords:
                    if keyword in text:
                        logger.info(f"Found TOC/Chapter marker '{keyword}' on page {page_num + 1}")
                        doc.close()
                        return page_num
            
            doc.close()
            return min(5, doc.page_count)  # Default to first 5 pages if no TOC found
            
        except Exception as e:
            logger.error(f"Error finding TOC in {pdf_path}: {e}")
            return 5
    
    def extract_text_from_pdf_pages(self, pdf_path: Path, max_page: int) -> str:
        """Extract text from PDF pages using OCR"""
        try:
            # First try to extract text directly from PDF
            doc = fitz.open(pdf_path)
            extracted_text = ""
            
            for page_num in range(min(max_page, doc.page_count)):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():  # If text is extractable
                    extracted_text += text + "\n"
                else:  # If no text, use OCR
                    logger.info(f"Using OCR for page {page_num + 1} of {pdf_path.name}")
                    extracted_text += self.ocr_page(pdf_path, page_num)
            
            doc.close()
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def ocr_page(self, pdf_path: Path, page_num: int) -> str:
        """Perform OCR on a specific page"""
        try:
            # Convert PDF page to image
            images = pdf2image.convert_from_path(
                pdf_path, 
                first_page=page_num + 1, 
                last_page=page_num + 1,
                dpi=300
            )
            
            if images:
                # Perform OCR
                text = pytesseract.image_to_string(images[0], lang='eng')
                return text
            
        except Exception as e:
            logger.error(f"OCR error for page {page_num + 1} of {pdf_path}: {e}")
        
        return ""
    
    def extract_data_patterns(self, text: str) -> Dict:
        """Extract structured data from text using regex patterns"""
        data = {
            'emails': [],
            'phones': [],
            'urls': [],
            'addresses': [],
            'city_state_zip': []
        }
        
        # Extract emails
        emails = re.findall(self.patterns['email'], text, re.IGNORECASE)
        data['emails'] = list(set(emails))  # Remove duplicates
        
        # Extract phone numbers
        phones = re.findall(self.patterns['phone'], text)
        data['phones'] = [f"({area}){prefix}-{number}" for area, prefix, number in phones]
        
        # Extract URLs
        urls = re.findall(self.patterns['url'], text, re.IGNORECASE)
        data['urls'] = list(set(urls))
        
        # Extract addresses
        addresses = re.findall(self.patterns['address'], text, re.IGNORECASE)
        data['addresses'] = addresses
        
        # Extract city, state, zip
        city_state_zip = re.findall(self.patterns['city_state_zip'], text)
        data['city_state_zip'] = city_state_zip
        
        return data
    
    def create_company_record(self, pdf_path: Path, extracted_data: Dict) -> Dict:
        """Create a company record from extracted data"""
        record = {header: '' for header in self.company_headers}
        
        # Fill in available data
        record['Company_Name'] = pdf_path.stem  # Use filename as default company name
        record['Company_MAIN_Phone'] = extracted_data['phones'][0] if extracted_data['phones'] else ''
        record['Company_URL'] = extracted_data['urls'][0] if extracted_data['urls'] else ''
        record['ALL_Company_Contact_Emails'] = '; '.join(extracted_data['emails'])
        record['Date_Created'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Parse address information
        if extracted_data['addresses']:
            record['Company_Street'] = extracted_data['addresses'][0]
        
        if extracted_data['city_state_zip']:
            city, state, zip_code = extracted_data['city_state_zip'][0]
            record['Company_City'] = city.strip()
            record['Company_State'] = state.strip()
            record['Company_Zip/Postal'] = zip_code.strip()
        
        # Create combined name and location
        location_parts = [record['Company_City'], record['Company_State']]
        location = ', '.join([part for part in location_parts if part])
        record['Company_Name_Location'] = f"{record['Company_Name']} - {location}" if location else record['Company_Name']
        
        return record
    
    def create_contact_records(self, pdf_path: Path, extracted_data: Dict, company_record: Dict) -> List[Dict]:
        """Create contact records from extracted data"""
        contacts = []
        
        # Create a contact for each email found
        for i, email in enumerate(extracted_data['emails']):
            record = {header: '' for header in self.contact_headers}
            
            record['Contact_Email'] = email
            record['Contact_ID'] = f"{pdf_path.stem}_contact_{i+1}"
            record['Company_Name_Location'] = company_record['Company_Name_Location']
            record['Contact_Phone_Direct'] = extracted_data['phones'][i] if i < len(extracted_data['phones']) else ''
            record['Contact_ALL_Phones_JSON'] = json.dumps(extracted_data['phones'])
            record['Date_Created'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            contacts.append(record)
        
        return contacts
    
    def save_to_csv(self, companies: List[Dict], contacts: List[Dict]):
        """Save extracted data to CSV files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save companies
        company_file = self.folder_out / f"companies_{timestamp}.csv"
        with open(company_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.company_headers)
            writer.writeheader()
            writer.writerows(companies)
        log_change(str(company_file), f"Created/updated company data with {len(companies)} records.")
        logger.info(f"Companies saved to: {company_file}")
        
        # Save contacts
        contact_file = self.folder_out / f"contacts_{timestamp}.csv"
        with open(contact_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.contact_headers)
            writer.writeheader()
            writer.writerows(contacts)
        log_change(str(contact_file), f"Created/updated contact data with {len(contacts)} records.")
        logger.info(f"Contacts saved to: {contact_file}")
        
        return company_file, contact_file
    
    def process_pdfs(self, limit: int = 5):
        """Main processing function"""
        logger.info("Starting PDF processing...")
        
        pdf_files = self.get_pdf_files(limit)
        if not pdf_files:
            logger.warning("No PDF files found in input folder")
            return
        
        all_companies = []
        all_contacts = []
        
        for pdf_path in pdf_files:
            logger.info(f"Processing: {pdf_path.name}")
            
            try:
                # Find where to stop scanning
                toc_page = self.find_toc_page(pdf_path)
                
                # Extract text from relevant pages
                text = self.extract_text_from_pdf_pages(pdf_path, toc_page)
                
                if not text.strip():
                    logger.warning(f"No text extracted from {pdf_path.name}")
                    continue
                
                # Extract structured data
                extracted_data = self.extract_data_patterns(text)
                
                # Create records
                company_record = self.create_company_record(pdf_path, extracted_data)
                contact_records = self.create_contact_records(pdf_path, extracted_data, company_record)
                
                all_companies.append(company_record)
                all_contacts.extend(contact_records)
                
                logger.info(f"Extracted {len(contact_records)} contacts from {pdf_path.name}")
                
            except Exception as e:
                logger.error(f"Error processing {pdf_path.name}: {e}")
                continue
        
        # Save results
        if all_companies or all_contacts:
            company_file, contact_file = self.save_to_csv(all_companies, all_contacts)
            logger.info(f"Processing complete! Found {len(all_companies)} companies and {len(all_contacts)} contacts")
        else:
            logger.warning("No data extracted from any PDFs")

def main():
    """Main entry point"""
    # Configuration
    # Use FOLDER_OUT from config.py for consistency
    # FOLDER_IN = r"C:\Users\brenn\n8n-docker\upload-to-n8n-Waiting"
    
    try:
        # Configure the change logger with the path from config.py
        if hasattr(config, 'CHANGE_LOG_FILE'):
            configure_log_file_path(config.CHANGE_LOG_FILE)
        else:
            # Fallback if CHANGE_LOG_FILE is not in config for some reason
            logger.warning("CHANGE_LOG_FILE not found in config.py. Using default log path.")
            # The change_logger will use its internal default or a local file.
            pass

        extractor = PDFMetadataExtractor(config.FOLDER_IN, config.FOLDER_OUT)
        extractor.process_pdfs(limit=config.MAX_PDFS if hasattr(config, 'MAX_PDFS') else 5)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
