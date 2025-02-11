import csv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def scrape_results_for_name(search_name, page):
    """
    Given a search name and a Playwright page,
    fill the search form, submit the search, wait for results,
    and return a list of dictionaries with the record details.
    """
    # Fill the search field (the input has id "keyword")
    page.fill("input#keyword", search_name)

    # Click the submit button (the button with value "Search directory")
    page.click("input[type=submit][value='Search directory']")

    # Wait for the results table to appear.
    try:
        page.wait_for_selector("table#dresults", timeout=5000)
    except PlaywrightTimeoutError:
        print(f"No results found for '{search_name}'.")
        return []

    # Find all rows in the table body.
    rows = page.query_selector_all("table#dresults tbody tr")
    results = []
    for row in rows:
        cells = row.query_selector_all("td")
        if len(cells) >= 7:
            # Get text content for each cell.
            # Note that the first cell contains a link with the person's name.
            result_record = {
                "Result Name": cells[0].inner_text().strip(),
                "Phone": cells[1].inner_text().strip(),
                "Email": cells[2].inner_text().strip(),
                "Dept/College": cells[3].inner_text().strip(),
                "Title": cells[4].inner_text().strip(),
                "Affiliation": cells[5].inner_text().strip(),
                "Mail Stop": cells[6].inner_text().strip()
            }
            results.append(result_record)
    return results


def main():
    # List to hold all the records.
    output_records = []

    # Open the CSV with the search names.
    with open("data/input/ucsc_names.csv", "r", encoding="utf-8") as csvfile:
        csv_reader = csv.reader(csvfile)
        # Assume one column per row with the full name.
        names = [row[0].strip() for row in csv_reader if row]

    with sync_playwright() as p:
        # Launch the browser in headless mode.
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for name in names:
            # Go to the directory search page for each name.
            page.goto("https://campusdirectory.ucsc.edu/cd_simple")
            # Wait for the page to be fully loaded.
            page.wait_for_load_state("networkidle")

            # Perform the search and get the results.
            records = scrape_results_for_name(name, page)

            if records:
                # For each record found, add the search name to the record.
                for rec in records:
                    rec["Search Name"] = name
                    output_records.append(rec)
            else:
                # If no record was found, output a record with empty fields.
                output_records.append({
                    "Search Name": name,
                    "Result Name": "",
                    "Phone": "",
                    "Email": "",
                    "Dept/College": "",
                    "Title": "",
                    "Affiliation": "",
                    "Mail Stop": ""
                })

        browser.close()

    # Define the header for the output CSV.
    fieldnames = ["Search Name", "Result Name", "Phone", "Email", "Dept/College", "Title", "Affiliation", "Mail Stop"]
    # Write the collected records to an output CSV file.
    with open("data/output/output.csv", "w", newline='', encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for record in output_records:
            writer.writerow(record)

    print("Scraping complete. Data saved to output.csv.")


if __name__ == '__main__':
    main()
