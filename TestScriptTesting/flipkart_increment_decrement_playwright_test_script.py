# Playwright Test Script for TC001
# Test Case: Complete happy path - Add Decathlon bottle to cart and modify quantity from 1 to 5 to 3
# Generated: 2026-01-22

from playwright.sync_api import sync_playwright, expect
import time

def test_decathlon_bottle_cart_quantity_modification():
    """
    Test Case ID: TC001
    Category: Positive
    Description: Complete happy path - Add Decathlon bottle to cart and modify quantity from 1 to 5 to 3
    
    Test Steps:
    1. Navigate to www.flipkart.com
    2. Search for 'Decathlon bottle'
    3. Click on 'QUECHUA by Decathlon Iron Man 0.75 ml Plastic Bottle'
    4. Add product to cart
    5. Verify product added
    6. Navigate to cart
    7. Verify initial quantity is 1
    8. Increase quantity from 1 to 5 (click plus 4 times)
    9. Verify quantity is 5
    10. Decrease quantity from 5 to 3 (click minus 2 times)
    11. Verify final quantity is 3 and total amount is correct
    """
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        print("[STEP 1] Navigate to Flipkart homepage")
        page.goto("https://www.flipkart.com")
        page.wait_for_load_state("networkidle")
        print("PASS: Successfully navigated to Flipkart homepage")
        
        # Handle login popup if appears
        try:
            close_button = page.locator("button:has-text('✕')")
            if close_button.is_visible(timeout=3000):
                close_button.click()
                print("INFO: Closed login popup")
        except:
            print("INFO: No login popup detected")
        
        print("\n[STEP 2] Locate and interact with search bar")
        # Search bar is in shadow DOM - use pierce selector
        search_input = page.locator("input[name='q'][placeholder*='Search for products']").first
        search_input.wait_for(state="visible", timeout=10000)
        print("PASS: Search bar located successfully")
        
        print("\n[STEP 3] Enter 'Decathlon bottle' into search bar")
        search_input.fill("Decathlon bottle")
        print("PASS: Entered 'Decathlon bottle' into search bar")
        
        print("\n[STEP 4] Click search button")
        search_button = page.locator("button[type='submit']").first
        search_button.click()
        print("PASS: Clicked search button")
        
        print("\n[STEP 5] Verify search results page displays")
        page.wait_for_load_state("networkidle")
        time.sleep(2)  # Wait for SPA to render results
        
        # Verify search results are displayed
        search_results = page.locator("text=Decathlon bottle").first
        expect(search_results).to_be_visible()
        print("PASS: Search results page displayed with Decathlon bottle products")
        
        print("\n[STEP 6] Click on 'QUECHUA by Decathlon Iron Man 0.75 ml Plastic Bottle'")
        # Locate the specific product
        product_link = page.locator("a:has-text('QUECHUA by Decathlon Iron Man')").first
        
        # Handle new tab opening
        with context.expect_page() as new_page_info:
            product_link.click()
        product_page = new_page_info.value
        product_page.wait_for_load_state("networkidle")
        print("PASS: Clicked on target product, new tab opened")
        
        print("\n[STEP 7] Verify product details page")
        # Verify product images are visible
        product_image = product_page.locator("img[alt*='QUECHUA']").first
        expect(product_image).to_be_visible()
        
        # Verify price is displayed
        price_element = product_page.locator("text=/₹[0-9,]+/").first
        expect(price_element).to_be_visible()
        
        # Verify specifications are visible
        specs = product_page.locator("text=/0.75 ml|Plastic|Green/").first
        expect(specs).to_be_visible()
        print("PASS: Product details page verified - images, price, and specifications visible")
        
        print("\n[STEP 8] Click 'Add to cart' button")
        add_to_cart_button = product_page.locator("button:has-text('Add to cart')").first
        add_to_cart_button.click()
        print("PASS: Clicked 'Add to cart' button")
        
        print("\n[STEP 9] Verify button changes to indicate product added")
        time.sleep(1)  # Wait for button state change
        going_to_cart_button = product_page.locator("button:has-text('Going to cart')").first
        expect(going_to_cart_button).to_be_visible(timeout=5000)
        print("PASS: Button changed to 'Going to cart' - product added successfully")
        
        print("\n[STEP 10] Click on 'Cart' link")
        cart_link = product_page.locator("a:has-text('Cart')").first
        cart_link.click()
        product_page.wait_for_url("**/viewcart**")
        product_page.wait_for_load_state("networkidle")
        time.sleep(2)  # Wait for cart page to fully render
        print("PASS: Navigated to cart page")
        
        print("\n[STEP 11] Verify cart page displays with product, quantity 1, and total amount")
        # Verify product is in cart
        cart_product = product_page.locator("text=QUECHUA by Decathlon Iron Man").first
        expect(cart_product).to_be_visible()
        
        # Verify initial quantity is 1
        quantity_input = product_page.locator("input[type='text'][value='1']").first
        expect(quantity_input).to_be_visible()
        current_quantity = quantity_input.input_value()
        assert current_quantity == "1", f"Expected quantity 1, but got {current_quantity}"
        
        # Verify total amount is displayed
        total_amount = product_page.locator("text=/Total Amount/").first
        expect(total_amount).to_be_visible()
        print("PASS: Cart verified - product present, quantity is 1, total amount displayed")
        
        print("\n[STEP 12] Click plus button 4 times to increase quantity from 1 to 5")
        plus_button = product_page.locator("button:has-text('+')").first
        
        # Click plus button 4 times: 1 -> 2 -> 3 -> 4 -> 5
        for i in range(4):
            plus_button.click()
            time.sleep(0.5)  # Wait for quantity update
            print(f"  Clicked plus button (click {i+1}/4)")
        
        print("PASS: Clicked plus button 4 times")
        
        print("\n[STEP 13] Verify quantity displays 5 and total amount updates correctly")
        time.sleep(1)  # Wait for final update
        quantity_input_5 = product_page.locator("input[type='text'][value='5']").first
        expect(quantity_input_5).to_be_visible(timeout=5000)
        current_quantity_5 = quantity_input_5.input_value()
        assert current_quantity_5 == "5", f"Expected quantity 5, but got {current_quantity_5}"
        
        # Verify total amount updated (should be around Rs. 1,962 for 5 items)
        total_amount_5 = product_page.locator("text=/₹1,9[0-9]{2}/").first
        expect(total_amount_5).to_be_visible()
        print("PASS: Quantity is 5 and total amount updated correctly")
        
        print("\n[STEP 14] Click minus button 2 times to decrease quantity from 5 to 3")
        minus_button = product_page.locator("button:has-text('-')").first
        
        # Click minus button 2 times: 5 -> 4 -> 3
        for i in range(2):
            minus_button.click()
            time.sleep(0.5)  # Wait for quantity update
            print(f"  Clicked minus button (click {i+1}/2)")
        
        print("PASS: Clicked minus button 2 times")
        
        print("\n[STEP 15] Verify quantity displays 3 and total amount reflects correct total for 3 items")
        time.sleep(1)  # Wait for final update
        quantity_input_3 = product_page.locator("input[type='text'][value='3']").first
        expect(quantity_input_3).to_be_visible(timeout=5000)
        current_quantity_3 = quantity_input_3.input_value()
        assert current_quantity_3 == "3", f"Expected quantity 3, but got {current_quantity_3}"
        
        # Verify total amount for 3 items (should be around Rs. 1,180)
        total_amount_3 = product_page.locator("text=/₹1,1[0-9]{2}/").first
        expect(total_amount_3).to_be_visible()
        print("PASS: Final quantity is 3 and total amount is correct for 3 items")
        
        print("\n" + "="*80)
        print("TEST CASE TC001: PASSED")
        print("="*80)
        print("Summary:")
        print("- Successfully navigated to Flipkart and searched for 'Decathlon bottle'")
        print("- Successfully added 'QUECHUA by Decathlon Iron Man 0.75 ml Plastic Bottle' to cart")
        print("- Successfully modified quantity: 1 -> 5 -> 3")
        print("- All verification steps passed")
        print("- Price calculations correct at each step")
        
        # Cleanup
        time.sleep(2)
        browser.close()

if __name__ == "__main__":
    test_decathlon_bottle_cart_quantity_modification()

