import os
import re
import time

import pandas as pd
from playwright.sync_api import sync_playwright

SEARCH_URL = "https://uaw4811.laborbase.org/locationsdataentry/building/42"
USERNAME = "siwei.huang@uc-uaw.org"
PASSWORD = "Elves-Negligent-Footsore5"

test_data = pd.read_csv('/Users/huangdavid/Downloads/Workers who are supervisors and left UC - Left UC since 2nd July.csv')


def extract_first_digit(room_number):
    if ' ' in room_number or ',' in room_number:
        return '0'
    match = re.search(r'\d', room_number)
    return match.group(0) if match else "0"


def print_page_html():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://uaw4811.laborbase.org/")

        # Fill in login credentials
        page.fill("#identifier-field", USERNAME)
        page.fill("#password-field", PASSWORD)

        # Submit the login form (if there's a login button, find its selector and click it)
        page.click(".cl-formButtonPrimary")

        # Wait for page to be idle before proceeding
        # page.wait_for_load_state("networkidle")

        # Wait for login to complete and redirect to data entry page
        page.wait_for_selector("text=Person Data Entry")
        page.click("text=Person Data Entry")

        for index, row in test_data.iterrows():
            # get the data out of csv file
            building_name = row['PERSON ID']
            campus_name = row['Campus']

            dropdown_items = page.query_selector_all('#person-id')
            dropdown_items[1].click()
            page.click("")