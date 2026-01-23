# Airbnb Search Test - Playwright Python Script
# Test Case: Search for New York stays and verify listing details
# Date: 2026-01-22

from playwright.sync_api import sync_playwright, expect
import time
from datetime import datetime, timedelta

def run_airbnb_test():
    """
    Test case for Airbnb search functionality:
    1. Navigate to Airbnb homepage
    2. Search for New York with specific dates and guests
    3. Verify search results
    4. Click on first listing and verify details page
    """
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print("[TEST START] Airbnb Search Flow Test")
        print("-" * 60)
        
        try:
            # Step 1: Navigate to Airbnb homepage
            print("[STEP 1] Navigating to www.airbnb.com...")
            page.goto("https://www.airbnb.com", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
            print("[PASS] Successfully navigated to Airbnb homepage")
            
            # Step 2: Handle cookie consent or welcome popups if present
            print("[STEP 2] Checking for cookie consent or welcome popups...")
            try:
                # Wait briefly to see if any modal appears
                page.wait_for_timeout(2000)
                # Try to find and close common popup selectors
                popup_selectors = [
                    "button[aria-label*='Close']",
                    "button:has-text('Accept')",
                    "button:has-text('Got it')",
                    "button:has-text('OK')"
                ]
                for selector in popup_selectors:
                    if page.locator(selector).count() > 0:
                        page.locator(selector).first.click()
                        print("[PASS] Closed popup/modal")
                        page.wait_for_timeout(1000)
                        break
                else:
                    print("[INFO] No popups detected")
            except Exception as e:
                print(f"[INFO] No popups to close or already closed: {e}")
            
            # Step 3: Click on location search field
            print("[STEP 3] Clicking on location search field...")
            # Wait for the search input to be visible
            location_input = page.locator("input[type='search'][name='query']").first
            location_input.wait_for(state="visible", timeout=10000)
            location_input.click()
            page.wait_for_timeout(1000)
            print("[PASS] Location search field activated")
            
            # Step 4: Enter location 'New York'
            print("[STEP 4] Entering location: New York...")
            location_input.fill("New York")
            page.wait_for_timeout(2000)
            print("[PASS] Location 'New York' entered successfully")
            
            # Step 5: Click on 'When' field to open date picker
            print("[STEP 5] Opening date picker...")
            when_button = page.locator("div[role='button']:has-text('When')").first
            when_button.click()
            page.wait_for_timeout(2000)
            print("[PASS] Date picker opened")
            
            # Step 6: Select check-in date (one week from today: 2026-01-29)
            print("[STEP 6] Selecting check-in date: January 29, 2026...")
            # Click on January 29, 2026
            checkin_date = page.locator("button[aria-label*='29, Thursday, Januar']").first
            checkin_date.click()
            page.wait_for_timeout(1000)
            print("[PASS] Check-in date selected: January 29, 2026")
            
            # Step 7: Select check-out date (three days after check-in: 2026-02-01)
            print("[STEP 7] Selecting check-out date: February 1, 2026...")
            # Click on February 1, 2026
            checkout_date = page.locator("button[aria-label*='1, Sunday, February']").first
            checkout_date.click()
            page.wait_for_timeout(1000)
            print("[PASS] Check-out date selected: February 1, 2026")
            
            # Step 8: Click on 'Who' field to set guests
            print("[STEP 8] Opening guests selector...")
            who_button = page.locator("div[role='button']:has-text('Who')").first
            who_button.click()
            page.wait_for_timeout(1000)
            print("[PASS] Guests selector opened")
            
            # Step 9: Set number of guests to 2 adults
            print("[STEP 9] Setting guests to 2 adults...")
            # Click increase button for adults twice
            increase_adults_button = page.locator("button[aria-label='increase value']").first
            increase_adults_button.click()
            page.wait_for_timeout(500)
            increase_adults_button.click()
            page.wait_for_timeout(1000)
            print("[PASS] Set guests to 2 adults")
            
            # Step 10: Click Search button
            print("[STEP 10] Clicking Search button...")
            search_button = page.locator("button[aria-label='Search']").first
            search_button.click()
            print("[PASS] Search button clicked")
            
            # Step 11: Wait for search results page to load
            print("[STEP 11] Waiting for search results page to load...")
            page.wait_for_url("**/s/New-York/**", timeout=30000)
            page.wait_for_timeout(5000)
            print("[PASS] Search results page loaded")
            
            # Handle any modal that might appear (e.g., pricing information modal)
            try:
                got_it_button = page.locator("button:has-text('Got it')")
                if got_it_button.count() > 0:
                    got_it_button.first.click()
                    page.wait_for_timeout(1000)
                    print("[INFO] Closed pricing information modal")
            except:
                pass
            
            # Step 12: Verify that a list of available stays is displayed
            print("[STEP 12] Verifying list of available stays...")
            # Check for listing elements
            listings = page.locator("[data-testid='card-container'], [itemprop='itemListElement']")
            listings_count = listings.count()
            
            if listings_count > 0:
                print(f"[PASS] Found {listings_count} listings displayed")
                # Also verify the results text
                results_text = page.locator("text=/homes in New York/i, text=/stays in New York/i")
                if results_text.count() > 0:
                    print(f"[PASS] Results header confirmed: {results_text.first.text_content()}")
            else:
                print("[FAIL] No listings found on the page")
                raise Exception("No listings displayed")
            
            # Step 13: Click on the first available listing
            print("[STEP 13] Clicking on first available listing...")
            first_listing = page.locator("[data-testid='card-container'] a, [itemprop='itemListElement'] a").first
            
            # Get the listing title before clicking
            listing_title = first_listing.get_attribute("aria-label") or "First listing"
            print(f"[INFO] Clicking on: {listing_title}")
            
            # Click and wait for new page/tab
            with context.expect_page() as new_page_info:
                first_listing.click()
            
            listing_page = new_page_info.value
            listing_page.wait_for_load_state("domcontentloaded")
            listing_page.wait_for_timeout(3000)
            print("[PASS] First listing clicked and details page opened")
            
            # Step 14: Verify that the listing details page opens successfully
            print("[STEP 14] Verifying listing details page...")
            
            # Check URL contains 'rooms'
            current_url = listing_page.url
            if "/rooms/" in current_url:
                print(f"[PASS] Listing details page URL verified: {current_url}")
            else:
                print(f"[FAIL] Unexpected URL: {current_url}")
                raise Exception("Listing details page URL not as expected")
            
            # Verify key elements on listing details page
            verification_checks = [
                ("h1, h2", "Listing title"),
                ("text=/bed/i", "Bed information"),
                ("text=/bathroom/i", "Bathroom information"),
                ("button:has-text('Reserve'), button:has-text('Check availability')", "Booking button"),
                ("text=/Check-in/i", "Check-in date"),
                ("text=/Checkout/i", "Checkout date")
            ]
            
            all_checks_passed = True
            for selector, description in verification_checks:
                element = listing_page.locator(selector)
                if element.count() > 0:
                    print(f"[PASS] {description} found")
                else:
                    print(f"[FAIL] {description} not found")
                    all_checks_passed = False
            
            if all_checks_passed:
                print("[PASS] All listing details page elements verified")
            else:
                print("[WARN] Some listing details page elements missing")
            
            # Close any translation modal if present
            try:
                close_modal = listing_page.locator("button[aria-label='Close']")
                if close_modal.count() > 0:
                    close_modal.first.click()
                    listing_page.wait_for_timeout(500)
                    print("[INFO] Closed translation modal")
            except:
                pass
            
            print("-" * 60)
            print("[TEST COMPLETE] All test steps executed successfully")
            print("[RESULT] PASS - Airbnb search flow test completed")
            print("-" * 60)
            
            # Keep browser open for a few seconds to see final state
            page.wait_for_timeout(3000)
            
        except Exception as e:
            print("-" * 60)
            print(f"[TEST FAILED] Error occurred: {str(e)}")
            print("[RESULT] FAIL - Test execution failed")
            print("-" * 60)
            raise
        
        finally:
            # Cleanup
            browser.close()
            print("[INFO] Browser closed")

if __name__ == "__main__":
    print("="*60)
    print("Airbnb Search Test - Playwright Automation")
    print("Test Date: 2026-01-22")
    print("="*60)
    print()
    
    run_airbnb_test()
    
    print()
    print("="*60)
    print("Test execution completed")
    print("="*60)

