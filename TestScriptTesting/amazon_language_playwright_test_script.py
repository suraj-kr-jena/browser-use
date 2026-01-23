# Amazon Language Change Test - Playwright Script
# Test Case: Navigate to Amazon.com, hover over EN label, change language to DE, and wait for page load
# Requirements: ASCII characters only, no Unicode symbols

from playwright.sync_api import sync_playwright, expect
import time

def test_amazon_language_change():
    """
    Test case to change Amazon language from EN to DE
    Steps:
    1. Navigate to www.amazon.com
    2. Click on EN language selector
    3. Wait for preferences page to load
    4. Select Deutsch - DE language option
    5. Click Save Changes button
    6. Wait for page to reload with German language
    """
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("[STEP 1] Navigating to www.amazon.com...")
        page.goto("https://www.amazon.com")
        page.wait_for_load_state("networkidle")
        print("[PASS] Successfully loaded Amazon.com")
        
        print("[STEP 2] Clicking on EN language selector...")
        # Locate and click the EN language selector
        # Using aria-label that contains "Choose a language"
        language_selector = page.locator('[aria-label*="Choose a language"]').first
        language_selector.click()
        print("[PASS] Clicked EN language selector")
        
        print("[STEP 3] Waiting for customer preferences page to load...")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Additional wait for dynamic content
        print("[PASS] Customer preferences page loaded")
        
        print("[STEP 4] Selecting Deutsch - DE language option...")
        # Click on the Deutsch - DE radio button
        # The radio button has value="de_DE"
        german_radio = page.locator('input[type="radio"][value="de_DE"]')
        german_radio.click()
        print("[PASS] Selected Deutsch - DE language")
        
        print("[STEP 5] Clicking Save Changes button...")
        # Click the submit button to save changes
        # The button is an input type=submit
        save_button = page.locator('input[type="submit"]').first
        save_button.click()
        print("[PASS] Clicked Save Changes button")
        
        print("[STEP 6] Waiting for page to reload with German language...")
        page.wait_for_load_state("networkidle")
        time.sleep(3)  # Wait for complete page reload
        print("[PASS] Page reloaded successfully")
        
        # Verify that the page is now in German
        print("[VERIFICATION] Checking if page is in German...")
        # Check for German text elements
        page_content = page.content()
        if "Liefern nach" in page_content or "Einkaufswagen" in page_content:
            print("[PASS] Page is now displaying in German language")
            print("[TEST RESULT] -> PASS - Language successfully changed to DE")
        else:
            print("[FAIL] Could not verify German language on page")
            print("[TEST RESULT] -> FAIL - Language change verification failed")
        
        # Keep browser open for a moment to see the result
        time.sleep(2)
        
        # Close browser
        browser.close()
        print("[INFO] Test execution completed")

if __name__ == "__main__":
    print("="*70)
    print("Amazon Language Change Test - Playwright Automation")
    print("="*70)
    test_amazon_language_change()
    print("="*70)
    print("Test execution finished")
    print("="*70)

