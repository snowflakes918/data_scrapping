import pandas as pd
import requests
from bs4 import BeautifulSoup
import time


# Function to get email and phone number from UCLA directory
def get_contact_info_from_directory(name):
    base_url = "https://directory.ucla.edu/search.php"
    params = {
        'searchtype': 'basic',
        'querytype': 'person',
        'q': name
    }
    response = requests.post(base_url, data=params)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate email address in the search results
    email_tag = soup.find('a', href=lambda href: href and "mailto:" in href)
    email = email_tag.get('href').replace('mailto:', '') if email_tag else None

    # Locate phone number in the search results
    phone = None
    phone_tags = soup.find_all('nobr')
    for tag in phone_tags:
        if "310-" in tag.text:
            phone = tag.text.strip().replace('\n', '')
            break

    return email, phone


# Main function to find email and phone number using the UCLA directory with rate limiting
def find_contact_info(name):
    while True:
        try:
            email, phone = get_contact_info_from_directory(name)
            return email, phone
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}. Retrying in 60 seconds...")
            time.sleep(60)  # Wait for 60 seconds before retrying


data = pd.read_csv('data/ucla_staff.csv')

# List to store results
results = []

# Iterate over each name and find emails and phone numbers with a delay to prevent rate limiting
for index, row in data.iterrows():
    name = row['Name']
    email, phone = find_contact_info(name)
    results.append({'Name': name, 'Email': email, 'Phone': phone})
    print(f"Processed: {name}, Email: {email}, Phone: {phone}")
    time.sleep(5)  # Delay between requests to prevent rate limiting

# Convert results to a DataFrame and save to a new CSV file
results_df = pd.DataFrame(results)
results_df.to_csv('ucla_staff_with_contact_info.csv', index=False)

print("Contact information has been processed and saved to 'ucla_staff_with_contact_info.csv'.")
