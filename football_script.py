from playwright.sync_api import sync_playwright
import os
from datetime import datetime
import zoneinfo
import sys


# ---- Environment variables ----
USERNAME = os.environ["BOOKING_USERNAME"]
PASSWORD = os.environ["BOOKING_PASSWORD"]
URL = os.environ["BOOKING_URL"]
DAY_OF_WEEK = os.environ["BOOKING_DAY_OF_WEEK"]

# ---- Timezone check ----
tz = zoneinfo.ZoneInfo("Europe/Bucharest")
now = datetime.now(tz)

print(f"Current local time: {now}")

# We only proceed if it's Tuesday 19:50 local time
if not (now.weekday() == 1 and now.hour == 19 and now.minute == 50):
    print("Not the correct local booking time (19:50 Tuesday). Exiting.")
    sys.exit(0)

print("Correct booking window. Starting automation...")

# ---- Playwright automation ----
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"]
    )
    page = browser.new_page()
    page.goto(URL)

    # Accept cookies
    if page.locator("#rcc-confirm-button").count() > 0:
        page.click("#rcc-confirm-button")

    # Go to login
    page.get_by_role("link", name="Intră în cont").click()
    page.wait_for_url("**/login")

    # Fill login form
    page.fill("#email-input", USERNAME)
    page.fill("input[name='password']", PASSWORD)

    with page.expect_navigation():
        page.get_by_role("button", name="Intră în cont").click()

    # Go to reservations
    page.get_by_role("link", name="REZERVĂ ACUM").click()
    page.wait_for_url("**/reservations")

    # --- Select Gheorgheni base ---
    page.get_by_role("combobox").click()
    page.locator("li[data-value='gheorgheni-base']").click()

    # --- Click Fotbal ---
    with page.expect_navigation():
        page.locator("a[href*='preferredSportComplex=gheorgheni-base']").click()

    page.wait_for_url("**/reservations/football**")
    page.wait_for_load_state("networkidle")

    for week in range(2):

        print(f"Booking week {week + 1}")

        # --- Move to next week ---
        page.locator("button:has(svg[data-testid='ArrowForwardIcon'])").click()
        page.wait_for_timeout(800)

        # --- Click Tuesday ---
        page.locator("button:has(h6:text('M'))").nth(0).click()
        page.wait_for_timeout(500)

        # --- Look for slot ---
        while True:
            page.wait_for_load_state("networkidle")

            slot20 = page.locator("div.MuiChip-clickable:has-text('20:00')")
            if slot20.count() > 0:
                slot20.first.click()
                break

            slot21 = page.locator("div.MuiChip-clickable:has-text('21:00')")
            if slot21.count() > 0:
                slot21.first.click()
                break

            print("Still looking...")
            page.reload()
            page.wait_for_load_state("networkidle")

        # --- Reserve ---
        page.get_by_role("button", name="Rezervă").click()

        # --- Wait for confirmation modal ---
        page.wait_for_load_state("networkidle")

        # --- Check required checkboxes ---
        page.get_by_label("Voi invita încă 3 persoane").click()
        page.get_by_label("Am citit regulamentul specific*").click()
        page.get_by_label("Sunt de acord cu Regulamentul de funcționare*").click()

        # --- Wait until Confirm button is enabled ---
        confirm_button = page.get_by_role("button", name="Confirmă rezervarea")
        confirm_button.wait_for(state="visible")
        page.wait_for_timeout(300)

        # --- Click Confirm ---
        confirm_button.click()

        print("Reservation confirmed.")
        page.wait_for_timeout(1500)

    browser.close()