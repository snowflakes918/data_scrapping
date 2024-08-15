import pandas as pd
import requests
from bs4 import BeautifulSoup
import time


# Function to get email from UCSD directory
def get_email_from_directory(first_name, last_name):
    base_url = "https://directory.ucsd.edu/search"
    params = {
        'searchtype': 'advanced',
        'querytype': 'person',
        'first': first_name,
        'last': last_name,
    }
    response = requests.get(base_url, params=params)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Locate email address in the search results
    email_tag = soup.find('a', href=lambda href: href and "mailto:" in href)
    email = email_tag.get('href').replace('mailto:', '') if email_tag else None

    return email


# Main function to find email using the UCSD directory with rate limiting
def find_email(name):
    first_name, last_name = name.split()
    while True:
        try:
            email = get_email_from_directory(first_name, last_name)
            return email
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}. Retrying in 60 seconds...")
            time.sleep(60)  # Wait for 60 seconds before retrying


data = pd.read_csv('data/ucsd_staff.csv')

# List to store results
results = []

# Iterate over each name and find emails with a delay to prevent rate limiting

for index, row in data.iterrows():
    try:
        name = row['Name']
        email = find_email(name)
        results.append({'Name': name, 'Email': email})
        print(f"Processed: {name}, Email: {email}")
        time.sleep(5)  # Delay between requests to prevent rate limiting
    except ValueError:
        continue

# Convert results to a DataFrame and save to a new CSV file
results_df = pd.DataFrame(results)
results_df.to_csv('ucsd_staff_with_emails.csv', index=False)

print("Email addresses have been processed and saved to 'ucsd_staff_with_emails.csv'.")
