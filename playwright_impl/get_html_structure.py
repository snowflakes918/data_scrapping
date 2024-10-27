from playwright.sync_api import sync_playwright


def print_page_html():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # test case
        page.goto(
            "https://itsweb.ucsd.edu/directory/search?last=yang&first=yujing&email=&title=&phone=&fax=&dept2=&mail=&searchType=0")
        page.wait_for_timeout(5000)  # Wait 5 seconds for page to fully load
        name = page.text_content('#empName')

        print(name)
        # print(page.content())  # Print full HTML content
        browser.close()


if __name__ == "__main__":
    print_page_html()
