"""
Collections Orchestrator Agent
================================
Deployable to AgentCore Runtime via the Multitenant Agentic Platform dashboard.

Dashboard settings:
  - GitHub Repository: your-org/loan-collections-agents
  - File Path: agents/collections-orchestrator/main.py
  - Branch: main

Trust Gap Barrier: #1 Shadow AI (+ coordinates all 5 barriers)
AgentCore Services: Runtime, Gateway, Identity, Memory, Observability

This is the master orchestrator that coordinates the full collections workflow.
It delegates to the specialized agents (Identity, Hardship, Compliance) and
enforces the workflow sequence defined by the 10-section policy.

In a production Multitenant Platform deployment, this agent would use
agent-as-tool patterns or A2A protocol to invoke the other agents running
on separate AgentCore Runtime instances.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from strands import Agent
from bedrock_agentcore import BedrockAgentCoreApp

# Import ALL tools for the orchestrator
# In production, these would be accessed via AgentCore Gateway (MCP)
# Import from individual tool directories
import sys, os
_tools = os.path.join(os.path.dirname(__file__), "..", "..", "tools")
sys.path.insert(0, os.path.join(_tools, "identity-verification")); from tool import verify_customer_identity
sys.path.insert(0, os.path.join(_tools, "loan-status")); from tool import check_loan_status
sys.path.insert(0, os.path.join(_tools, "deferment-history")); from tool import check_deferment_history
sys.path.insert(0, os.path.join(_tools, "hardship-recorder")); from tool import record_hardship
sys.path.insert(0, os.path.join(_tools, "offer-deferment")); from tool import offer_deferment
sys.path.insert(0, os.path.join(_tools, "offer-modified-plan")); from tool import offer_modified_plan
sys.path.insert(0, os.path.join(_tools, "offer-settlement")); from tool import offer_settlement
sys.path.insert(0, os.path.join(_tools, "repossession-check")); from tool import check_repossession_eligibility
sys.path.insert(0, os.path.join(_tools, "compliance-logger")); from tool import log_interaction
sys.path.insert(0, os.path.join(_tools, "fair-lending-validator")); from tool import validate_fair_lending


SYSTEM_PROMPT = """You are the Collections Orchestrator Agent for a loan collections system.

You coordinate the ENTIRE collections workflow by following a strict sequence.
You have access to all tools, but you MUST follow the workflow order.

## WORKFLOW SEQUENCE (MUST follow in order)

### STEP 1: Identity Verification (Section 2)
- You MUST verify customer identity FIRST using verify_customer_identity.
- You MUST use at least 2 of 5 approved methods.
- If verification FAILS → TERMINATE. Do NOT proceed. Do NOT disclose account info.

### STEP 2: Loan Status Check (Section 1)
- Call check_loan_status to understand the delinquency situation.
- Note the delinquency_days — this drives all subsequent decisions.

### STEP 3: Hardship Assessment (Section 3)
- If customer claims hardship, MUST document it via record_hardship.
- Ask for the specific reason. Do not skip this.

### STEP 4: Resolution Eligibility (Sections 4-6)
Based on delinquency_days, determine eligible options:
- 30-90 days + no recent deferment + ≤1 modification → Deferment eligible
- 30-120 days → Modified payment plan eligible (min 50% of original, max 6 months)
- 90+ days + vehicle not repossessed → Settlement eligible (REQUIRES SUPERVISOR APPROVAL)
- 60+ days + all options declined → Repossession eligible

CRITICAL RULES:
- MUST NOT offer settlement if < 90 days delinquent
- MUST NOT offer deferment if customer had one in past 12 months
- MUST NOT initiate repossession if < 60 days delinquent
- Settlement MUST be escalated to supervisor BEFORE communicating to customer

### STEP 5: Present Resolution
- Present eligible options to the customer in order of least severity.
- Clearly explain terms and consequences.

### STEP 6: Compliance Documentation (Sections 8-9)
- MUST log ALL 6 required fields via log_interaction.
- MUST validate fair lending via validate_fair_lending.
- Decision factors MUST be ONLY: loan_status, payment_history, delinquency_duration, hardship_reason.
- ANY missing field = NON-COMPLIANT interaction.

## GOVERNANCE CONTROLS ACTIVE
1. Shadow AI: All tool calls route through AgentCore Gateway (MCP). No shadow access.
2. Identity (KYA): Your agent identity is verified. Each tool call is attributed to you.
3. Data Exfiltration: Bedrock Guardrails redact PII. Automated Reasoning validates responses.
4. Governance: Cedar policies block invalid tool calls at the Gateway boundary.
5. Audit: OTEL traces every decision. 13 evaluators + custom compliance evaluators run continuously.

You MUST NOT skip any step. You MUST NOT proceed past Step 1 if verification fails.
"""

orchestrator_agent = Agent(
    model="us.anthropic.claude-sonnet-4-20250514-v1:0",
    tools=[
        # Identity tools
        verify_customer_identity,
        # Assessment tools
        check_loan_status,
        check_deferment_history,
        record_hardship,
        offer_deferment,
        offer_modified_plan,
        offer_settlement,
        check_repossession_eligibility,
        # Compliance tools
        log_interaction,
        validate_fair_lending,
            ],
    system_prompt=SYSTEM_PROMPT,
)

app = BedrockAgentCoreApp()


@app.entrypoint
def handle_request(payload):
    """
    AgentCore Runtime entrypoint for the Collections Orchestrator.

    Expected payload:
    {
        "prompt": "Customer ACC-12345 is calling about their delinquent loan.
                   They say their date of birth is 1985-03-15 and last 4 SSN is 4567.
                   They lost their job and want to discuss options.",
        "customer_id": "ACC-12345",
        "tenant_id": "servicer-001"  # For multi-tenant isolation
    }
    """
    user_input = payload.get("prompt", "")
    customer_id = payload.get("customer_id", "unknown")
    tenant_id = payload.get("tenant_id", "default")

    contextualized_input = (
        f"[Tenant: {tenant_id} | Customer: {customer_id}]\n\n{user_input}"
    )

    response = orchestrator_agent(contextualized_input)
    return {
        "response": response.message,
        "agent": "collections-orchestrator",
        "tenant_id": tenant_id,
        "customer_id": customer_id,
    }


if __name__ == "__main__":
    print("=" * 60)
    print("Collections Orchestrator Agent - Local Test")
    print("=" * 60)

    # Full scenario: 95-day delinquent loan, customer claims job loss
    test_input = (
        "Customer ACC-12345 is calling about their delinquent loan. "
        "They provided their date of birth as 1985-03-15 and their "
        "last four SSN digits as 4567. "
        "They say they lost their job 3 months ago and want to discuss "
        "what options are available to them."
    )
    print(f"\nInput: {test_input}\n")
    print("-" * 60)

    response = orchestrator_agent(test_input)
    print(f"\nResponse:\n{response.message}")
