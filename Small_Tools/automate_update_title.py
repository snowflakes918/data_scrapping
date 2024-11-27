import os
import re
import time

import pandas as pd
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError

SEARCH_URL = "https://uaw4811.laborbase.org/"
USERNAME = "siwei.huang@uc-uaw.org"
PASSWORD = "Elves-Negligent-Footsore5"


def data_pre_process(filepath):
    data = pd.read_csv(filepath_or_buffer=filepath)
    data = data.drop_duplicates('PersonID')
    data.reset_index(drop=True, inplace=True)

    return data


def print_page_html(data):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(SEARCH_URL)

        # Login Process
        page.fill("#identifier-field", USERNAME)
        page.fill("#password-field", PASSWORD)

        page.click(".cl-formButtonPrimary")
        page.wait_for_load_state("networkidle")

        # Wait for login to complete and redirect to person data entry page
        page.wait_for_selector("text=Person Data Entry")
        page.click("text=Person Data Entry")

        for index, row in data.iterrows():
            try:
                # get the data out of csv file
                pid = row['PersonID']
                title = row['In-Unit Title (researched)']

                # fill in personid in search bar
                page.goto(f"https://uaw4811.laborbase.org/persondataentry/employment/{pid}")
                page.wait_for_load_state("networkidle")

                # edit the work title
                page.locator("svg[data-testid='EditSharpIcon']").first.click()

                page.locator("input[name='position_type.job_title']").clear()
                page.fill("input[name='position_type.job_title']", title)
                page.wait_for_selector("ul[role='listbox']", timeout=5000)  # Wait for the dropdown
                # Step 3: Select the first option in the dropdown
                first_option = page.locator("ul[role='listbox'] > li").first
                first_option.click()

                page.click("svg[data-testid='SaveIcon']")

            except TimeoutError as e:
                print(f"Timeout error when processing {pid}: {e}")
                continue

        browser.close()


def open_page_for_inspection():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Open in a visible browser
        page = browser.new_page()
        page.goto("https://uaw4811.laborbase.org/login")  # Navigate to login page

        print(page.content())

        # Wait to manually inspect the page
        input("Press Enter after inspecting the page to close the browser...")

        browser.close()


if __name__ == "__main__":
    # open_page_for_inspection()
    df = data_pre_process('SSAP - Title Unknown Research - Found Titles.csv')
    print_page_html(df)
