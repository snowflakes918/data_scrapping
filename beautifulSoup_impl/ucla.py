import pandas as pd
import requests
from bs4 import BeautifulSoup
import time


# Function to get contact details from UCLA directory
def get_contact_info_from_directory(name):
    base_url = "https://directory.ucla.edu/search.php"
    params = {
        'searchtype': 'basic',
        'querytype': 'person',
        'q': name
    }
    response = requests.post(base_url, data=params)
    soup = BeautifulSoup(response.text, 'html.parser')

    # TODO: people might use nickname


    # check if the people is in directory
    pexit_tag = soup.find('div', class_='pexit')
    pexit = pexit_tag.text.strip() if pexit_tag else None
    if pexit and 'Your search did not return any results' in pexit:
        return None, None, None, None, None, None, None, False, False

    # Check for multiple results
    page_title_tag = soup.find('p', class_='page-title')
    if page_title_tag and "found" in page_title_tag.text.lower():
        records_found = int(page_title_tag.text.split('found')[1].strip().split()[0])
        if records_found > 1:
            return None, None, None, None, None, None, None, True, True

    # Extract details assuming only one result
    dir_name_tag = soup.find('a', rel='lightbox')
    directory_name = dir_name_tag.text.strip() if dir_name_tag else None

    # change name format from "LastName, FirstName" to "FirstName LastName"
    if directory_name:
        temp = directory_name.split(', ')
        directory_name = temp[1] + ' ' + temp[0]

    email_tag = soup.find('a', href=lambda href: href and "mailto:" in href)
    email = email_tag.get('href').replace('mailto:', '') if email_tag else None
    if email:
        email = email.replace('%40', '@')

    phone_tag = soup.find('nobr')
    phone = phone_tag.text.strip() if phone_tag else None

    location_tag = soup.find('a', href=lambda href: href and "maps.google.com" in href)
    location = location_tag.text.strip() if location_tag else None

    websites = []
    website_tags = soup.find_all('a', href=lambda href: href and "http" in href)
    for tag in website_tags:
        if "mailto:" not in tag.get('href') and "tel:" not in tag.get('href') and "maps.google.com" not in tag.get(
                'href') \
                and ".edu" not in tag.get('href'):
            websites.append(tag.get('href'))
    websites = ", ".join(websites) if websites else None

    department_tag = soup.find('label', text="Department")
    department = department_tag.find_next('span').text.strip() if department_tag else None

    supervisor_tag = soup.find('div', text=lambda text: text and "Supervisor/PI" in text)
    supervisor = supervisor_tag.find_next_sibling('div').text.strip() if supervisor_tag else None

    return directory_name, email, phone, location, websites, department, supervisor, False, True


# Main function to find contact details using the UCLA directory with rate limiting
def find_contact_info(name):
    while True:
        try:
            directory_name, email, phone, location, websites, department, supervisor, multiple_results, in_directory = get_contact_info_from_directory(name)
            return directory_name, email, phone, location, websites, department, supervisor, multiple_results, in_directory
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}. Retrying in 60 seconds...")
            time.sleep(60)  # Wait for 60 seconds before retrying


data = pd.read_csv('../data/ucla_staff.csv')

# List to store results
results = []

# Iterate over each name and find contact details with a delay to prevent rate limiting
for index, row in data.iterrows():
    name = row['Name']
    directory_name, email, phone, location, websites, department, supervisor, multiple_results, in_directory = find_contact_info(name)

    if not in_directory:
        results.append({
            'Name': None, 'Directory_Name': None, 'Email': None, 'Phone': None, 'Location': None,
            'Websites': None, 'Department': None, 'Supervisor/PI': None, 'Multiple_Results': False,
            'in_directory': False
        })
        print(f"Processed: {name}, no result found")
    elif multiple_results:
        results.append({
            'Name': name, 'Directory_Name': None, 'Email': None, 'Phone': None, 'Location': None,
            'Websites': None, 'Department': None, 'Supervisor/PI': None, 'Multiple_Results': True,
            'in_directory': True
        })
        print(f"Processed: {name}, Multiple results found")
    else:
        results.append({
            'Name': name, 'Directory_Name': directory_name, 'Email': email, 'Phone': phone, 'Location': location,
            'Websites': websites, 'Department': department, 'Supervisor/PI': supervisor, 'Multiple_Results': False,
            'In_Directory': True
        })
        print(
            f"Processed: {name}, Directory Name: {directory_name}, Email: {email}, Phone: {phone}, Location: {location}, Websites: {websites}, Department: {department}, Supervisor/PI: {supervisor}, Multiple Result: {multiple_results}, In Directory: {in_directory}")

    time.sleep(5)

# Convert results to a DataFrame and save to a new CSV file
results_df = pd.DataFrame(results)
results_df.to_csv('result/ucla_staff_with_contact_info.csv', index=False)

print("Contact information has been processed and saved to 'ucla_staff_with_contact_info.csv'.")
