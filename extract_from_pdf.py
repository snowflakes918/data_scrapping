import pdfplumber
import pandas as pd
import re

# Load the PDF
with pdfplumber.open("data/ucsd_dir.pdf") as pdf:
    text = ""
    for page in pdf.pages:
        text += page.extract_text()

# Define a regular expression pattern to capture all relevant fields, allowing for missing (null) fields
pattern = re.compile(
    r'([A-Z][A-Za-z]+),\s+([A-Z][A-Za-z]+(?: [A-Z]\.)?)\s+'  # Last name, First name (Middle initial optional)
    r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|)\s+'  # Phone (can be empty)
    r'(.*?)\s+'  # Title (non-greedy, so it stops before dept name)
    r'(.*?)\s+'  # Department name
    r'(\d{4})\s+'  # Mail code (always 4 digits)
    r'(.*?)\s+'  # Room (non-greedy)
    r'(.*?)\s+'  # Location
    r'([\w\.-]+@[\w\.-]+)'
)

# Extract all the matches
matches = pattern.findall(text)

# Convert matches to a DataFrame
staff_data = pd.DataFrame(matches, columns=[
    'last_name', 'first_name', 'phone', 'title', 'dept_name', 'mail_code', 'room', 'location', 'email'
])

# Replace empty strings with None (null) to better represent missing data
staff_data.replace('', None, inplace=True)

# Display the extracted data
staff_data.to_excel('result/ucsd_staff_info.xlsx', index=False)