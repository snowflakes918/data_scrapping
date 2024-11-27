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

def main():
    # Load data from CSV
    data = pd.read_csv('../data/ucsf_staff.csv')

    # List to store results
    results = []

    for index, row in data.iterrows():
        name = row['Name']
        directory_name, email, phone, location, websites, department, supervisor, multiple_results, in_directory = get_contact_info_from_directory(
            name)

        result_data = {
            'Name': name,
            'Directory_Name': directory_name,
            'Email': email,
            'Phone': phone,
            'Location': location,
            'Websites': websites,
            'Department': department,
            'Supervisor/PI': supervisor,
            'Multiple_Results': multiple_results,
            'In_Directory': in_directory
        }

        results.append(result_data)
        display_result(result_data)
        time.sleep(1)

    export_to_csv(results, '../result/ucsf_staff_with_contact_info.csv')

def display_result(result):
    if not result['In_Directory']:
        print(f"Processed: {result['Name']}, not in directory")
    elif result['Multiple_Results']:
        print(f"Processed: {result['Name']}, Multiple results found")
    else:
        print(
            f"Processed: {result['Name']}, Directory Name: {result['Directory_Name']}, Email: {result['Email']}, Phone: {result['Phone']}, Location: {result['Location']}, Websites: {result['Websites']}, Department: {result['Department']}, Supervisor/PI: {result['Supervisor/PI']}")


# Function to export results to CSV
def export_to_csv(results, filename):
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False)
    print(f"Data exported to {filename}")


if __name__ == "__main__":
    main()
