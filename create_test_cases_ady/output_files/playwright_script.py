import asyncio
from playwright.async_api import async_playwright, expect

async def test_tc006_decrease_quantity_below_minimum():
    """
    TC006: Attempt to decrease quantity below minimum value of 1
    Category: Negative test case
    Expected: System prevents quantity from going below 1
    """
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Step 1: Navigate to Flipkart
            print("Step 1: Navigating to www.flipkart.com...")
            await page.goto("https://www.flipkart.com")
            await page.wait_for_load_state("networkidle")

            # Step 2: Search for 'Decathlon bottle'
            print("Step 2: Searching for 'Decathlon bottle'...")
            search_input = page.locator("input[name='q']").first
            await search_input.fill("Decathlon bottle")
            await search_input.press("Enter")
            await page.wait_for_load_state("networkidle")

            # Step 3: Add a product to cart
            print("Step 3: Adding product to cart...")
            # Click on the first Decathlon bottle product
            product_link = page.locator("a:has-text('QUECHUA by Decathlon')").first        

            # Handle new tab opening
            async with context.expect_page() as new_page_info:
                await product_link.click()
            product_page = await new_page_info.value
            await product_page.wait_for_load_state("networkidle")

            # Click ADD TO CART button
            add_to_cart_btn = product_page.locator("button:has-text('ADD TO CART')").first 
            await add_to_cart_btn.click()
            await product_page.wait_for_timeout(2000)  # Wait for cart update

            # Step 4: Go to Cart page
            print("Step 4: Navigating to cart page...")
            # Click on cart icon or navigate directly
            await product_page.goto("https://www.flipkart.com/viewcart")
            await product_page.wait_for_load_state("networkidle")

            # Step 5: Verify product is in cart with quantity 1
            print("Step 5: Verifying product in cart with quantity 1...")
            quantity_input = product_page.locator("input[type='text'][value='1']").first   
            await expect(quantity_input).to_be_visible()
            current_quantity = await quantity_input.input_value()
            assert current_quantity == "1", f"Expected quantity 1, but got {current_quantity}"
            print(f"✓ Verified: Product quantity is {current_quantity}")

            # Step 6: Attempt to click the minus button to decrease quantity below 1       
            print("Step 6: Attempting to decrease quantity below 1...")
            # Use JavaScript to find and click the minus button
            minus_button_clicked = await product_page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button'));       
                    const minusButton = buttons.find(btn => btn.textContent.trim() === '–' || btn.textContent.trim() === '-');
                    if (minusButton) {
                        minusButton.click();
                        return true;
                    }
                    return false;
                }
            """)

            assert minus_button_clicked, "Minus button not found"
            print("✓ Clicked minus button")

            # Wait for any UI updates
            await product_page.wait_for_timeout(1000)

            # Step 7: Verify that quantity remains at 1
            print("Step 7: Verifying quantity remains at 1...")
            final_quantity = await product_page.evaluate("""
                () => {
                    const input = document.querySelector('input[type="text"][value="1"]'); 
                    return input ? input.value : null;
                }
            """)

            assert final_quantity == "1", f"Expected quantity to remain 1, but got {final_quantity}"
            print(f"✓ PASSED: Quantity remained at {final_quantity} (system prevented going below 1)")

            print("\n" + "="*60)
            print("TEST CASE TC006: PASSED")
            print("System correctly prevents quantity from going below 1")
            print("="*60)

        except Exception as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            raise

        finally:
            # Close browser
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_tc006_decrease_quantity_below_minimum())
