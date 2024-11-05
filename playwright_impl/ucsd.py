import re

import pandas as pd
from playwright.sync_api import sync_playwright


def scrape_ucsd_directory_from_excel(file_path):
    df = pd.read_excel(file_path)

    if 'first name' not in df.columns or 'last name' not in df.columns:
        raise ValueError("Excel file must contain 'first name' and 'last name' columns")

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for index, row in df.iterrows():
            first_name = row['first name']
            last_name = row['last name']

            # Construct the search URL using first and last names
            search_url = f"https://itsweb.ucsd.edu/directory/search?last={last_name}&first={first_name}&email=&title=&phone=&fax=&dept2=&mail=&searchType=0"
            try:
                page.goto(search_url)
            except:
                results.append({
                    'First Name': 'N/A',
                    'Last Name': 'N/A',
                    # 'Name': emp_name,
                    # 'Email': email,
                    'Mail Code': 'N/A'
                })
                continue
            page.wait_for_timeout(3000)  # Wait for the page to fully load

            # Try to extract the data with error handling
            # try:
            #     page.wait_for_selector('#empName', timeout=2000)
            #     emp_name = page.text_content('#empName')
            # except:
            #     emp_name = 'N/A'
            #
            # try:
            #     page.wait_for_selector('a[href^="mailto:"]', timeout=2000)
            #     email = page.text_content('a[href^="mailto:"]') or 'N/A'
            # except:
            #     email = 'N/A'

            try:
                page.wait_for_selector('label:has-text("Mail Code") + div', timeout=2000)
                mail_code_raw = page.text_content('label:has-text("Mail Code") + div')
                # Use regex to find the 4-digit mail code in the string
                mail_code_match = re.search(r'\b\d{4}\b', mail_code_raw)
                mail_code = mail_code_match.group(0) if mail_code_match else 'N/A'
            except:
                mail_code = 'N/A'

            person_entry = {
                'First Name': first_name,
                'Last Name': last_name,
                # 'Name': emp_name,
                # 'Email': email,
                'Mail Code': mail_code
            }

            print(person_entry)

            # Append the scraped data to results
            results.append(person_entry)

        browser.close()

    return pd.DataFrame(results)


if __name__ == "__main__":
    # File path to the Excel file with 'first name' and 'last name' columns
    excel_file_path = '../data/ucsd_staff_data.xlsx'

    # Scrape the data
    scraped_data_df = scrape_ucsd_directory_from_excel(excel_file_path)

    # Save the scraped data to a new Excel file
    scraped_data_df.to_excel('../result/ucsd_staff_data_result.xlsx', index=False)
    print("Scraping complete. Data saved to ucsd_staff_data.xlsx")
