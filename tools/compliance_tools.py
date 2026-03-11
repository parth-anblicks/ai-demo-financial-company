"""
Loan Collections Tools — Compliance & Documentation
These tools handle call documentation and fair lending compliance
per Sections 8-9 of the Loan Collections Decision Policy.
"""

from strands import tool
from datetime import datetime
from typing import Optional
import json


# Section 9 required fields
REQUIRED_FIELDS = [
    "identity_verification_method",
    "identity_verification_outcome",
    "hardship_reason",
    "resolution_options_discussed",
    "resolution_option_offered_or_declined",
    "next_action_date",
]

# Section 8 protected characteristics (MUST NOT influence decisions)
PROTECTED_CHARACTERISTICS = [
    "race", "color", "religion", "national_origin", "sex",
    "marital_status", "age", "public_assistance_income",
]

# Section 8 permitted decision factors
PERMITTED_FACTORS = [
    "loan_status", "payment_history", "delinquency_duration",
    "documented_hardship_reason",
]

# In-memory interaction log (replace with database in production)
INTERACTION_LOG = []


@tool
def log_interaction(
    customer_id: str,
    identity_verification_method: str,
    identity_verification_outcome: str,
    hardship_reason: str,
    resolution_options_discussed: str,
    resolution_option_offered_or_declined: str,
    next_action_date: str,
    supervisor_approval_reference: Optional[str] = None,
) -> dict:
    """Log all required fields after a collections call.

    Per Section 9: The agent MUST log ALL of the following after every call:
    1. Identity verification method used and outcome
    2. Customer-stated hardship reason
    3. Resolution option(s) discussed
    4. Resolution option offered or declined
    5. Supervisor approval reference (if settlement was discussed)
    6. Next action date

    If ANY field is missing, the interaction is NON-COMPLIANT.

    Args:
        customer_id: The loan account identifier
        identity_verification_method: Methods used (e.g., "ssn_last4, date_of_birth")
        identity_verification_outcome: "verified" or "failed"
        hardship_reason: Customer's stated reason for hardship
        resolution_options_discussed: Comma-separated list of options discussed
        resolution_option_offered_or_declined: Final outcome
        next_action_date: Date of next scheduled action (YYYY-MM-DD)
        supervisor_approval_reference: Reference ID if settlement was discussed

    Returns:
        dict with compliance status and any missing fields
    """
    entry = {
        "customer_id": customer_id,
        "timestamp": datetime.now().isoformat(),
        "identity_verification_method": identity_verification_method,
        "identity_verification_outcome": identity_verification_outcome,
        "hardship_reason": hardship_reason,
        "resolution_options_discussed": resolution_options_discussed,
        "resolution_option_offered_or_declined": resolution_option_offered_or_declined,
        "next_action_date": next_action_date,
        "supervisor_approval_reference": supervisor_approval_reference,
    }

    # Check for missing required fields
    missing = []
    for field in REQUIRED_FIELDS:
        val = entry.get(field)
        if val is None or (isinstance(val, str) and val.strip() == ""):
            missing.append(field)

    # Check if settlement was discussed but no supervisor reference
    if "settlement" in resolution_options_discussed.lower() and not supervisor_approval_reference:
        missing.append("supervisor_approval_reference (settlement was discussed)")

    compliant = len(missing) == 0
    entry["compliant"] = compliant
    entry["missing_fields"] = missing

    INTERACTION_LOG.append(entry)

    return {
        "logged": True,
        "compliant": compliant,
        "missing_fields": missing,
        "interaction_id": f"INT-{customer_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "warning": None if compliant else (
            f"NON-COMPLIANT: Missing fields: {', '.join(missing)}. "
            "Per Section 9, this interaction requires remediation."
        ),
    }


@tool
def validate_fair_lending(
    customer_id: str,
    decision_factors: str,
) -> dict:
    """Validate that resolution decision factors comply with fair lending rules.

    Per Section 8: Resolution options MUST be determined solely based on:
    - Loan status
    - Payment history
    - Delinquency duration
    - Documented hardship reason

    Resolution options MUST NOT vary based on: race, color, religion,
    national origin, sex, marital status, age, or receipt of income
    from public assistance programs.

    Args:
        customer_id: The loan account identifier
        decision_factors: Comma-separated list of factors that influenced
            the resolution decision

    Returns:
        dict with compliance status and any violations found
    """
    factors = [f.strip().lower() for f in decision_factors.split(",")]

    # Check for prohibited factors
    violations = []
    for factor in factors:
        for protected in PROTECTED_CHARACTERISTICS:
            if protected in factor:
                violations.append(
                    f"VIOLATION: '{factor}' references protected characteristic "
                    f"'{protected}' (Section 8)"
                )

    # Check that at least some permitted factors are present
    has_permitted = any(
        any(p in factor for p in PERMITTED_FACTORS)
        for factor in factors
    )

    compliant = len(violations) == 0 and has_permitted

    return {
        "customer_id": customer_id,
        "compliant": compliant,
        "decision_factors_reviewed": factors,
        "permitted_factors_present": has_permitted,
        "violations": violations,
        "timestamp": datetime.now().isoformat(),
        "warning": None if compliant else (
            f"FAIR LENDING VIOLATION DETECTED: {'; '.join(violations)}. "
            "Escalate to compliance officer immediately."
        ),
    }


@tool
def get_compliance_summary(customer_id: str) -> dict:
    """Get a compliance summary for all interactions with a customer.

    Returns the total number of interactions, compliance rate, and
    any outstanding non-compliant interactions requiring remediation.

    Args:
        customer_id: The loan account identifier

    Returns:
        dict with compliance summary
    """
    customer_entries = [
        e for e in INTERACTION_LOG if e["customer_id"] == customer_id
    ]

    if not customer_entries:
        return {
            "customer_id": customer_id,
            "total_interactions": 0,
            "message": "No interactions logged for this customer.",
        }

    compliant_count = sum(1 for e in customer_entries if e["compliant"])
    non_compliant = [e for e in customer_entries if not e["compliant"]]

    return {
        "customer_id": customer_id,
        "total_interactions": len(customer_entries),
        "compliant_count": compliant_count,
        "non_compliant_count": len(non_compliant),
        "compliance_rate": f"{compliant_count / len(customer_entries) * 100:.1f}%",
        "non_compliant_details": [
            {"timestamp": e["timestamp"], "missing_fields": e["missing_fields"]}
            for e in non_compliant
        ],
    }
