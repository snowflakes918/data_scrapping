import pandas as pd
import requests
from bs4 import BeautifulSoup
import time


# Function to get contact details from UCSF directory
def get_contact_info_from_directory(name):
    base_url = "https://directory.ucsf.edu/people/search"
    params = {
        'keywords': name
    }
    response = requests.post(base_url, data=params)
    soup = BeautifulSoup(response.text, 'html.parser')

    h2_results = soup.find_all('h2')
    for h2_result in h2_results:
        if h2_result and "results from your search" in h2_result.text.lower():
            return None, None, None, None, None, None, None, True, True

    # Check if the user is in directory
    search_result = soup.find('div', id="search-results")
    if search_result:
        h2_result = search_result.find('h2')
        if h2_result and "your search produced no results" in h2_result.text.lower():
            return None, None, None, None, None, None, None, False, False

    # Extract details assuming only one result
    dir_name_tag = soup.find('h2', class_='displayname')
    directory_name = dir_name_tag.text.strip() if dir_name_tag else None

    email_tag = soup.find('a', href=lambda href: href and "mailto:" in href)
    email = email_tag.get('href').replace('mailto:', '') if email_tag else None

    phone_tag = soup.find('a', href=lambda href: href and "tel:" in href)
    phone = phone_tag.text.strip() if phone_tag else None

    location_tag = soup.find('a', href=lambda href: href and "maps.google.com" in href)
    location = location_tag.text.strip() if location_tag else None

    websites = []
    website_tags = soup.find_all('a', href=lambda href: href and "https" in href and "ucsf" not in href)
    for tag in website_tags:
        if "mailto:" not in tag.get('href') and "tel:" not in tag.get('href') and "maps.google.com" not in tag.get(
                'href'):
            websites.append(tag.get('href'))
    websites = ", ".join(websites) if websites else None

    department_tag = soup.find('a', href=lambda href: href and "/people/search/dept/" in href)
    department = department_tag.text.strip() if department_tag else None

    supervisor_tag = soup.find('div', text=lambda text: text and "Supervisor/PI" in text)
    supervisor = supervisor_tag.find_next_sibling('div').text.strip() if supervisor_tag else None

    return directory_name, email, phone, location, websites, department, supervisor, False, True


# Main function to find contact details using the UCSF directory with rate limiting
def find_contact_info(name):
    while True:
        try:
            directory_name, email, phone, location, websites, department, supervisor, multiple_results, in_directory = get_contact_info_from_directory(
                name)
            return directory_name, email, phone, location, websites, department, supervisor, multiple_results, in_directory
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}. Retrying in 60 seconds...")
            time.sleep(60)  # Wait for 60 seconds before retrying


# Load data
data = pd.read_csv('data/ucsf_staff.csv')

# List to store results
results = []

# Iterate over each name and find contact details with a delay to prevent rate limiting
for index, row in data.iterrows():
    name = row['Name']
    directory_name, email, phone, location, websites, department, supervisor, multiple_results, in_directory = find_contact_info(
        name)

    if not in_directory:
        results.append({
            'Name': name, 'Directory_Name': None, 'Email': None, 'Phone': None, 'Location': None,
            'Websites': None, 'Department': None, 'Supervisor/PI': None, 'Multiple_Results': False,
            'In_Directory': False
        })
        print(f'Processed: {name} is not in the directory')
    elif multiple_results:
        results.append({
            'Name': name, 'Directory_Name': None, 'Email': None, 'Phone': None, 'Location': None,
            'Websites': None, 'Department': None, 'Supervisor/PI': None, 'Multiple_Results': True,
            'In_Directory': True
        })
        print(f"Processed: {name}, Multiple results found")
    else:
        results.append({
            'Name': name, 'Directory_Name': directory_name, 'Email': email, 'Phone': phone, 'Location': location,
            'Websites': websites, 'Department': department, 'Supervisor/PI': supervisor, 'Multiple_Results': False,
            'In_Directory': True
        })
        print(
            f"Processed: {name}, Directory Name: {directory_name}, Email: {email}, Phone: {phone}, Location: {location}, Websites: {websites}, Department: {department}, Supervisor/PI: {supervisor}")
    time.sleep(5)  # Delay between requests to prevent rate limiting

# Convert results to a DataFrame and save to a new CSV file
results_df = pd.DataFrame(results)
results_df.to_csv('ucsf_staff_with_contact_info.csv', index=False)

print("Contact information has been processed and saved to 'ucsf_staff_with_contact_info.csv'.")
