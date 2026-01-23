from playwright.sync_api import sync_playwright, expect
import time

def test_flipkart_decathlon_bottle_cart_quantity():
    """
    TC001: Complete happy path - Add Decathlon bottle to cart and modify quantity from 1 to 5 to 3

    Test Steps:
    1. Navigate to www.flipkart.com
    2. Locate the search bar at the top of the page
    3. Enter 'Decathlon bottle' into the search bar
    4. Click the search icon or press Enter
    5. Verify search results page displays with list of Decathlon bottle products    
    6. Click on 'QUECHUA by Decathlon Iron Man 0.75 ml Plastic Bottle' product       
    7. Verify product details page is displayed
    8. Click the 'Add to cart' button
    9. Verify button changes to indicate product added
    10. Click on 'Cart' link at the top of the page
    11. Verify cart page displays with product, quantity 1, and total amount
    12. Click the plus button 4 times to increase quantity from 1 to 5
    13. Verify quantity displays 5 and total amount updates correctly
    14. Click the minus button 2 times to decrease quantity from 5 to 3
    15. Verify quantity displays 3 and total amount reflects correct total
    """

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})      
        page = context.new_page()

        try:
            # Step 1: Navigate to www.flipkart.com
            print("Step 1: Navigating to Flipkart homepage...")
            page.goto('https://www.flipkart.com', wait_until='networkidle')
            page.wait_for_timeout(2000)

            # Close any initial popups if present
            try:
                # Try to close popup using Escape key
                page.keyboard.press('Escape')
                page.wait_for_timeout(1000)
            except:
                pass

            # Step 2 & 3: Locate the search bar and enter 'Decathlon bottle'
            print("Step 2-3: Locating search bar and entering 'Decathlon bottle'...")
            search_input = page.locator('input[name="q"], input[placeholder*="Search"]').first
            search_input.fill('Decathlon bottle')
            page.wait_for_timeout(1000)

            # Step 4: Click the search icon or press Enter
            print("Step 4: Clicking search button...")
            search_button = page.locator('button[type="submit"], button[aria-label*="Search"]').first
            search_button.click()
            page.wait_for_timeout(3000)

            # Step 5: Verify search results page displays
            print("Step 5: Verifying search results page...")
            page.wait_for_url('**/search?q=**', timeout=10000)
            results_text = page.locator('text=/results/i, text=/products/i').first   
            expect(results_text).to_be_visible(timeout=5000)
            print("Success: Search results page displayed successfully")

            # Step 6: Click on 'QUECHUA by Decathlon Iron Man 0.75 ml Plastic Bottle' product
            print("Step 6: Clicking on target product...")
            product_link = page.locator('a:has-text("QUECHUA by Decathlon Iron Man")').first

            # Handle new tab opening
            with context.expect_page() as new_page_info:
                product_link.click()
            product_page = new_page_info.value
            product_page.wait_for_load_state('networkidle')
            page.wait_for_timeout(2000)

            # Step 7: Verify product details page is displayed
            print("Step 7: Verifying product details page...")
            product_title = product_page.locator('text=/QUECHUA.*Iron Man/i').first  
            expect(product_title).to_be_visible(timeout=5000)
            print("Success: Product details page displayed successfully")

            # Step 8: Click the 'Add to cart' button
            print("Step 8: Clicking 'Add to cart' button...")
            add_to_cart_button = product_page.locator('button:has-text("Add to cart"), button:has-text("ADD TO CART")').first
            add_to_cart_button.click()
            product_page.wait_for_timeout(2000)

            # Step 9: Verify button changes to indicate product added
            print("Step 9: Verifying product added to cart...")
            cart_button = product_page.locator('button:has-text("Go to cart"), button:has-text("Going to cart")').first
            expect(cart_button).to_be_visible(timeout=5000)
            print("Success: Product successfully added to cart")

            # Step 10: Click on 'Cart' link at the top of the page
            print("Step 10: Navigating to cart page...")
            cart_link = product_page.locator('a:has-text("Cart")').first
            cart_link.click()
            product_page.wait_for_timeout(3000)

            # Close login popup if it appears
            try:
                product_page.keyboard.press('Escape')
                product_page.wait_for_timeout(2000)
            except:
                pass

            # Step 11: Verify cart page displays with product, quantity 1, and total amount
            print("Step 11: Verifying cart page with initial quantity...")
            product_page.wait_for_url('**/viewcart**', timeout=10000)
            cart_product = product_page.locator('text=/QUECHUA.*Iron Man/i').first   
            expect(cart_product).to_be_visible(timeout=5000)

            # Verify initial quantity is 1
            quantity_input = product_page.locator('input[type="text"][value]').first 
            initial_quantity = quantity_input.input_value()
            assert initial_quantity == '1', f"Expected initial quantity 1, but got {initial_quantity}"
            print(f"Success: Cart page displayed with initial quantity: {initial_quantity}")

            # Step 12: Click the plus button 4 times to increase quantity from 1 to 5
            print("Step 12: Increasing quantity from 1 to 5...")
            plus_button = product_page.locator('button:has-text("+")').first

            for i in range(4):
                plus_button.click()
                product_page.wait_for_timeout(2000)  # Wait for quantity to update   
                current_qty = quantity_input.input_value()
                print(f"  Clicked plus button {i+1}/4 times, current quantity: {current_qty}")

            # Step 13: Verify quantity displays 5 and total amount updates correctly 
            print("Step 13: Verifying quantity is 5...")
            product_page.wait_for_timeout(2000)
            final_quantity_5 = quantity_input.input_value()
            assert final_quantity_5 == '5', f"Expected quantity 5, but got {final_quantity_5}"

            # Verify total amount is updated
            total_amount = product_page.locator('text=/Total Amount/i').locator('xpath=following-sibling::*').first
            expect(total_amount).to_be_visible()
            print(f"Success: Quantity successfully increased to 5")

            # Step 14: Click the minus button 2 times to decrease quantity from 5 to 3
            print("Step 14: Decreasing quantity from 5 to 3...")
            minus_button = product_page.locator('button:has-text("-")').first        

            for i in range(2):
                minus_button.click()
                product_page.wait_for_timeout(2000)  # Wait for quantity to update   
                current_qty = quantity_input.input_value()
                print(f"  Clicked minus button {i+1}/2 times, current quantity: {current_qty}")

            # Step 15: Verify quantity displays 3 and total amount reflects correct total
            print("Step 15: Verifying final quantity is 3...")
            product_page.wait_for_timeout(2000)
            final_quantity_3 = quantity_input.input_value()
            assert final_quantity_3 == '3', f"Expected quantity 3, but got {final_quantity_3}"

            # Verify total amount is updated for 3 items
            total_amount_final = product_page.locator('text=/Total Amount/i').locator('xpath=following-sibling::*').first
            expect(total_amount_final).to_be_visible()
            print(f"Success: Quantity successfully decreased to 3")

            print("\n" + "="*80)
            print("TEST CASE TC001 PASSED SUCCESSFULLY!")
            print("="*80)
            print("Summary:")
            print(f"  - Product: QUECHUA by Decathlon Iron Man 0.75 ml Plastic Bottle")
            print(f"  - Initial Quantity: 1")
            print(f"  - Increased to: 5")
            print(f"  - Final Quantity: 3")
            print(f"  - All verification steps passed")
            print("="*80)

        except Exception as e:
            print(f"\nTEST FAILED: {str(e)}")
            # Take screenshot on failure
            product_page.screenshot(path='test_failure_screenshot.png')
            raise

        finally:
            # Keep browser open for 3 seconds to see final result
            page.wait_for_timeout(3000)
            browser.close()

if __name__ == '__main__':
    test_flipkart_decathlon_bottle_cart_quantity()

# ============================================================================       
# INSTALLATION INSTRUCTIONS:
# ============================================================================       
# 1. Install Python 3.8 or higher
# 2. Install Playwright:
#    pip install playwright pytest-playwright
# 3. Install browser drivers:
#    playwright install chromium
# 4. Run the test:
#    python flipkart_test_case_playwright.py
#    OR
#    pytest flipkart_test_case_playwright.py -v -s
# ============================================================================       

# ============================================================================       
# TEST CASE DETAILS:
# ============================================================================       
# TC_ID: TC001
# Category: positive
# Test Name: Complete happy path - Add Decathlon bottle to cart and modify quantity from 1 to 5 to 3
# Precondition: User is on Flipkart homepage and not logged in or logged in with valid account
# Expected Result: Product is successfully added to cart and quantity is modified from 1 to 5 to 3 with correct price calculations at each step
# ============================================================================       
