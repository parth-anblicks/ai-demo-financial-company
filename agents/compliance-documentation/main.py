"""
Compliance Documentation Agent
================================
Deployable to AgentCore Runtime via the Multitenant Agentic Platform dashboard.

Dashboard settings:
  - GitHub Repository: your-org/loan-collections-agents
  - File Path: agents/compliance-documentation/main.py
  - Branch: main

Trust Gap Barrier: #5 Audit Blind Spots
AgentCore Services: Runtime, Observability (OTEL), Evaluations
Policy Sections: Sections 8, 9

This agent runs AFTER every collections interaction to ensure 100% compliance
documentation. It replaces quarterly post-hoc sampling with real-time validation.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from strands import Agent
from bedrock_agentcore import BedrockAgentCoreApp
# Import from individual tool directories
import sys, os
_tools = os.path.join(os.path.dirname(__file__), "..", "..", "tools")
sys.path.insert(0, os.path.join(_tools, "compliance-logger")); from tool import log_interaction
sys.path.insert(0, os.path.join(_tools, "fair-lending-validator")); from tool import validate_fair_lending


SOP_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "sops", "compliance-documentation.md")
with open(SOP_PATH, "r") as f:
    COMPLIANCE_SOP = f.read()

SYSTEM_PROMPT = f"""You are the Compliance Documentation Agent for a loan collections system.

Your responsibility is to ensure every collections interaction is fully documented
per Section 9 and validated for fair lending compliance per Section 8.

GOVERNANCE CONTROLS IN EFFECT:
1. AgentCore Observability traces every action you take via OTEL.
2. Custom evaluators continuously monitor Section 9 completeness.
3. A Fair Lending Audit evaluator checks for disparate impact patterns.
4. CloudWatch dashboards surface compliance rates in real-time.

CRITICAL RULES:
- You MUST log ALL 6 required fields for every interaction.
- If ANY field is missing, you MUST flag the interaction as NON-COMPLIANT.
- You MUST validate that resolution decisions are based ONLY on permitted factors.
- If you detect a fair lending violation, you MUST escalate immediately.

{COMPLIANCE_SOP}
"""

compliance_agent = Agent(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    tools=[log_interaction, validate_fair_lending],
    system_prompt=SYSTEM_PROMPT,
)

app = BedrockAgentCoreApp()


@app.entrypoint
def handle_request(payload):
    """
    AgentCore Runtime entrypoint.

    Expected payload:
    {
        "prompt": "Log the interaction for customer ACC-12345...",
        "customer_id": "ACC-12345",
        "interaction_data": {
            "identity_verification_method": "ssn_last4, date_of_birth",
            "identity_verification_outcome": "verified",
            "hardship_reason": "job loss",
            "resolution_options_discussed": "deferment, modified plan, settlement",
            "resolution_option_offered_or_declined": "settlement offered, pending supervisor",
            "next_action_date": "2025-04-15",
            "supervisor_approval_reference": "SUP-ACC-12345-20250401"
        }
    }
    """
    user_input = payload.get("prompt", "")
    customer_id = payload.get("customer_id", "unknown")
    interaction_data = payload.get("interaction_data", {})

    # If structured data is provided, include it in the prompt
    if interaction_data:
        data_str = "\n".join(f"  - {k}: {v}" for k, v in interaction_data.items())
        contextualized_input = (
            f"[Customer ID: {customer_id}]\n"
            f"Interaction data to log:\n{data_str}\n\n"
            f"Additional context: {user_input}"
        )
    else:
        contextualized_input = f"[Customer ID: {customer_id}] {user_input}"

    response = compliance_agent(contextualized_input)
    return {"response": response.message, "agent": "compliance-documentation"}


if __name__ == "__main__":
    print("=" * 60)
    print("Compliance Documentation Agent - Local Test")
    print("=" * 60)

    test_input = (
        "Log the following interaction for customer ACC-12345:\n"
        "- Identity verified using ssn_last4 and date_of_birth\n"
        "- Customer claimed job loss as hardship\n"
        "- Discussed deferment, modified plan, and settlement options\n"
        "- Settlement offered at $18,750 pending supervisor approval\n"
        "- Supervisor reference: SUP-ACC-12345-20250401\n"
        "- Next action date: 2025-04-15\n"
        "\n"
        "Also validate that the decision was based on permitted factors: "
        "loan_status, delinquency_duration, documented_hardship_reason"
    )
    print(f"\nInput: {test_input}\n")

    response = compliance_agent(test_input)
    print(f"\nResponse: {response.message}")
