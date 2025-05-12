from playwright.sync_api import sync_playwright
import os

USERNAME = os.environ["BOOKING_USERNAME"]
PASSWORD = os.environ["BOOKING_PASSWORD"]
URL = os.environ["BOOKING_URL"]
DAY_OF_WEEK = os.environ["BOOKING_DAY_OF_WEEK"]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL)

    page.fill("#forEmail", USERNAME)
    page.fill("#forPassword", PASSWORD)
    page.click("text=CONECTEAZĂ-TE")

    found = False
    while not found:
        page.locator(".slots-message").filter(has_text="Se caută spații disponibile... ").wait_for(state="detached")
        page.wait_for_timeout(500)
        page.click(".calendar-arrow.right-arrow")
        page.locator(".slots-message").filter(has_text="Se caută spații disponibile... ").wait_for(state="detached")
        page.wait_for_timeout(500)
        page.click(".calendar-arrow.right-arrow")
        page.locator(".slots-message").filter(has_text="Se caută spații disponibile... ").wait_for(state="detached")
        page.wait_for_timeout(500)
        page.locator(".day-week").filter(has_text=DAY_OF_WEEK).click()
        page.locator(".slots-message").filter(has_text="Se caută spații disponibile... ").wait_for(state="detached")
        page.wait_for_timeout(500)
        if page.locator("strong", has_text="20:00").count() > 0:
            found = True
            print("Slot found!\n", flush=True)
        else:
            page.reload()
            print("Still looking for slot\n", flush=True)

    page.locator("strong", has_text="20:00").click()

    page.click("#submit-appointment")

    page.wait_for_url("https://www.calendis.ro/finalizeaza-programarea")

    page.check("#regulations-checkbox")
    page.click("#confirm-appointment")

    browser.close()