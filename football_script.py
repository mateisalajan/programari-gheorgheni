from playwright.sync_api import sync_playwright
import os

USERNAME = os.environ["BOOKING_USERNAME"]
PASSWORD = os.environ["BOOKING_PASSWORD"]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.calendis.ro/cluj-napoca/baza-sportiva-gheorgheni/fotbal/s")

    page.fill("#forEmail", USERNAME)
    page.fill("#forPassword", PASSWORD)
    page.click("text=CONECTEAZĂ-TE")

    found = False
    while not found:
        page.locator(".slots-message").filter(has_text="Se caută spații disponibile... ").wait_for(state="detached")
        page.click(".calendar-arrow.right-arrow")
        page.locator(".slots-message").filter(has_text="Se caută spații disponibile... ").wait_for(state="detached")
        page.click(".calendar-arrow.right-arrow")
        page.locator(".slots-message").filter(has_text="Se caută spații disponibile... ").wait_for(state="detached")
        if page.locator("strong", has_text="20:00").count() > 0:
            found = True
        else:
            page.reload()

    page.locator("strong", has_text="20:00").click()

    page.click("#submit-appointment")

    page.wait_for_url("https://www.calendis.ro/finalizeaza-programarea")

    page.check("#regulations-checkbox")
    page.click("#confirm-appointment")

    browser.close()