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
		task="""
		Task:
		Help me test an e-commerce purchase flow on the Sephora India website.
		Open https://sephora.in/. Use the search bar to search for the exact product
		'Sephora Collection Cream Lip Stain Liquid Lipstick – 01 Always Red'. From the search
		results, select the product with brand 'Sephora Collection' and shade '01 Always Red'.
		On the product detail page, validate that the product name, shade, and price are displayed.
		Add the product to the cart. Open the cart and validate that the product name matches
		exactly, quantity is 1, and the price is consistent with the product detail page.
		Do not proceed to checkout.

		User Guide Creation Task:
		You also need to transform the whole journey of the user into a human-friendly, step-by-step guide that a non-technical user can follow to complete this feature.

		Guidelines to create user guide:
		- Create a detailed step by step guide for the user to complete the feature. Add as many steps as needed to complete the feature.
		- Add as much detail as possible to the guide.
		- Focus on the main happy-path flow only.
		- Use simple, direct language (imperative voice).
		- Number the steps: '1.', '2.', '3.', ...
		- For taps/clicks, say things like: \"Tap 'Sent Quotes'\" or \"Click 'Create Quote'\.
		- For data entry, say things like: \"Enter '1000.00' in 'Gross Invoice Amount'\.
		- Do NOT mention internal technical terms like 'screen_id', 'record_id', etc.
		- Do NOT include raw JSON or code. Plain text only.
		- If some details are missing, make reasonable, generic assumptions but keep them minimal.
		
		IMPORTANT: 
		1. Save the complete user guide to a file called 'user_guide.txt' using the write_file action.
		2. Use only ASCII characters - NO Unicode symbols (✓, ✕, →, •, etc.)
		3. Use ASCII alternatives: 'PASS' instead of ✓, 'FAIL' instead of ✕, '->' instead of →
    	""",
		llm=llm,
		browser=browser,
		generate_gif="./my_agent_history_playwright.gif")

	try:
		history = await agent.run()

		print(f"Number of steps: {history.number_of_steps()}")
		print(f"URLs visited: {history.urls()}")
		print(f"Final result: {history.final_result()}")

		return history
	finally:
		# Explicit cleanup to avoid Windows asyncio warnings
		if hasattr(agent, 'browser_session'):
			await agent.browser_session.kill()
		await asyncio.sleep(5)

if __name__ == "__main__":
    history = asyncio.run(example())