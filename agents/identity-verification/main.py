"""
Identity Verification Agent
============================
Deployable to AgentCore Runtime via the Multitenant Agentic Platform dashboard.

Dashboard settings:
  - GitHub Repository: your-org/loan-collections-agents
  - File Path: agents/identity-verification/main.py
  - Branch: main

Trust Gap Barrier: #2 Identity Crisis (KYA)
AgentCore Services: Runtime, Identity, Memory
Policy Sections: Section 2 (Identity Verification)
"""

import os
import sys

# Add project root to path for tool imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from strands import Agent
from bedrock_agentcore import BedrockAgentCoreApp
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools", "identity-verification")); from tool import verify_customer_identity


# Load SOP as system prompt
SOP_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "sops", "identity-verification.md")
with open(SOP_PATH, "r") as f:
    IDENTITY_SOP = f.read()

SYSTEM_PROMPT = f"""You are the Identity Verification Agent for a loan collections system.

Your ONLY responsibility is to verify customer identity per Section 2 of the
Loan Collections Decision Policy. You operate under strict governance controls:

- You have a scoped identity (KYA - Know Your Agent) that only permits access
  to identity verification tools.
- You CANNOT access loan status, settlement, or repossession tools.
- Every action you take is logged and attributed to your agent identity.

Follow the SOP below precisely. Use RFC 2119 keywords as hard constraints:
MUST = mandatory, MUST NOT = prohibited, SHOULD = recommended.

{IDENTITY_SOP}
"""

# Create the Strands agent
identity_agent = Agent(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    tools=[verify_customer_identity],
    system_prompt=SYSTEM_PROMPT,
)

# Wrap with AgentCore Runtime
app = BedrockAgentCoreApp()


@app.entrypoint
def handle_request(payload):
    """
    AgentCore Runtime entrypoint.

    Expected payload:
    {
        "prompt": "I need to verify customer ACC-12345. They provided
                   their date of birth as 1985-03-15 and SSN last 4 as 4567.",
        "customer_id": "ACC-12345"  # optional, for tenant context
    }
    """
    user_input = payload.get("prompt", "")
    customer_id = payload.get("customer_id", "unknown")

    # Include tenant/customer context for multi-tenant isolation
    contextualized_input = (
        f"[Customer ID: {customer_id}] {user_input}"
        if customer_id != "unknown"
        else user_input
    )

    response = identity_agent(contextualized_input)
    return {"response": response.message, "agent": "identity-verification"}


# For local development
if __name__ == "__main__":
    # Local test
    print("=" * 60)
    print("Identity Verification Agent - Local Test")
    print("=" * 60)

    test_input = (
        "I need to discuss a collections matter with customer ACC-12345. "
        "They provided their date of birth as 1985-03-15 and their "
        "last four SSN digits as 4567."
    )
    print(f"\nInput: {test_input}\n")

    response = identity_agent(test_input)
    print(f"\nResponse: {response.message}")
