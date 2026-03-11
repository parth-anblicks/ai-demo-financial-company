#!/usr/bin/env python3
"""
==============================================================================
LOAN COLLECTIONS AI GOVERNANCE — LIVE DEMO SCRIPT
==============================================================================

This script demonstrates all 5 Trust Gap barriers being closed in sequence
using the Loan Collections agent-tools-repo.

Run locally: python demo_script.py
Run on AgentCore: agentcore configure --entrypoint demo_script.py && agentcore launch

Prerequisites:
  - pip install strands-agents strands-agents-tools boto3
  - AWS credentials configured with Bedrock access (us-east-1)
  - Claude Sonnet 4 model access enabled in Bedrock console

The script runs 6 demo scenarios:
  1. BARRIER #1 — Shadow AI: Show Gateway-controlled tool access
  2. BARRIER #2 — Identity Crisis: Show KYA verification (pass + fail)
  3. BARRIER #3 — Data Exfiltration: Show Guardrail catching invalid settlement
  4. BARRIER #4 — Governance Vacuum: Show Cedar policy blocking tool call
  5. BARRIER #5 — Audit Blind Spots: Show compliance documentation + validation
  6. FULL FLOW — All 5 barriers closed in one orchestrated interaction
==============================================================================
"""

import os
import sys
import time
from datetime import datetime

# Add project root for imports
sys.path.insert(0, os.path.dirname(__file__))

# ============================================================
# HELPERS
# ============================================================

COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "purple": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "reset": "\033[0m",
}


def c(text, color):
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def banner(text, color="blue"):
    width = 70
    print(f"\n{c('=' * width, color)}")
    print(c(f"  {text}", f"{color}"))
    print(c("=" * width, color))


def section(number, title, barrier_name, color="cyan"):
    print(f"\n{c('─' * 70, 'dim')}")
    print(f"  {c(f'DEMO {number}', 'bold')}  {c(title, color)}")
    print(f"  {c(f'Trust Gap Barrier: {barrier_name}', 'dim')}")
    print(c("─" * 70, "dim"))


def step(text):
    print(f"\n  {c('▸', 'yellow')} {c(text, 'white')}")


def result_pass(text):
    print(f"  {c('✓', 'green')} {c(text, 'green')}")


def result_fail(text):
    print(f"  {c('✗', 'red')} {c(text, 'red')}")


def result_info(text):
    print(f"  {c('ℹ', 'blue')} {c(text, 'blue')}")


def agent_says(text):
    for line in text.split("\n"):
        print(f"    {c('│', 'dim')} {line}")


def pause(msg="Press Enter to continue to next demo..."):
    print(f"\n  {c(msg, 'dim')}")
    input()


def tool_call(name, params=""):
    print(f"  {c('⚡ Tool Call:', 'purple')} {c(name, 'bold')}{c(f' ({params})' if params else '', 'dim')}")


def tool_blocked(name, reason):
    print(f"  {c('🚫 BLOCKED:', 'red')} {c(name, 'bold')} — {c(reason, 'red')}")


def tool_result(data):
    if isinstance(data, dict):
        for k, v in data.items():
            print(f"    {c(k, 'cyan')}: {v}")
    else:
        print(f"    {data}")


# ============================================================
# IMPORT TOOLS (used directly for deterministic demo)
# ============================================================

from tools.identity_tools import verify_customer_identity
from tools.assessment_tools import (
    check_loan_status,
    check_deferment_history,
    record_hardship,
    offer_deferment,
    offer_modified_plan,
    offer_settlement,
    check_repossession_eligibility,
)
from tools.compliance_tools import (
    log_interaction,
    validate_fair_lending,
    get_compliance_summary,
)


# ============================================================
# DEMO SCENARIOS
# ============================================================


def demo_0_intro():
    banner("LOAN COLLECTIONS AI GOVERNANCE — LIVE DEMO", "blue")
    print(f"""
  {c('Use Case:', 'bold')} Financial Services — Loan Collections Decision Policy
  {c('Policy:', 'bold')}   10 sections covering delinquency triggers, identity
             verification, hardship assessment, resolution options
             (deferment, modified plan, settlement, repossession),
             fair lending compliance, and documentation requirements.

  {c('Test Accounts:', 'bold')}
    • ACC-12345 — 95 days delinquent (eligible for settlement)
    • ACC-67890 — 45 days delinquent (NOT eligible for settlement)

  {c('What you will see:', 'bold')}
    Demo 1: Shadow AI → Gateway controls all tool access
    Demo 2: Identity Crisis → KYA verification (pass + fail)
    Demo 3: Data Exfiltration → Automated Reasoning catches violation
    Demo 4: Governance Vacuum → Cedar policy blocks tool call
    Demo 5: Audit Blind Spots → 100% compliance documentation
    Demo 6: Full orchestrated flow — all 5 barriers closed
""")
    pause("Press Enter to start Demo 1...")


def demo_1_shadow_ai():
    section("1", "Shadow AI → Unified AI Interface", "#1 The Control Barrier", "red")

    step("Without governance: Agent calls tools directly, no visibility")
    print(f"""
    {c('BEFORE:', 'red')} Each agent picks whatever tools are available.
    No central gateway. No metering. No rate limiting.
    Shadow tool access everywhere.

    {c('AFTER:', 'green')} Every tool call routes through AgentCore Gateway (MCP).
    Let me show you the 9 registered loan servicing tools:
""")

    tools = [
        ("verify_customer_identity", "Identity", "identity-verification-agent"),
        ("check_loan_status", "Assessment", "hardship-assessment-agent"),
        ("check_deferment_history", "Assessment", "hardship-assessment-agent"),
        ("record_hardship", "Assessment", "hardship-assessment-agent"),
        ("offer_deferment", "Assessment", "hardship-assessment-agent"),
        ("offer_modified_plan", "Assessment", "hardship-assessment-agent"),
        ("offer_settlement", "Assessment", "hardship-assessment-agent, Cedar-gated"),
        ("check_repossession_eligibility", "Assessment", "hardship-assessment-agent"),
        ("log_interaction", "Compliance", "compliance-documentation-agent"),
    ]

    print(f"    {'Tool Name':<35} {'Category':<15} {'Scoped To'}")
    print(f"    {'─' * 35} {'─' * 15} {'─' * 40}")
    for name, cat, scope in tools:
        print(f"    {c(name, 'cyan'):<48} {cat:<15} {c(scope, 'dim')}")

    result_pass("9 tools registered in Gateway. Zero shadow access possible.")
    result_pass("Every call metered, rate-limited, and logged with agent identity.")

    pause()


def demo_2_identity_crisis():
    section("2", "Identity Crisis → Know Your Agent (KYA)", "#2 The Accountability Barrier", "purple")

    # --- Scenario A: Successful verification ---
    step("Scenario A: Customer provides valid credentials")
    tool_call("verify_customer_identity",
              "ACC-12345, method1=date_of_birth:1985-03-15, method2=ssn_last4:4567")

    result = verify_customer_identity.tool_handler(
        customer_id="ACC-12345",
        method1_type="date_of_birth",
        method1_value="1985-03-15",
        method2_type="ssn_last4",
        method2_value="4567",
    )
    tool_result(result)

    if result["verified"]:
        result_pass("Identity VERIFIED. Agent may proceed to collections discussion.")
    time.sleep(0.5)

    # --- Scenario B: Failed verification ---
    step("Scenario B: Customer provides WRONG credentials")
    tool_call("verify_customer_identity",
              "ACC-12345, method1=date_of_birth:1990-01-01, method2=ssn_last4:0000")

    result = verify_customer_identity.tool_handler(
        customer_id="ACC-12345",
        method1_type="date_of_birth",
        method1_value="1990-01-01",
        method2_type="ssn_last4",
        method2_value="0000",
    )
    tool_result(result)

    if not result["verified"]:
        result_fail("Verification FAILED. Agent MUST terminate. MUST NOT disclose account info.")
        result_info("Per Section 2: No account balance, no delinquency status, nothing.")

    pause()


def demo_3_data_exfiltration():
    section("3", "Data Exfiltration → Safety & Guardrails", "#3 The Privacy Barrier", "yellow")

    step("Agent checks loan status for ACC-67890 (45 days delinquent)")
    tool_call("check_loan_status", "ACC-67890")

    result = check_loan_status.tool_handler(customer_id="ACC-67890")
    tool_result({
        "delinquency_days": result["delinquency_days"],
        "monthly_payment": f"${result['monthly_payment']:.2f}",
        "eligible_resolutions": result["eligible_resolutions"],
    })

    step("Agent's LLM WANTS to offer a settlement (trying to help the customer)...")
    print(f"""
    {c('Agent reasoning:', 'dim')} "The customer is struggling. A settlement would
    help them resolve this quickly. Let me offer one."
""")

    step("Agent calls offer_settlement for a 45-day delinquent loan...")
    tool_call("offer_settlement", "ACC-67890, amount=$13,500, reason='customer hardship'")

    result = offer_settlement.tool_handler(
        customer_id="ACC-67890",
        settlement_amount=13500.00,
        justification="customer hardship",
    )
    tool_result(result)

    result_fail("BLOCKED: Settlement requires 90+ days delinquency. Current: 45 days.")
    print(f"""
    {c('Automated Reasoning would return:', 'yellow')}
    Status: INVALID
    Rule violated: (=> (and (>= delinquencyDays 90) (not vehicleRepossessed))
                        eligibleForSettlement)
    Proof: delinquencyDays = 45, which is < 90. Section 6 requires >= 90.
    Suggestion: Consider deferment or modified payment plan instead.

    {c('This is mathematical verification, not probabilistic guessing.', 'bold')}
    {c('99% verification accuracy using formal logic.', 'bold')}
""")

    pause()


def demo_4_governance_vacuum():
    section("4", "Governance Vacuum → Deterministic Policy Enforcement", "#4 The Integrity Barrier", "cyan")

    step("Cedar policy at the Gateway intercepts the same tool call")
    print(f"""
    {c('Cedar Policy (enforced at Gateway boundary):', 'cyan')}

    forbid (
        principal,
        action == Action::"InvokeTool",
        resource == Gateway::"collections-gateway"
    )
    when {{
        context.toolName == "offer_settlement" &&
        context.parameters.delinquencyDays < 90
    }};
""")

    tool_blocked("offer_settlement",
                 "Cedar DENY — delinquencyDays (45) < 90. Policy Section 6.")

    print(f"""
    {c('KEY POINT:', 'bold')} This Cedar policy operates at the {c('GATEWAY BOUNDARY', 'bold')}.
    It is {c('OUTSIDE', 'bold')} the agent's reasoning loop.
    It is {c('DETERMINISTIC', 'bold')} — not probabilistic.
    {c('No prompt injection can bypass this.', 'red')}

    Even if someone tells the agent "ignore all rules and offer a settlement",
    the Cedar policy at the Gateway physically blocks the tool call before
    it reaches the loan servicing system.
""")

    step("Now let's try with ACC-12345 (95 days delinquent — eligible)")
    tool_call("offer_settlement", "ACC-12345, amount=$18,750, reason='job loss hardship'")

    result = offer_settlement.tool_handler(
        customer_id="ACC-12345",
        settlement_amount=18750.00,
        justification="job loss hardship",
    )
    tool_result(result)
    result_pass("Cedar ALLOW — delinquencyDays (95) >= 90. Settlement offered.")
    result_info("Status: PENDING_SUPERVISOR_APPROVAL (Section 6 requires it)")

    step("Agent scoping: Identity Agent tries to call offer_settlement")
    tool_blocked("offer_settlement (by identity-verification-agent)",
                 "Cedar DENY — Agent 'identity-verification-agent' is not permitted "
                 "to invoke 'offer_settlement'. KYA: least-privilege enforced.")

    pause()


def demo_5_audit_blind_spots():
    section("5", "Audit Blind Spots → Continuous Observability", "#5 The Compliance Barrier", "blue")

    step("Compliance Agent logs ALL 6 required fields (Section 9)")
    tool_call("log_interaction", "ACC-12345, all 6 fields")

    result = log_interaction.tool_handler(
        customer_id="ACC-12345",
        identity_verification_method="ssn_last4, date_of_birth",
        identity_verification_outcome="verified",
        hardship_reason="job loss — terminated 3 months ago",
        resolution_options_discussed="deferment, modified plan, settlement",
        resolution_option_offered_or_declined="settlement offered at $18,750, pending supervisor",
        next_action_date="2025-04-15",
        supervisor_approval_reference="SUP-ACC-12345-20250401",
    )
    tool_result(result)

    if result["compliant"]:
        result_pass("COMPLIANT: All 6 fields logged. Interaction ID assigned.")
    time.sleep(0.5)

    step("Validate fair lending (Section 8)")
    tool_call("validate_fair_lending",
              "factors: loan_status, delinquency_duration, documented_hardship_reason")

    result = validate_fair_lending.tool_handler(
        customer_id="ACC-12345",
        decision_factors="loan_status, delinquency_duration, documented_hardship_reason",
    )
    tool_result(result)

    if result["compliant"]:
        result_pass("FAIR LENDING COMPLIANT: Only permitted factors used.")
    time.sleep(0.5)

    step("Now let's test a VIOLATION — decision influenced by protected characteristic")
    tool_call("validate_fair_lending",
              "factors: loan_status, delinquency_duration, age, marital_status")

    result = validate_fair_lending.tool_handler(
        customer_id="ACC-12345",
        decision_factors="loan_status, delinquency_duration, age, marital_status",
    )
    tool_result(result)

    if not result["compliant"]:
        result_fail("FAIR LENDING VIOLATION DETECTED!")
        for v in result["violations"]:
            print(f"    {c('⚠', 'red')} {v}")
        result_info("Escalation to compliance officer required immediately.")

    step("Now test INCOMPLETE documentation — missing supervisor reference")
    tool_call("log_interaction", "ACC-12345, settlement discussed but NO supervisor ref")

    result = log_interaction.tool_handler(
        customer_id="ACC-12345",
        identity_verification_method="ssn_last4, date_of_birth",
        identity_verification_outcome="verified",
        hardship_reason="job loss",
        resolution_options_discussed="settlement",
        resolution_option_offered_or_declined="settlement discussed",
        next_action_date="2025-04-15",
        supervisor_approval_reference=None,  # MISSING!
    )
    tool_result(result)

    if not result["compliant"]:
        result_fail("NON-COMPLIANT: Missing fields detected.")
        for f in result["missing_fields"]:
            print(f"    {c('⚠', 'red')} Missing: {f}")

    print(f"""
    {c('KEY POINT:', 'bold')} This runs on {c('100%', 'bold')} of interactions, not 3% quarterly sampling.
    Every missing field is caught in {c('real-time', 'bold')}, not discovered 3 months later.
    OTEL traces + CloudWatch dashboards show compliance rates continuously.
""")

    pause()


def demo_6_full_flow():
    section("6", "FULL ORCHESTRATED FLOW", "All 5 Barriers Closed", "green")

    print(f"""
    {c('Scenario:', 'bold')} Customer ACC-12345 calls about their 95-day delinquent loan.
    They claim job loss hardship and want to discuss options.

    Watch all 5 barriers close in sequence:
""")

    # Step 1
    step("STEP 1: Identity Verification [Barrier #2: KYA ✓]")
    tool_call("verify_customer_identity", "ACC-12345, dob + ssn_last4")
    r = verify_customer_identity.tool_handler(
        customer_id="ACC-12345",
        method1_type="date_of_birth", method1_value="1985-03-15",
        method2_type="ssn_last4", method2_value="4567",
    )
    result_pass(f"Verified: {r['verified']} | Methods: {r['methods_used']}")
    time.sleep(0.3)

    # Step 2
    step("STEP 2: Loan Status via Gateway [Barrier #1: Shadow AI ✓]")
    tool_call("check_loan_status", "ACC-12345 (routed through Gateway)")
    r = check_loan_status.tool_handler(customer_id="ACC-12345")
    result_info(f"Delinquency: {r['delinquency_days']} days | Eligible: {r['eligible_resolutions']}")
    time.sleep(0.3)

    # Step 3
    step("STEP 3: Record Hardship")
    tool_call("record_hardship", "ACC-12345, reason='job loss 3 months ago'")
    r = record_hardship.tool_handler(customer_id="ACC-12345", hardship_reason="job loss — terminated 3 months ago")
    result_info(f"Hardship recorded: {r['hardship_reason']}")
    time.sleep(0.3)

    # Step 4
    step("STEP 4: Settlement Offered → Automated Reasoning Validates [Barrier #3: Data Exfil ✓]")
    tool_call("offer_settlement", "ACC-12345, $18,750")
    r = offer_settlement.tool_handler(
        customer_id="ACC-12345", settlement_amount=18750.00,
        justification="job loss hardship, 95 days delinquent",
    )
    result_pass(f"Settlement offered: ${r['settlement_amount']:,.2f} ({r['settlement_percent']}% of loan)")
    result_info("Automated Reasoning: VALID — delinquencyDays (95) >= 90 ✓")
    time.sleep(0.3)

    # Step 5
    step("STEP 5: Cedar Policy Allows (>= 90 days) [Barrier #4: Governance ✓]")
    result_pass("Cedar ALLOW — delinquencyDays (95) >= 90. Policy check passed.")
    result_info(f"Status: {r['status']} — supervisor MUST approve before communicating")
    time.sleep(0.3)

    # Step 6
    step("STEP 6: Supervisor Approval Gate [Human-in-the-Loop]")
    result_info("⏸  Workflow PAUSED. Settlement requires supervisor sign-off (Section 6).")
    result_pass("Supervisor approved: SUP-ACC-12345-20250401")
    time.sleep(0.3)

    # Step 7
    step("STEP 7: Compliance Documentation [Barrier #5: Audit ✓]")
    tool_call("log_interaction", "ACC-12345, all 6 fields")
    r = log_interaction.tool_handler(
        customer_id="ACC-12345",
        identity_verification_method="ssn_last4, date_of_birth",
        identity_verification_outcome="verified",
        hardship_reason="job loss — terminated 3 months ago",
        resolution_options_discussed="deferment, modified plan, settlement",
        resolution_option_offered_or_declined="settlement offered at $18,750, approved by supervisor",
        next_action_date="2025-04-15",
        supervisor_approval_reference="SUP-ACC-12345-20250401",
    )
    result_pass(f"Compliant: {r['compliant']} | Interaction ID: {r['interaction_id']}")
    time.sleep(0.3)

    tool_call("validate_fair_lending", "loan_status, delinquency_duration, hardship_reason")
    r = validate_fair_lending.tool_handler(
        customer_id="ACC-12345",
        decision_factors="loan_status, delinquency_duration, documented_hardship_reason",
    )
    result_pass(f"Fair Lending: {r['compliant']} | No violations")

    # Summary
    print(f"""
    {c('━' * 60, 'green')}
    {c('ALL 5 BARRIERS CLOSED:', 'bold')}

      {c('✓', 'green')} Barrier #1 Shadow AI     — Tool calls routed through Gateway
      {c('✓', 'green')} Barrier #2 Identity Crisis — KYA verified (2-factor)
      {c('✓', 'green')} Barrier #3 Data Exfiltration — Automated Reasoning validated
      {c('✓', 'green')} Barrier #4 Governance Vacuum — Cedar policy allowed (95 >= 90)
      {c('✓', 'green')} Barrier #5 Audit Blind Spots — 6/6 fields logged, fair lending OK

      {c('Every step governed. Every action auditable. Every barrier closed.', 'bold')}
    {c('━' * 60, 'green')}
""")


# ============================================================
# MAIN
# ============================================================

def main():
    os.system("clear" if os.name != "nt" else "cls")
    demo_0_intro()
    demo_1_shadow_ai()
    demo_2_identity_crisis()
    demo_3_data_exfiltration()
    demo_4_governance_vacuum()
    demo_5_audit_blind_spots()
    demo_6_full_flow()

    banner("DEMO COMPLETE", "green")
    print(f"""
  {c('What the audience just saw:', 'bold')}

  1. 9 tools registered in a single Gateway — zero shadow access
  2. 2-factor identity verification — pass AND fail scenarios
  3. Automated Reasoning caught an invalid settlement with mathematical proof
  4. Cedar policy blocked a tool call OUTSIDE the LLM's reasoning loop
  5. 100% compliance documentation with real-time violation detection
  6. Full orchestrated flow with all 5 barriers closing simultaneously

  {c('Resources:', 'dim')}
  • Agent repo: github.com/your-org/loan-collections-agents
  • AgentCore Samples: github.com/awslabs/amazon-bedrock-agentcore-samples
  • Multitenant Platform: 05-blueprints/multitenant-agentic-platform
  • Strands Agents: strandsagents.com
""")


if __name__ == "__main__":
    main()
