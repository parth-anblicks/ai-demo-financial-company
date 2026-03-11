"""
Loan Collections Tools — Identity Verification
These tools handle customer identity verification per Section 2 of the
Loan Collections Decision Policy.
"""

from strands import tool
from typing import Literal


APPROVED_METHODS = [
    "ssn_last4",
    "date_of_birth",
    "account_number",
    "mothers_maiden_name",
    "registered_email",
]

# Simulated customer database (replace with actual DB/API in production)
CUSTOMER_DB = {
    "ACC-12345": {
        "ssn_last4": "4567",
        "date_of_birth": "1985-03-15",
        "account_number": "ACC-12345",
        "mothers_maiden_name": "Johnson",
        "registered_email": "jsmith@email.com",
    },
    "ACC-67890": {
        "ssn_last4": "8901",
        "date_of_birth": "1990-07-22",
        "account_number": "ACC-67890",
        "mothers_maiden_name": "Williams",
        "registered_email": "mwilliams@email.com",
    },
}


@tool
def verify_customer_identity(
    customer_id: str,
    method1_type: str,
    method1_value: str,
    method2_type: str,
    method2_value: str,
) -> dict:
    """Verify customer identity using two of five approved methods.

    Per Section 2 of the Loan Collections Decision Policy, the agent
    MUST verify identity using at least two of: ssn_last4, date_of_birth,
    account_number, mothers_maiden_name, registered_email.

    If verification fails, the agent MUST NOT disclose any account
    information and MUST terminate the call.

    Args:
        customer_id: The loan account identifier (e.g., ACC-12345)
        method1_type: First verification method (one of the 5 approved methods)
        method1_value: Value provided by customer for method 1
        method2_type: Second verification method (must differ from method 1)
        method2_value: Value provided by customer for method 2

    Returns:
        dict with verified (bool), methods_used (list), and reason (str)
    """
    # Validate methods are approved
    if method1_type not in APPROVED_METHODS:
        return {
            "verified": False,
            "methods_used": [],
            "reason": f"Invalid verification method: {method1_type}. "
            f"Approved methods: {', '.join(APPROVED_METHODS)}",
        }
    if method2_type not in APPROVED_METHODS:
        return {
            "verified": False,
            "methods_used": [],
            "reason": f"Invalid verification method: {method2_type}. "
            f"Approved methods: {', '.join(APPROVED_METHODS)}",
        }
    if method1_type == method2_type:
        return {
            "verified": False,
            "methods_used": [],
            "reason": "Two DIFFERENT verification methods are required.",
        }

    # Look up customer
    customer = CUSTOMER_DB.get(customer_id)
    if not customer:
        return {
            "verified": False,
            "methods_used": [],
            "reason": "Customer account not found.",
        }

    # Verify each method
    m1_ok = customer.get(method1_type, "").lower() == method1_value.lower()
    m2_ok = customer.get(method2_type, "").lower() == method2_value.lower()

    if m1_ok and m2_ok:
        return {
            "verified": True,
            "methods_used": [method1_type, method2_type],
            "reason": "Identity verified successfully with 2 approved methods.",
        }
    else:
        failed = []
        if not m1_ok:
            failed.append(method1_type)
        if not m2_ok:
            failed.append(method2_type)
        return {
            "verified": False,
            "methods_used": [],
            "reason": f"Verification failed for: {', '.join(failed)}. "
            "Agent MUST terminate call. MUST NOT disclose account information.",
        }
