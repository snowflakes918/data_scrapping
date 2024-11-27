import time

from commonUtils.scrape_utils import safe_text_content, safe_attribute_content, apply_transform
import pandas as pd
from playwright.sync_api import sync_playwright


def scrape_directory(config):
    df = pd.read_csv(filepath_or_buffer=config['input_file'])

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
            search_url = config['search_url'].format(first_name=first_name, last_name=last_name)
            page.goto(search_url)

            time.sleep(2)

            try:
                # Check for no results
                if page.query_selector(config['no_results_selector']):
                    print(f"No results for {first_name} {last_name}")
                    results.append({key: 'N/A' for key in config['fields']})
                    continue

                # Check for multiple results
                multiple_results_selector = config.get('multiple_results_selector')
                if multiple_results_selector['type'] == 'text':
                    if page.query_selector(multiple_results_selector['selector']):
                        print(f"Multiple results found for {first_name} {last_name}, skipping.")
                        results.append({key: 'Multiple Results' for key in config['fields']})
                        continue
                elif multiple_results_selector['type'] == 'element':
                    if page.locator(multiple_results_selector['selector']).count() > 0:
                        print(f"Multiple results found for {first_name} {last_name}, skipping.")
                        results.append({key: 'Multiple Results' for key in config['fields']})
                        continue

                # Extract data based on field selectors
                record = {}
                for field, selector in config['fields'].items():
                    if selector['type'] == 'text':
                        record[field] = safe_text_content(page, selector['selector'])
                    elif selector['type'] == 'attribute':
                        script_content = safe_attribute_content(page, selector['selector'], selector['attribute'])
                        record[field] = apply_transform(script_content, selector.get("transform"))

                results.append(record)
                print(f"{record} has been processed!")


            except Exception as e:
                print(f"Error processing {first_name} {last_name}: {e}")
                results.append({key: 'N/A' for key in config['fields']})

        browser.close()

    return pd.DataFrame(results)
