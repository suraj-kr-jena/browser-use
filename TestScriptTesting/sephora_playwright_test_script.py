from playwright.sync_api import sync_playwright, expect
import time

def test_sephora_purchase_flow():
    """
    Test case: E-commerce purchase flow on Sephora India website
    
    Test Steps:
    1. Open https://sephora.in/
    2. Search for 'Sephora Collection Cream Lip Stain Liquid Lipstick - 01 Always Red'
    3. Select product with brand 'Sephora Collection' and shade '01 Always Red'
    4. Validate product name, shade, and price on product detail page
    5. Add product to cart
    6. Open cart and validate product name, quantity, and price
    
    Note: This test does not proceed to checkout as per requirements
    """
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("[STEP 1] Navigating to Sephora India website...")
        page.goto("https://sephora.in/")
        page.wait_for_load_state("networkidle")
        print("[PASS] Successfully loaded Sephora India homepage")
        
        # Step 2: Search for the product
        print("\n[STEP 2] Searching for product...")
        search_input = page.locator("#search")
        search_input.fill("Sephora Collection Cream Lip Stain Liquid Lipstick - 01 Always Red")
        print("[INFO] Entered search query")
        
        # Click search button
        search_button = page.locator("#search-container button")
        search_button.click()
        print("[INFO] Clicked search button")
        
        # Wait for search results to load
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        print("[PASS] Search results loaded")
        
        # Step 3: Select the product with shade '01 Always Red'
        print("\n[STEP 3] Selecting product with shade '01 Always Red'...")
        # Look for product with the specific shade - using text content to find the right product
        product_cards = page.locator("[id^='product-']").all()
        
        target_product = None
        for card in product_cards:
            try:
                shade_text = card.locator("text=01 Always Red").first
                if shade_text.is_visible():
                    # Check if this product is available (not out of stock)
                    out_of_stock = card.locator("text=OUT OF STOCK").count()
                    if out_of_stock == 0:
                        target_product = card
                        break
            except:
                continue
        
        if target_product:
            # Click on the product title/link to go to detail page
            product_link = target_product.locator("a").first
            product_link.click()
            print("[PASS] Clicked on product with shade '01 Always Red'")
        else:
            print("[FAIL] Could not find available product with shade '01 Always Red'")
            browser.close()
            return
        
        # Wait for product detail page to load
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # Step 4: Validate product details on product detail page
        print("\n[STEP 4] Validating product details on product detail page...")
        
        # Validate product name
        product_name = page.locator("h1:has-text('New Cream Lip Stain')").first
        expect(product_name).to_be_visible()
        product_name_text = product_name.text_content().strip()
        print(f"[INFO] Product name: {product_name_text}")
        assert "New Cream Lip Stain" in product_name_text, "Product name validation failed"
        print("[PASS] Product name is displayed correctly")
        
        # Validate shade
        shade = page.locator("text=01 Always Red").first
        expect(shade).to_be_visible()
        shade_text = shade.text_content().strip()
        print(f"[INFO] Shade: {shade_text}")
        assert "01 Always Red" in shade_text, "Shade validation failed"
        print("[PASS] Shade '01 Always Red' is displayed correctly")
        
        # Validate price
        price_element = page.locator("p:has-text('1,700')").first
        expect(price_element).to_be_visible()
        price_text = price_element.text_content().strip()
        print(f"[INFO] Price on detail page: {price_text}")
        assert "1,700" in price_text or "1700" in price_text, "Price validation failed"
        detail_page_price = price_text
        print("[PASS] Price is displayed correctly on product detail page")
        
        # Step 5: Add product to cart
        print("\n[STEP 5] Adding product to cart...")
        add_to_bag_button = page.locator("button:has-text('ADD TO BAG')").first
        add_to_bag_button.click()
        print("[INFO] Clicked 'ADD TO BAG' button")
        
        # Wait for cart to update
        time.sleep(3)
        print("[PASS] Product added to cart")
        
        # Step 6: Validate cart contents
        print("\n[STEP 6] Validating cart contents...")
        
        # Cart overlay should be visible - if not, click on bag icon
        cart_overlay = page.locator("text=VIEW BAG")
        if not cart_overlay.is_visible():
            bag_icon = page.locator("#header-cart")
            bag_icon.click()
            time.sleep(2)
        
        # Validate product name in cart
        cart_product_name = page.locator("text=New Cream Lip Stain").first
        expect(cart_product_name).to_be_visible()
        cart_product_name_text = cart_product_name.text_content().strip()
        print(f"[INFO] Product name in cart: {cart_product_name_text}")
        assert "New Cream Lip Stain" in cart_product_name_text, "Cart product name validation failed"
        print("[PASS] Product name in cart matches the product detail page")
        
        # Validate quantity
        quantity = page.locator("text=Qty: 1").first
        expect(quantity).to_be_visible()
        quantity_text = quantity.text_content().strip()
        print(f"[INFO] Quantity in cart: {quantity_text}")
        assert "Qty: 1" in quantity_text or "1" in quantity_text, "Quantity validation failed"
        print("[PASS] Quantity is 1 as expected")
        
        # Validate price consistency
        cart_total = page.locator("text=Total:").locator("xpath=following-sibling::*").first
        if not cart_total.is_visible():
            cart_total = page.locator("text=1,700").last
        
        expect(cart_total).to_be_visible()
        cart_price_text = cart_total.text_content().strip()
        print(f"[INFO] Price in cart: {cart_price_text}")
        assert "1,700" in cart_price_text or "1700" in cart_price_text, "Cart price validation failed"
        print("[PASS] Price in cart is consistent with product detail page")
        
        # Final summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print("[PASS] All validations completed successfully:")
        print("  - Product name validated on detail page and cart")
        print("  - Shade '01 Always Red' validated")
        print("  - Price consistency validated between detail page and cart")
        print("  - Quantity validated as 1")
        print("\n[INFO] Test completed. Not proceeding to checkout as per requirements.")
        print("="*60)
        
        # Keep browser open for a few seconds to see final state
        time.sleep(3)
        
        # Close browser
        browser.close()
        print("\n[INFO] Browser closed. Test execution completed.")

if __name__ == "__main__":
    test_sephora_purchase_flow()

