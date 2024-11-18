import os
import re
import time

import pandas as pd
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError

SEARCH_URL = "https://uaw4811.laborbase.org/"
USERNAME = "siwei.huang@uc-uaw.org"
PASSWORD = "Elves-Negligent-Footsore5"
CAMPUS_OPTIONS = {
    "All": "0",
    "Berkeley": "1",
    "Berkeley Lab": "11",
    "Davis": "3",
    "Irvine": "9",
    "Los Angeles": "4",
    "Merced": "10",
    "Riverside": "5",
    "San Diego": "6",
    "San Francisco": "2",
    "Santa Barbara": "8",
    "Santa Cruz": "7",
    "UCOP": "12"
}

test_data = pd.read_csv(filepath_or_buffer='../data/test_location - main.csv')


def extract_first_digit(room_number):
    if ' ' in room_number or ',' in room_number:
        return '0'
    match = re.search(r'\d', room_number)
    return match.group(0) if match else "0"


def print_page_html():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(SEARCH_URL)

        # Fill in login credentials
        page.fill("#identifier-field", USERNAME)
        page.fill("#password-field", PASSWORD)

        # Submit the login form (if there's a login button, find its selector and click it)
        page.click(".cl-formButtonPrimary")

        # Wait for page to be idle before proceeding
        page.wait_for_load_state("networkidle")

        # Wait for login to complete and redirect to data entry page
        page.wait_for_selector("text=Location Data Entry")
        page.click("text=Location Data Entry")

        for index, row in test_data.iterrows():
            try:
                # get the data out of csv file
                building_name = row['Building']
                campus_name = row['Campus']
                room_number = str(row['Room'])
                if building_name is None:
                    continue

                floor_number = extract_first_digit(room_number)  # Use first digit as floor number

                # Step 3a: Search for the building
                # choose campus first
                if campus_name in CAMPUS_OPTIONS:
                    campus_value = CAMPUS_OPTIONS[campus_name]
                    page.select_option("#person-id", campus_value)

                # input building in the search bar
                page.fill(".MuiInputBase-inputTypeSearch", building_name)
                page.click(f"text={building_name}")

                # Step 3b: Click on the 'ADD' button to add a new room
                page.click(".css-1igheai")

                # Step 3c: Fill in the room details
                page.locator("input[name='room']").fill(room_number)  # Room number
                page.locator("input[name='floor']").fill(floor_number)  # Floor number

                # open the location type dropdown menu
                page.locator("input[name='location_type.location_type']").fill("Office")
                page.click("text=Office")

                time.sleep(1)

                # Step 3d: Save the new room information
                page.wait_for_selector(".MuiSvgIcon-root.MuiSvgIcon-fontSizeMedium.css-fhjkay")
                page.click(".MuiSvgIcon-root.MuiSvgIcon-fontSizeMedium.css-fhjkay")

                # Wait 3 seconds just to be safe
                time.sleep(3)
                print(f"Building {building_name} Room {room_number} has been added")
            except TimeoutError:
                print(f"Timeout error when processing {building_name} {row['Room']} at {campus_name}")
                continue

        browser.close()

# just for test
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
    print_page_html()
