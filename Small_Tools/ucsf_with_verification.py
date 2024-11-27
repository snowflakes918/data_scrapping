import pandas as pd
import requests
from bs4 import BeautifulSoup
import time


# Function to get email and phone number from UCSF directory
def get_contact_info_from_directory(name):
    base_url = "https://directory.ucsf.edu/people/search"
    params = {
        'keywords': name
    }
    response = requests.post(base_url, data=params)
    soup = BeautifulSoup(response.text, 'html.parser')

    multi = False

    # Check if there are multiple results
    search_result = soup.find('div', id='search-results')
    result_header = search_result.find('h2')
    if result_header and "results from your search" in result_header.text.lower():
        multi = True

    # Locate all search result

    email_tag = soup.find('a', href=lambda href: href and "mailto:" in href)
    email = email_tag.get('href').replace('mailto:', '') if email_tag else None

    phone_tag = soup.find('a', href=lambda href: href and "tel:" in href)
    phone = phone_tag.text.strip() if phone_tag else None

    return email, phone, multi


# Main function to find email and phone number using the UCSF directory with rate limiting
def find_contact_info(name):
    while True:
        try:
            email, phone, multiple_results = get_contact_info_from_directory(name)
            return email, phone, multiple_results
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}. Retrying in 60 seconds...")
            time.sleep(60)  # Wait for 60 seconds before retrying


# Load your data
data = pd.read_csv('data/ucsf_staff.csv')  # Ensure your CSV has a column 'Name'

# List to store results
results = []

# Iterate over each name and find emails and phone numbers with a delay to prevent rate limiting
for index, row in data.iterrows():
    name = row['Name']
    email, phone, multiple_results = find_contact_info(name)
    if multiple_results:
        results.append({'Name': name, 'Email': None, 'Phone': None, 'Multiple_Results': True})
        print(f"Processed: {name}, Multiple results found")
    else:
        results.append({'Name': name, 'Email': email, 'Phone': phone, 'Multiple_Results': False})
        print(f"Processed: {name}, Email: {email}, Phone: {phone}")
    time.sleep(5)  # Delay between requests to prevent rate limiting

# Convert results to a DataFrame and save to a new CSV file
results_df = pd.DataFrame(results)
results_df.to_csv('ucsf_staff_with_contact_info.csv', index=False)

print("Contact information has been processed and saved to 'ucsf_staff_with_contact_info.csv'.")
