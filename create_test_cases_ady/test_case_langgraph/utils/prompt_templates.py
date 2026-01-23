"""
Centralized prompt templates for all nodes.
"""


class PromptTemplates:
    """All prompts in one place for easy maintenance."""

    FEATURE_ANALYSIS = """You are a senior QA analyst analyzing a feature for test coverage.

FEATURE CONTEXT:
Name: {feature_name}
Description: {feature_description}
Platform: {platform}

USER GUIDE:
{user_guide_text}

FEATURE SUMMARY:
{feature_summary_text}

SCREEN CONTRACTS:
{screen_contracts_json}

YOUR TASK:
Analyze this feature and extract:

1. **User Flows**: All possible user journeys (happy paths, alternatives, error paths)
2. **Test Scenarios**: What needs testing?

Return ONLY valid JSON (no markdown):
{{
  "user_flows": [
    {{
      "flow_name": "Successful login",
      "steps": ["Navigate to login", "Enter credentials", "Click login"],
      "flow_type": "happy_path"
    }}
  ],
  "test_scenarios": [
    {{
      "scenario_name": "Valid login",
      "category": "positive",
      "priority": 1,
      "description": "User logs in with valid credentials"
    }}
  ]
}}
"""

    TEST_GENERATION = """You are an expert test case designer.

FEATURE: {feature_name}
PLATFORM: {platform}

ANALYSIS:
{feature_analysis}

SCREEN CONTRACTS:
{screen_contracts_json}

ALREADY COVERED SCENARIOS:
{covered_scenarios}

ALREADY USED TEST TITLES:
{covered_test_titles}

PREVIOUS FEEDBACK FROM REFLEXION AGENT:
{reflexion_feedback}

REJECTED TEST CASES (DO NOT regenerate these):
{rejected_summaries}

YOUR TASK:
Generate {batch_size} NEW, HIGH-QUALITY test cases that:
- Cover scenarios NOT yet tested
- Address feedback from Reflexion agent
- Are specific and executable
- Include realistic test data
- Have UNIQUE titles (different from already used ones)

Return ONLY valid JSON array (no markdown):
[
  {{
    "TC_ID": "TC_TEMP_001",
    "Testcase name": "Login with valid email and password",
    "category": "positive",
    "Precondition": "User is on login page",
    "Test steps": [
      "Enter 'user@example.com' in email field",
      "Enter 'Password123!' in password field",
      "Click 'Login' button"
    ],
    "Test data": {{"email": "user@example.com", "password": "Password123!"}},
    "Expected Result": "User is redirected to dashboard",
    "scenario_covered": "Valid login"
  }}
]

CRITICAL:
- Reference actual UI elements from screen contracts
- Make steps actionable (e.g., "Click the 'Submit' button")
- Use realistic test data
- Each test case must have a UNIQUE "Testcase name"
"""

    REFLEXION_EVALUATION = """You are a strict QA reviewer evaluating test case quality.

FEATURE: {feature_name}

NEWLY GENERATED TEST CASES:
{current_batch_json}

ALREADY APPROVED TEST CASES:
{approved_testcases_json}

EVALUATION CRITERIA:

1. **AUTHENTICITY** - Is it a real, valid test case?
   - Steps are specific and actionable
   - Test data is realistic
   - Expected result is verifiable

2. **REDUNDANCY** - Is it duplicate/too similar to approved tests?
   - Different scenario, not just rephrased
   - Adds new coverage value

3. **QUALITY** - Is it well-written?
   - Clear preconditions
   - Logical step sequence
   - Proper test data
   - Testable assertions

YOUR TASK:
For EACH test case, decide: APPROVE or REJECT

Return ONLY valid JSON (no markdown):
{{
  "evaluations": [
    {{
      "TC_ID": "TC_TEMP_001",
      "decision": "APPROVE",
      "authenticity_score": 9,
      "redundancy_score": 9,
      "quality_score": 8,
      "issues": [],
      "reason": "Well-written positive test case with clear steps"
    }},
    {{
      "TC_ID": "TC_TEMP_002",
      "decision": "REJECT",
      "authenticity_score": 5,
      "redundancy_score": 3,
      "quality_score": 6,
      "issues": ["Too similar to TC001", "Vague expected result"],
      "reason": "Redundant with existing approved test"
    }}
  ],
  "overall_feedback": "Good progress. Need more negative test cases and boundary conditions.",
  "suggestions_for_next_batch": [
    "Add tests for invalid inputs",
    "Cover edge cases like empty fields",
    "Test error messages"
  ]
}}

SCORING GUIDE:
- 8-10: Excellent
- 6-7: Good (but may have minor issues)
- 4-5: Mediocre (significant issues)
- 1-3: Poor

APPROVE if all scores >= 6 AND no critical redundancy.
REJECT otherwise.
"""

    @staticmethod
    def build_test_case_prompt(
        *,
        feature_name: str,
        feature_description: str,
        user_guide_text: str,
        feature_summary_text: str,
        screen_contracts_json: str,
        max_cases: int,
        platform: str,
    ) -> str:
        """
        High-fidelity prompt for generating UI test cases.
        """
        return f"""
You are a senior QA engineer and test architect specialising in end-to-end UI testing for enterprise applications.

Your task is to design a compact but high-quality test suite for a SINGLE feature of an application.

The test suite must be returned as pure JSON (no markdown, no comments), following the exact schema described below.

========================
FEATURE CONTEXT
========================

Feature name:
{feature_name}

Feature description (business purpose and high-level behaviour):
{feature_description}

High-level user guide for the main flow (happy path):
{user_guide_text}

Abstract execution summary for this feature (screens & actions actually observed by the crawler, may be noisy but useful for nuance):
{feature_summary_text}

Screen contracts (summarised UI structure for key {"pages" if platform == "web" else "screens"} in this feature).
Each entry lists a page heading / screen and its most important controls:
{screen_contracts_json}

The "screen contracts" give you field labels, types, and whether they look required.
Use these to design realistic and meaningful tests, especially for forms.

========================
TEST CASE DESIGN GOALS
========================

Your goal is to produce a diverse set of UI test cases that:

- Thoroughly exercise this feature end-to-end.
- Follow the main happy path described in the USER GUIDE, but also explore meaningful variations.
- Include positive, negative, and edge-case scenarios.
- Are realistic and executable on the actual UI, based on headings / labels / controls from the screen contracts.

You must design AT MOST {max_cases} test cases.

Rough target distribution:
- 30–40% positive cases
- 40–50% negative cases
- 10–20% edge cases

Always include at least:
- 1 full happy-path positive test that closely follows the user guide.
- 2–3 negative tests focused on validation / mandatory fields / wrong formats.
- 1–2 edge tests focused on boundary values and navigation quirks (back, relaunch, etc.).

========================
ACTIONS & BEHAVIOUR
========================

The underlying execution engine supports these high-level actions:

- "tap": clicking / tapping on a control (buttons, links, tiles, icons).
- "fill": entering text/value into an input, textarea, or similar control.
- "verify": checking that something is visible or that we navigated to the right screen.
- "back": using browser Back, app Back, or a visible Back button to go to the previous screen.
- "relaunch": closing and reopening the app (or refreshing the web app) so the feature is started from a clean state.

You do NOT need to use these keywords directly in the JSON, but your test steps SHOULD describe actions that can be mapped to them.

========================
TEST CASE CATEGORIES
========================

You must tag EACH test case with a "category" field:

- "positive"
- "negative"
- "edge"

Use these meanings:

- "positive": valid sequences + valid data, expected to succeed.
- "negative": intentionally invalid inputs or sequences, expected to trigger validation or rejection.
- "edge": boundary/limit conditions or navigation quirks (back, relaunch, double-click, etc.) that must still be handled safely.

========================
TEST CASE FORMAT (SCHEMA)
========================

You must output a JSON array of objects. No extra text, no markdown.

Each object MUST have EXACTLY these fields:

- "TC_ID": string
    - Format: "TC001", "TC002", ... 3-digit zero-padded.
- "category": string
    - One of: "positive", "negative", "edge".
- "Testcase name": string
    - Short descriptive name.
- "Precondition": string
    - Single sentence describing start state.
- "Test steps": array of strings
    - 4 to 15 steps.
    - Each step a concise imperative sentence describing exactly one action or verification.
- "Test data": object
    - Map from field label / logical name to example value.
- "Expected Result": string
    - Single concise sentence describing main outcome (success or error).

IMPORTANT CONSTRAINTS:
- Do NOT include comments or explanation outside the JSON.
- Do NOT include markdown formatting.
- Keep each test case self-contained and non-duplicate.
- Reuse realistic sample values inferred from the user guide and screen contracts whenever possible.

========================
OUTPUT
========================

Now, using all the information above, produce AT MOST {max_cases} high-quality, non-duplicated test cases for this single feature, as a JSON array of objects following the exact schema.
Do not include any text before or after the JSON.
""".strip()
