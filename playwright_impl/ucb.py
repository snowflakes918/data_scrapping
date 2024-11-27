import pandas as pd
from playwright.sync_api import sync_playwright
import re


def decode_cf_email(encoded_email):
    """Decode Cloudflare obfuscated email."""
    r = int(encoded_email[:2], 16)
    email = ''.join([chr(int(encoded_email[i:i + 2], 16) ^ r) for i in range(2, len(encoded_email), 2)])
    return email


def safe_text_content(page, selector, default='N/A'):
    """Safely extract text content from a selector, returning a default value if not found."""
    try:
        element = page.query_selector(selector)
        if element:
            return element.text_content().strip()
    except Exception as e:
        print(f"Error extracting content for selector {selector}: {e}")
    return default


def scrape_uc_berkeley_directory(file_path):
    df = pd.read_csv(file_path)

    if 'first name' not in df.columns or 'last name' not in df.columns:
        raise ValueError("Excel file must contain 'first name' and 'last name' columns")

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for index, row in df.iterrows():
            first_name = row['first name']
            last_name = row['last name']

            # Construct the search URL
            search_url = f"https://www.berkeley.edu/directory/?search-term={first_name}+{last_name}"
            page.goto(search_url)

            try:
                no_results_selector = 'p:has-text("No results were found for your search.")'
                if page.query_selector(no_results_selector):
                    print(f"No results found for {first_name} {last_name}")
                    results.append({
                        'First Name': first_name,
                        'Last Name': last_name,
                        'Name': 'N/A',
                        'Title': 'N/A',
                        'Address': 'N/A',
                        'Email': 'N/A',
                        'Phone': 'N/A',
                        'Department': 'N/A',
                        'UID': 'N/A'
                    })
                    continue

                multiple_result_selector = 'h2:has-text("results for")'
                if page.query_selector(multiple_result_selector):
                    print(f"Multiple results found for {first_name} {last_name}")
                    results.append({
                        'First Name': first_name,
                        'Last Name': last_name,
                        'Name': 'Multiple Results !!!',
                        'Title': 'N/A',
                        'Address': 'N/A',
                        'Email': 'N/A',
                        'Phone': 'N/A',
                        'Department': 'N/A',
                        'UID': 'N/A'
                    })
                    continue


                # Wait for the results page to load
                # page.wait_for_selector('directory-search-result', timeout=5000)

                # Safely extract information
                name = safe_text_content(page, 'directory-search-result h2')
                title = safe_text_content(page, 'dt:has-text("Title") + dd')
                address = safe_text_content(page, 'dt:has-text("Address") + dd', 'N/A').replace('<br>', ', ')
                department = safe_text_content(page, 'dt:has-text("Home department") + dd')
                uid = safe_text_content(page, 'dt:has-text("UID") + dd')
                phone = safe_text_content(page, 'dt:has-text("Telephone") + dd a')

                try:
                    encoded_email = page.get_attribute('span.__cf_email__', 'data-cfemail')
                    email = decode_cf_email(encoded_email)
                except Exception:
                    email = 'N/A'

                result = {
                    'First Name': first_name,
                    'Last Name': last_name,
                    'Name': name,
                    'Title': title,
                    'Address': address,
                    'Email': email,
                    'Phone': phone,
                    'Department': department,
                    'UID': uid
                }
                results.append(result)
                print(f"{result} has been processed!")

            except Exception as e:
                print(f"Failed to extract data for {first_name} {last_name}: {e}")
                results.append({
                    'First Name': first_name,
                    'Last Name': last_name,
                    'Name': 'N/A',
                    'Title': 'N/A',
                    'Address': 'N/A',
                    'Email': 'N/A',
                    'Phone': 'N/A',
                    'Department': 'N/A',
                    'UID': 'N/A'
                })

        browser.close()

    return pd.DataFrame(results)


if __name__ == "__main__":
    excel_file_path = '../data/data_to_scrap - Berkeley.csv'

    scraped_data_df = scrape_uc_berkeley_directory(excel_file_path)

    scraped_data_df.to_excel('../result/ucb_staff_data.xlsx', index=False)
    print("Scraping complete. Data saved to ucb_staff_data.xlsx")
