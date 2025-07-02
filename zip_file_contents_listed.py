import zipfile
import os

# Define the paths to the uploaded ZIP files
zip_files = {
    "Siphonic_Ponding_Curves": "/mnt/data/Siphonic Ponding Curves.zip",
    "Siphonic_Dimensional_Drawings": "/mnt/data/Siphonic_Dimensional_Drawings.zip",
    "Siphonic_Spec_Sheets": "/mnt/data/Siphonic_Spec_Sheets.zip"
}

# Extract the contents of each ZIP file and list the filenames
zip_contents = {}
for label, path in zip_files.items():
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_contents[label] = zip_ref.namelist()

zip_contents
