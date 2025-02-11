import csv
import time
from playwright.sync_api import sync_playwright, TimeoutError


def extract_results(page):
    """
    Extracts all result items from the current search results page.
    For each result, it extracts:
      - result_name (from the persistent info)
      - pronouns (if available)
      - position (the text from the first office span)
      - department (from the anchor next to the office span)
      - office_assignment (if available, from the TableRow-assignment block)
      - email, phone, fax (from the contact table)
      - contact_permalink (from the info actions)
    Returns a list of dictionaries.
    """
    results = []
    # Query for all result blocks on the page
    result_blocks = page.query_selector_all("section.ResultBlock")
    for block in result_blocks:
        try:
            # Get the persistent information (name and pronouns)
            name_el = block.query_selector(".ResultBlock-info-name a")
            result_name = name_el.inner_text().strip() if name_el else ""

            pronouns_el = block.query_selector(".ResultBlock-info-pronouns")
            pronouns = pronouns_el.inner_text().strip() if pronouns_el else ""

            # Initialize variables for details from the optional container
            position = ""
            department = ""
            office_assignment = ""
            email = ""
            phone = ""
            fax = ""
            contact_permalink = ""

            # All the detailed info is in the element with class "ResultBlock-info-optional"
            info_optional = block.query_selector(".ResultBlock-info-optional")
            if info_optional:
                # Within the "info-optional", the office info is in the "ResultBlock-info-general" area.
                # Get the position from the first span that contains the office title.
                office_span = info_optional.query_selector("span.deptTitle.italic.ResultBlock-info-office")
                if office_span:
                    # Remove any trailing comma
                    position = office_span.inner_text().strip().rstrip(",")

                # Next, the department is typically contained in an <a> element
                dept_el = info_optional.query_selector("a.pointer.nohrefstyle.ResultBlock-info-office")
                if dept_el:
                    department = dept_el.inner_text().strip()

                # Optionally, get the office assignment (e.g. building and room) from the assignment row
                office_assignment_el = info_optional.query_selector("div.TableRow-assignment div.TableRow-value")
                if office_assignment_el:
                    office_assignment = office_assignment_el.inner_text().strip()

                # Extract contact details from the contact table
                rows = info_optional.query_selector_all("div.ResultBlock-contactTable .TableRow")
                for row in rows:
                    label_el = row.query_selector("div.TableRow-label")
                    value_el = row.query_selector("div.TableRow-value")
                    if label_el and value_el:
                        label = label_el.inner_text().strip().lower()
                        if "email" in label:
                            a_el = value_el.query_selector("a")
                            email = a_el.inner_text().strip() if a_el else value_el.inner_text().strip()
                        elif "phone" in label:
                            a_el = value_el.query_selector("a")
                            phone = a_el.inner_text().strip() if a_el else value_el.inner_text().strip()
                        elif "fax" in label:
                            fax = value_el.inner_text().strip()

                # Extract the contact permalink from the info actions section
                permalink_el = info_optional.query_selector("a.ResultBlock-info-actions-permalink")
                if permalink_el:
                    href = permalink_el.get_attribute("href")
                    if href:
                        # The link is relative so prepend the base URL.
                        contact_permalink = "https://directory.ucmerced.edu" + href

            results.append({
                "result_name": result_name,
                "pronouns": pronouns,
                "position": position,
                "department": department,
                "office_assignment": office_assignment,
                "email": email,
                "phone": phone,
                "fax": fax,
                "contact_permalink": contact_permalink
            })
        except Exception as e:
            print("Error processing a result block:", e)
    return results


def scrape_worker(page, worker_name):
    """
    Navigates to the UC Merced directory, enters the worker's name,
    submits the search, waits for the results to load, and then
    extracts the details.
    Returns a list of result dictionaries.
    """
    # Navigate to the directory homepage
    page.goto("https://directory.ucmerced.edu/")
    # Wait for the search input field to be available
    page.wait_for_selector("input[name='searchText']")

    # Fill in the search input with the worker's name
    search_input = page.query_selector("input[name='searchText']")
    search_input.fill(worker_name)

    # Click the submit button (here assumed to have id="searchButton")
    page.click("#searchButton")

    # Wait for at least one result block to appear (adjust timeout as needed)
    try:
        page.wait_for_selector("section.ResultBlock", timeout=10000)
    except TimeoutError:
        print(f"No results found for {worker_name}")
        return []

    # Wait a short time for dynamic content to render completely
    time.sleep(2)

    # Extract and return the results
    results = extract_results(page)
    # Record the searched name with each result
    for result in results:
        result["searched_name"] = worker_name
    return results


def main():
    input_csv = "ucm_names.csv"  # CSV file containing worker names (one name per row)
    output_csv = "output_ucm.csv"
    all_results = []

    with sync_playwright() as p:
        # Launch the browser (headless mode; set headless=False to see the browser)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Open the input CSV and process each worker name
        with open(input_csv, newline="", encoding="utf-8") as infile:
            reader = csv.reader(infile)
            # Uncomment the next line if your CSV has a header row
            # next(reader)
            for row in reader:
                if row:
                    worker_name = row[0].strip()
                    if worker_name:
                        print(f"Searching for: {worker_name}")
                        worker_results = scrape_worker(page, worker_name)
                        all_results.extend(worker_results)

        browser.close()

    # Define the output CSV columns
    fieldnames = [
        "searched_name",
        "result_name",
        "pronouns",
        "position",
        "department",
        "office_assignment",
        "email",
        "phone",
        "fax",
        "contact_permalink"
    ]

    # Write the collected results to the output CSV file
    with open(output_csv, "w", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in all_results:
            writer.writerow(result)

    print("Scraping complete. Results saved to", output_csv)


if __name__ == "__main__":
    main()
