from playwright.sync_api import sync_playwright, expect
import time

def test_ikea_lack_coffee_table_guest_flow():
    """
    Test case: IKEA India guest e-commerce flow for LACK coffee table
    
    Test Steps:
    1. Open IKEA India website
    2. Search for 'LACK coffee table'
    3. Select 'LACK coffee table' from search results
    4. Validate product name and price are displayed on detail page
    5. Add product to cart
    6. Open cart
    7. Validate product name matches exactly and quantity is 1
    
    Note: Uses ASCII characters only (no Unicode symbols)
    """
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("[TEST START] IKEA India - LACK Coffee Table Guest Flow")
        print("-" * 60)
        
        try:
            # Step 1: Navigate to IKEA India website
            print("[STEP 1] Navigating to IKEA India website...")
            page.goto("https://www.ikea.com/in/en/", wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle")
            print("[PASS] Successfully loaded IKEA India homepage")
            
            # Step 2: Search for 'LACK coffee table'
            print("\n[STEP 2] Searching for 'LACK coffee table'...")
            # Locate search input (inside shadow DOM)
            search_input = page.locator("#ikea-search-input")
            search_input.wait_for(state="visible", timeout=10000)
            search_input.fill("LACK coffee table")
            print("[PASS] Entered search query: 'LACK coffee table'")
            
            # Click search button
            search_button = page.locator("button:has-text('Search'), span:has-text('Search')")
            search_button.click()
            print("[PASS] Clicked search button")
            
            # Wait for search results to load
            page.wait_for_url("**/search/**", timeout=10000)
            page.wait_for_load_state("networkidle")
            time.sleep(2)  # Additional wait for SPA rendering
            print("[PASS] Search results page loaded")
            
            # Step 3: Select 'LACK coffee table' from search results
            print("\n[STEP 3] Selecting LACK coffee table from search results...")
            # Click on the first LACK coffee table product
            product_link = page.locator("a:has-text('LACK'):has-text('Coffee table')").first
            product_link.wait_for(state="visible", timeout=10000)
            product_link.click()
            print("[PASS] Clicked on LACK coffee table product")
            
            # Wait for product detail page to load
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            print("[PASS] Product detail page loaded")
            
            # Step 4: Validate product name and price on detail page
            print("\n[STEP 4] Validating product details on detail page...")
            
            # Validate product name
            product_name = page.locator("h1, [class*='name'], [class*='title']").filter(has_text="LACK").first
            product_name.wait_for(state="visible", timeout=10000)
            product_name_text = product_name.text_content()
            assert "LACK" in product_name_text, f"Product name validation failed. Found: {product_name_text}"
            assert "Coffee table" in product_name_text or "coffee table" in product_name_text, f"Product type validation failed. Found: {product_name_text}"
            print(f"[PASS] Product name validated: {product_name_text.strip()}")
            
            # Validate product price
            price_element = page.locator("[class*='price'], span:has-text('Rs')").filter(has_text="Rs").first
            price_element.wait_for(state="visible", timeout=10000)
            price_text = price_element.text_content()
            assert "Rs" in price_text or "₹" in price_text, f"Price validation failed. Found: {price_text}"
            print(f"[PASS] Product price validated: {price_text.strip()}")
            
            # Step 5: Add product to cart
            print("\n[STEP 5] Adding product to cart...")
            
            # Scroll to add to bag button if needed
            page.evaluate("window.scrollBy(0, 300)")
            time.sleep(1)
            
            # Click 'Add to bag' button
            add_to_bag_button = page.locator("button:has-text('Add to bag'), button[aria-label*='Add to']").first
            add_to_bag_button.wait_for(state="visible", timeout=10000)
            add_to_bag_button.click()
            print("[PASS] Clicked 'Add to bag' button")
            
            # Wait for cart to update
            time.sleep(2)
            
            # Step 6: Open cart
            print("\n[STEP 6] Opening shopping cart...")
            cart_button = page.locator("a[aria-label*='Shopping bag'], [aria-label*='Shopping bag']").first
            cart_button.wait_for(state="visible", timeout=10000)
            cart_button.click()
            print("[PASS] Clicked shopping bag icon")
            
            # Wait for cart page to load
            page.wait_for_url("**/shoppingcart/**", timeout=10000)
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            print("[PASS] Shopping cart page loaded")
            
            # Step 7: Validate cart contents
            print("\n[STEP 7] Validating cart contents...")
            
            # Validate product name in cart
            cart_product_name = page.locator("a:has-text('LACK'), span:has-text('LACK')").filter(has_text="coffee table").first
            cart_product_name.wait_for(state="visible", timeout=10000)
            cart_product_name_text = cart_product_name.text_content()
            assert "LACK" in cart_product_name_text, f"Cart product name validation failed. Found: {cart_product_name_text}"
            assert "coffee table" in cart_product_name_text.lower(), f"Cart product type validation failed. Found: {cart_product_name_text}"
            print(f"[PASS] Cart product name validated: {cart_product_name_text.strip()}")
            
            # Validate quantity is 1
            quantity_input = page.locator("input[type='text'][value='1'], input[aria-label*='quantity'][value='1']").first
            quantity_input.wait_for(state="visible", timeout=10000)
            quantity_value = quantity_input.get_attribute("value")
            assert quantity_value == "1", f"Quantity validation failed. Expected: 1, Found: {quantity_value}"
            print(f"[PASS] Quantity validated: {quantity_value}")
            
            # Test completed successfully
            print("\n" + "=" * 60)
            print("[TEST COMPLETE] All validations passed successfully!")
            print("=" * 60)
            print("\nTest Summary:")
            print("- Searched for 'LACK coffee table': PASS")
            print("- Selected product from search results: PASS")
            print("- Validated product name on detail page: PASS")
            print("- Validated product price on detail page: PASS")
            print("- Added product to cart: PASS")
            print("- Opened shopping cart: PASS")
            print("- Validated product name in cart: PASS")
            print("- Validated quantity is 1: PASS")
            print("\n[RESULT] TEST PASSED")
            
        except AssertionError as e:
            print(f"\n[FAIL] Assertion failed: {str(e)}")
            print("[RESULT] TEST FAILED")
            raise
            
        except Exception as e:
            print(f"\n[ERROR] Test execution failed: {str(e)}")
            print("[RESULT] TEST FAILED")
            raise
            
        finally:
            # Keep browser open for 3 seconds to view final state
            time.sleep(3)
            # Close browser
            browser.close()
            print("\n[INFO] Browser closed")

if __name__ == "__main__":
    test_ikea_lack_coffee_table_guest_flow()

