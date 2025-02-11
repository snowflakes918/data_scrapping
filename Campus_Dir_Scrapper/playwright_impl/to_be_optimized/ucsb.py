import csv
import time
from playwright.sync_api import sync_playwright

# Change these filenames as needed
INPUT_CSV = "ucsb_names.csv"
OUTPUT_CSV = "output_ucsb.csv"


def read_worker_names(input_csv):
    """Read the worker names from a CSV file.
       Assumes each row has one name.
    """
    names = []
    with open(input_csv, newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:  # skip empty rows
                names.append(row[0].strip())
    return names


def write_results(output_csv, results):
    """Write the search results to a CSV file.
       The header includes: QueryName, ResultName, Department, Phone, Email.
    """
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Write header row
        writer.writerow(["QueryName", "ResultName", "Department", "Phone", "Email"])
        # Write each result row
        writer.writerows(results)


def main():
    worker_names = read_worker_names(INPUT_CSV)
    results = []  # each element will be a list: [query name, result name, department, phone, email]

    with sync_playwright() as p:
        # Launch a headless Chromium browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the UCSB Directory Search page.
        # (This is the page that contains the Faculty and Staff search form.)
        page.goto("https://www.ucsb.edu/directory")

        for query_name in worker_names:
            print(f"Searching for: {query_name}")
            # Clear and fill in the "Name" text field (the selector uses the id "edit-name")
            page.fill("input#edit-name", "")  # clear the field
            page.fill("input#edit-name", query_name)

            # (If you need to clear other fields, you could do so similarly.)
            # Click the Submit button (the button with id "edit-submit")
            page.click("button#edit-submit")

            # Wait for the results to load.
            # You can wait for the table rows to appear.
            try:
                page.wait_for_selector("table tbody tr", timeout=5000)
            except:
                print(f"No results found for {query_name}")

            # Give a short delay (adjust as necessary)
            time.sleep(1)

            # Query all rows in the results table
            rows = page.query_selector_all("table tbody tr")
            if not rows:
                # No results – record this query with a note.
                results.append([query_name, "No results", "", "", ""])
            else:
                # Loop over each row in the table.
                for row in rows:
                    # There should be 4 cells: Name, Primary Department, Phone, Email.
                    tds = row.query_selector_all("td")
                    if len(tds) >= 4:
                        # Extract text from each cell and remove extra whitespace/newlines.
                        result_name = tds[0].inner_text().strip().replace("\n", " ")
                        department = tds[1].inner_text().strip().replace("\n", " ")
                        phone = tds[2].inner_text().strip().replace("\n", " ")
                        email = tds[3].inner_text().strip().replace("\n", " ")
                        results.append([query_name, result_name, department, phone, email])
                    else:
                        results.append([query_name, "Incomplete result", "", "", ""])

            # After processing the results for one query, go back to the search page.
            page.goto("https://www.ucsb.edu/directory")
            time.sleep(1)

        browser.close()

    write_results(OUTPUT_CSV, results)
    print(f"Results written to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
