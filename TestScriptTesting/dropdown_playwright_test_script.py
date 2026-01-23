# Playwright Test Script - Select Country Dropdown
# Test Case: Navigate to GlobalSQA demo site and select India from country dropdown

from playwright.sync_api import sync_playwright, expect
import sys

def test_select_country_dropdown():
    """
    Test case to verify country dropdown selection functionality
    Steps:
    1. Navigate to the demo site
    2. Locate the country dropdown
    3. Select 'India' from the dropdown
    4. Verify the selection
    """
    
    with sync_playwright() as p:
        # Launch browser
        print("[INFO] Launching browser...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # Step 1: Navigate to the URL
            print("[STEP 1] Navigating to https://www.globalsqa.com/demo-site/select-dropdown-menu/")
            page.goto("https://www.globalsqa.com/demo-site/select-dropdown-menu/", wait_until="domcontentloaded")
            page.wait_for_timeout(2000)  # Wait for page to fully load
            print("[PASS] Successfully navigated to the page")
            
            # Step 2: Locate the dropdown element
            print("[STEP 2] Locating the country dropdown...")
            # The dropdown is inside a shadow DOM, so we need to handle it properly
            dropdown_selector = "select"
            page.wait_for_selector(dropdown_selector, timeout=10000)
            print("[PASS] Dropdown element located")
            
            # Step 3: Select 'India' from the dropdown
            print("[STEP 3] Selecting 'India' from the dropdown...")
            page.select_option(dropdown_selector, label="India")
            page.wait_for_timeout(1000)  # Wait for selection to complete
            print("[PASS] 'India' selected from dropdown")
            
            # Step 4: Verify the selection
            print("[STEP 4] Verifying the selection...")
            selected_value = page.locator(dropdown_selector).input_value()
            selected_text = page.locator(dropdown_selector).locator("option[selected]").inner_text()
            
            if selected_text == "India":
                print(f"[PASS] Verification successful - Selected country: {selected_text}")
                print(f"[INFO] Selected value: {selected_value}")
            else:
                print(f"[FAIL] Verification failed - Expected: India, Got: {selected_text}")
                raise AssertionError(f"Expected 'India' but got '{selected_text}'")
            
            # Final summary
            print("\n" + "="*60)
            print("TEST EXECUTION SUMMARY")
            print("="*60)
            print("Test Case: Select India from Country Dropdown")
            print("Status: PASS")
            print("All steps completed successfully")
            print("="*60)
            
            # Keep browser open for a moment to see the result
            page.wait_for_timeout(2000)
            
        except Exception as e:
            print(f"\n[FAIL] Test execution failed with error: {str(e)}")
            print("="*60)
            print("TEST EXECUTION SUMMARY")
            print("="*60)
            print("Test Case: Select India from Country Dropdown")
            print("Status: FAIL")
            print(f"Error: {str(e)}")
            print("="*60)
            sys.exit(1)
            
        finally:
            # Cleanup
            print("\n[INFO] Closing browser...")
            context.close()
            browser.close()
            print("[INFO] Browser closed")

if __name__ == "__main__":
    print("="*60)
    print("PLAYWRIGHT TEST EXECUTION")
    print("="*60)
    print("Test: Select Country Dropdown - India Selection")
    print("URL: https://www.globalsqa.com/demo-site/select-dropdown-menu/")
    print("="*60 + "\n")
    
    test_select_country_dropdown()
    
    print("\n[INFO] Test execution completed")

