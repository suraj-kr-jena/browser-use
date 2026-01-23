import asyncio
import warnings
from browser_use import Agent, Browser
from browser_use.llm.aws import ChatAnthropicBedrock
import boto3

# Suppress Windows asyncio warnings
warnings.filterwarnings("ignore", category=ResourceWarning, module="asyncio")

async def example():
	# Create boto3 session with your SSO profile
	session = boto3.Session(profile_name='mlops')

	# Configure AWS Bedrock with your organization's Claude model
	llm = ChatAnthropicBedrock(
		# Your specific Claude model ID from Bedrock
		model='global.anthropic.claude-sonnet-4-5-20250929-v1:0',

		# Model parameters
		temperature=0.2,
		max_tokens=8192,

		# Use boto3 session with SSO authentication
		session=session,
	)

	# browser = Browser(cdp_url="http://127.0.0.1:9222", headless=False)
	browser = Browser(headless=False)

	agent = Agent(
		task="""You need the run the following test case by following the Test steps and generate the full runnable playwright code for the test case.

		Test case:
		Help me test an e-commerce purchase flow on the Sephora India website.
		Open https://sephora.in/. Use the search bar to search for the exact product
		'Sephora Collection Cream Lip Stain Liquid Lipstick – 01 Always Red'. From the search
		results, select the product with brand 'Sephora Collection' and shade '01 Always Red'.
		On the product detail page, validate that the product name, shade, and price are displayed.
		Add the product to the cart. Open the cart and validate that the product name matches
		exactly, quantity is 1, and the price is consistent with the product detail page.
		Do not proceed to checkout.

		IMPORTANT REQUIREMENTS:
		1. Generate the full runnable Playwright code for the test case
		2. Use ONLY ASCII characters - NO Unicode symbols (✓, ✕, →, •, etc.)
		3. Use ASCII alternatives: 'PASS' instead of ✓, 'FAIL' instead of ✕, '->' instead of →
		4. Save the code to 'playwright_test_script.txt' using the write_file action
		5. The code must be valid Python/Playwright syntax that can run directly
		""",
		llm=llm,
		browser=browser,
		generate_gif="./my_agent_history_playwright.gif")

	try:
		history = await agent.run()

		print(f"Number of steps: {history.number_of_steps()}")
		print(f"URLs visited: {history.urls()}")
		print(f"Final result: {history.final_result()}")

		# Post-processing: Copy .txt to .py file with proper encoding
		from pathlib import Path
		import tempfile
		
		# Find the agent's temp directory
		temp_base = Path(tempfile.gettempdir())
		agent_dirs = list(temp_base.glob("browser_use_agent_*/browseruse_agent_data"))
		
		if agent_dirs:
			latest_dir = max(agent_dirs, key=lambda p: p.stat().st_mtime)
			txt_file = latest_dir / "playwright_test_script.txt"
			
			if txt_file.exists():
				py_file = Path("playwright_test_script.py")
				content = txt_file.read_text(encoding='utf-8')
				py_file.write_text(content, encoding='utf-8')
				print(f"\n✅ Playwright script saved to: {py_file.absolute()}")
			else:
				print("\n⚠️ Could not find flipkart_test_case.txt in agent data directory")
		else:
			print("\n⚠️ Could not locate agent data directory")

		return history
	finally:
		# Explicit cleanup to avoid Windows asyncio warnings
		if hasattr(agent, 'browser_session'):
			await agent.browser_session.kill()
		await asyncio.sleep(1)

if __name__ == "__main__":
    history = asyncio.run(example())