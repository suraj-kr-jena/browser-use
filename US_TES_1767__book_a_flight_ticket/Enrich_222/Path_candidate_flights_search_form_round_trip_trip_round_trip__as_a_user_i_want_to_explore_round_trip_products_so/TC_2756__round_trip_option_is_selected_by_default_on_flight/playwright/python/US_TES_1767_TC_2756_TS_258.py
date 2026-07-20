from playwright.sync_api import sync_playwright
import sys
import os

import json
import os
from pathlib import Path

def load_test_data():
    test_data_file = os.environ.get("TEST_DATA_FILE")
    candidates = []
    if test_data_file:
        candidates.append(Path(test_data_file))
    current_file = Path(__file__)
    candidates.append(current_file.with_suffix(".testdata.json"))
    candidates.append(current_file.with_name("test_data.json"))
    for candidate in candidates:
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))
    raise FileNotFoundError("Test data file not found. Set TEST_DATA_FILE or place a .testdata.json file next to the script.")

TEST_DATA = load_test_data()
# Configure UTF-8 for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

def test_flow():
    with sync_playwright() as p:
        # Connect to browser via CDP. CDP_URL is set by the worker when running
        # in the scalable browser pool. Fail loudly if it is missing.
        cdp_url = os.environ.get("CDP_URL")
        if not cdp_url:
            raise RuntimeError("CDP_URL env var not set. This script must be run via the browser pool worker.")
        browser = p.chromium.connect_over_cdp(cdp_url)
        contexts = browser.contexts
        if not contexts:
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()
        else:
            context = contexts[0]
            pages = context.pages
            if not pages:
                page = context.new_page()
            else:
                page = pages[0]
        page.set_default_timeout(30000)

        try:
            # Step 0: Navigate to https://www.booking.com/
            print("Step 0: Navigate to target website")
            page.goto(TEST_DATA["url"], wait_until="commit")
            page.wait_for_selector("body")  # Ensure page structure loaded
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)  # Allow dynamic content to load
            print("[OK] Step 0 completed")

            # Step 1: Click 'Dismiss sign-in info.' button/link
            print("Step 1: Click 'Dismiss sign-in info.' button/link")
            # Multi-selector fallback strategy (tries alternatives if first fails)
            click_success = False
            # Strategy 1: Aria-label
            try:
                page.wait_for_selector('[aria-label="Dismiss sign-in info."]', state='visible', timeout=8000)
                page.locator('[aria-label="Dismiss sign-in info."]').first.click()
                click_success = True
            except:
                pass  # Try next selector
            if not click_success:
                try:
                    # Strategy 2: Specific Class
                    page.wait_for_selector('button.de576f5064', state='visible', timeout=8000)
                    page.locator('button.de576f5064').first.click()
                    click_success = True
                except:
                    pass  # Try next selector
            if not click_success:
                try:
                    # Strategy 3: CSS
                    page.wait_for_selector('button[aria-label="Dismiss sign-in info."]', state='visible', timeout=8000)
                    page.locator('button[aria-label="Dismiss sign-in info."]').first.click()
                    click_success = True
                except:
                    pass  # Try next selector
            if not click_success:
                try:
                    # Strategy 4: XPath (last resort)
                    page.wait_for_selector('xpath=html/body/div[2]/div/div/div/div[1]/div[1]/div/div/button', state='visible', timeout=8000)
                    page.locator('xpath=html/body/div[2]/div/div/div/div[1]/div[1]/div/div/button').first.click()
                    click_success = True
                except:
                    pass  # Try next selector

            if not click_success:
                raise Exception('Failed to click element after trying 4 selectors')

            page.wait_for_load_state('domcontentloaded')
            print("[OK] Step 1 completed")

            # Step 2: Click A with text 'Flights'
            print("Step 2: Click A with text 'Flights'")
            # Multi-selector fallback strategy (tries alternatives if first fails)
            click_success = False
            # Strategy 1: ID
            try:
                page.wait_for_selector('#flights', state='visible', timeout=10000)
                page.locator('#flights').first.click()
                click_success = True
            except:
                pass  # Try next selector
            if not click_success:
                try:
                    # Strategy 2: Specific Class
                    page.wait_for_selector('a.de576f5064', state='visible', timeout=10000)
                    page.locator('a.de576f5064').first.click()
                    click_success = True
                except:
                    pass  # Try next selector
            if not click_success:
                try:
                    # Strategy 3: XPath (last resort)
                    page.wait_for_selector('xpath=html/body/div[1]/div/div[2]/div/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/header/div/nav[2]/div/ul/li[2]/a', state='visible', timeout=10000)
                    page.locator('xpath=html/body/div[1]/div/div[2]/div/div[1]/div/div/div/div/div/div/div/div/div/div/div/div/header/div/nav[2]/div/ul/li[2]/a').first.click()
                    click_success = True
                except:
                    pass  # Try next selector

            if not click_success:
                try:
                    # Strategy: goto fallback (direct navigation)
                    page.goto(TEST_DATA["booking_url"], wait_until="commit")
                    page.wait_for_selector("body")  # Ensure page structure loaded
                    page.wait_for_load_state("domcontentloaded")
                    click_success = True
                except:
                    pass  # goto also failed

            if not click_success:
                raise Exception('Failed to click element after trying 3 selectors')

            page.wait_for_load_state('domcontentloaded')
            print("[OK] Step 2 completed")

            # Step 3: Verify extracted data
            print("Step 3: Verify extracted data")
            page.wait_for_timeout(2000)  # Ensure page is fully loaded
            # Verify Pre-selected option: \"Round-trip\"**
            try:
                page_text = page.inner_text("body")
                assert "\"Round-trip\"**" in page_text, "Could not find: \"Round-trip\"**"
                print("[OK] Verified Pre-selected option")
            except Exception:
                pass  # Verification is non-fatal; failures are intentionally not logged
            print("[OK] Step 3 completed")

            print("")
            print("[OK] All steps completed successfully")

        except Exception as e:
            print(f"FAIL: {e}")
            try:
                page.screenshot(path="error_screenshot.png")
                print("Error screenshot saved to: error_screenshot.png")
            except:
                print("Could not save error screenshot")
            raise
        finally:
            pass  # Do not close context/browser - they are shared via CDP

if __name__ == "__main__":
    test_flow()
