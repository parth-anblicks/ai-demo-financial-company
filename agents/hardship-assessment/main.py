"""
Hardship Assessment Agent
==========================
Deployable to AgentCore Runtime via the Multitenant Agentic Platform dashboard.

Dashboard settings:
  - GitHub Repository: your-org/loan-collections-agents
  - File Path: agents/hardship-assessment/main.py
  - Branch: main

Trust Gap Barriers: #3 Data Exfiltration + #4 Governance Vacuum
AgentCore Services: Runtime, Gateway (MCP), Guardrails (Automated Reasoning), Policy (Cedar)
Policy Sections: Sections 3, 4, 5, 6, 7

NOTE: The offer_settlement tool is gated by a Cedar policy at the AgentCore Gateway.
If delinquency_days < 90, the tool call is BLOCKED at the infrastructure level,
regardless of what this agent's LLM decides. This is deterministic policy enforcement
operating OUTSIDE the agent's reasoning loop.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from strands import Agent
from bedrock_agentcore import BedrockAgentCoreApp
# Import from individual tool directories
import sys, os
_tools = os.path.join(os.path.dirname(__file__), "..", "..", "tools")
sys.path.insert(0, os.path.join(_tools, "loan-status")); from tool import check_loan_status
sys.path.insert(0, os.path.join(_tools, "deferment-history")); from tool import check_deferment_history
sys.path.insert(0, os.path.join(_tools, "hardship-recorder")); from tool import record_hardship
sys.path.insert(0, os.path.join(_tools, "offer-deferment")); from tool import offer_deferment
sys.path.insert(0, os.path.join(_tools, "offer-modified-plan")); from tool import offer_modified_plan
sys.path.insert(0, os.path.join(_tools, "offer-settlement")); from tool import offer_settlement
sys.path.insert(0, os.path.join(_tools, "repossession-check")); from tool import check_repossession_eligibility


# Load SOP
SOP_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "sops", "hardship-assessment.md")
with open(SOP_PATH, "r") as f:
    HARDSHIP_SOP = f.read()

SYSTEM_PROMPT = f"""You are the Hardship Assessment Agent for a loan collections system.

Your responsibility is to assess customer hardship and determine eligible
resolution options per Sections 3-7 of the Loan Collections Decision Policy.

GOVERNANCE CONTROLS IN EFFECT:
1. Cedar policies at the Gateway will BLOCK tool calls that violate policy rules
   (e.g., offering a settlement for a loan < 90 days delinquent).
2. Automated Reasoning checks validate your recommendations against the full
   10-section policy with mathematical proof.
3. PII in customer data is redacted by Bedrock Guardrails before reaching your context.
4. Every tool call is logged, metered, and attributed to your agent identity.

You MUST follow the SOP below. MUST = mandatory, MUST NOT = prohibited.
If you are unsure about a rule, err on the side of NOT offering the resolution
and escalate to a human supervisor.

{HARDSHIP_SOP}
"""

hardship_agent = Agent(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    tools=[
        check_loan_status,
        check_deferment_history,
        record_hardship,
        offer_deferment,
        offer_modified_plan,
        offer_settlement,
        check_repossession_eligibility,
    ],
    system_prompt=SYSTEM_PROMPT,
)

app = BedrockAgentCoreApp()


@app.entrypoint
def handle_request(payload):
    """
    AgentCore Runtime entrypoint.

    Expected payload:
    {
        "prompt": "Customer ACC-12345 has been verified. They claim job loss
                   hardship. What resolution options are available?",
        "customer_id": "ACC-12345",
        "identity_verified": true
    }
    """
    user_input = payload.get("prompt", "")
    customer_id = payload.get("customer_id", "unknown")
    identity_verified = payload.get("identity_verified", False)

    if not identity_verified:
        return {
            "response": "ERROR: Customer identity has not been verified. "
            "The Identity Verification Agent must confirm identity before "
            "hardship assessment can proceed. Per Section 2.",
            "agent": "hardship-assessment",
        }

    contextualized_input = f"[Customer ID: {customer_id}, Identity: VERIFIED] {user_input}"
    response = hardship_agent(contextualized_input)
    return {"response": response.message, "agent": "hardship-assessment"}


if __name__ == "__main__":
    print("=" * 60)
    print("Hardship Assessment Agent - Local Test")
    print("=" * 60)

    test_input = (
        "Customer ACC-12345 has been verified. They say they lost their job "
        "3 months ago and can't make the monthly payments. What resolution "
        "options can we offer?"
    )
    print(f"\nInput: {test_input}\n")

    response = hardship_agent(test_input)
    print(f"\nResponse: {response.message}")
