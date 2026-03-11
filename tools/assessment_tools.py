"""
Loan Collections Tools — Assessment & Resolution
These tools handle loan status checks, hardship assessment, and resolution
offers per Sections 3-7 of the Loan Collections Decision Policy.
"""

from strands import tool
from datetime import datetime, timedelta
import json


# Simulated loan database (replace with actual DB/API in production)
LOAN_DB = {
    "ACC-12345": {
        "customer_name": "John Smith",
        "loan_amount": 25000.00,
        "monthly_payment": 450.00,
        "due_date": (datetime.now() - timedelta(days=95)).strftime("%Y-%m-%d"),
        "last_payment_date": (datetime.now() - timedelta(days=95)).strftime("%Y-%m-%d"),
        "delinquency_days": 95,
        "prior_deferments": 0,
        "deferment_in_past_12_months": False,
        "prior_modifications": 0,
        "vehicle_repossessed": False,
        "repossession_notice_sent": False,
        "hardship_reason": None,
    },
    "ACC-67890": {
        "customer_name": "Maria Williams",
        "loan_amount": 18000.00,
        "monthly_payment": 320.00,
        "due_date": (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d"),
        "last_payment_date": (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d"),
        "delinquency_days": 45,
        "prior_deferments": 1,
        "deferment_in_past_12_months": True,
        "prior_modifications": 1,
        "vehicle_repossessed": False,
        "repossession_notice_sent": False,
        "hardship_reason": None,
    },
}


@tool
def check_loan_status(customer_id: str) -> dict:
    """Retrieve current loan status including delinquency details.

    Returns loan amount, monthly payment, delinquency days, payment history,
    and eligibility flags needed for resolution assessment.

    Args:
        customer_id: The loan account identifier (e.g., ACC-12345)

    Returns:
        dict with full loan status details
    """
    loan = LOAN_DB.get(customer_id)
    if not loan:
        return {"found": False, "reason": "Loan account not found."}

    return {
        "found": True,
        "customer_name": loan["customer_name"],
        "loan_amount": loan["loan_amount"],
        "monthly_payment": loan["monthly_payment"],
        "delinquency_days": loan["delinquency_days"],
        "last_payment_date": loan["last_payment_date"],
        "prior_modifications": loan["prior_modifications"],
        "vehicle_repossessed": loan["vehicle_repossessed"],
        "eligible_resolutions": _compute_eligible_resolutions(loan),
    }


@tool
def check_deferment_history(customer_id: str) -> dict:
    """Check whether customer has received a deferment in the past 12 months.

    Per Section 4: Deferment may NOT be offered if the customer has
    received a deferment in the past 12 months OR the loan has been
    modified more than once.

    Args:
        customer_id: The loan account identifier

    Returns:
        dict with deferment eligibility details
    """
    loan = LOAN_DB.get(customer_id)
    if not loan:
        return {"found": False}

    eligible = (
        not loan["deferment_in_past_12_months"]
        and loan["prior_modifications"] <= 1
        and 30 <= loan["delinquency_days"] <= 90
    )

    reasons = []
    if loan["deferment_in_past_12_months"]:
        reasons.append("Customer received a deferment within the past 12 months")
    if loan["prior_modifications"] > 1:
        reasons.append("Loan has been modified more than once")
    if loan["delinquency_days"] < 30 or loan["delinquency_days"] > 90:
        reasons.append(f"Delinquency of {loan['delinquency_days']} days is outside 30-90 day window")

    return {
        "found": True,
        "deferment_in_past_12_months": loan["deferment_in_past_12_months"],
        "prior_deferments": loan["prior_deferments"],
        "prior_modifications": loan["prior_modifications"],
        "deferment_eligible": eligible,
        "ineligibility_reasons": reasons if not eligible else [],
    }


@tool
def record_hardship(customer_id: str, hardship_reason: str) -> dict:
    """Document the customer's stated hardship reason.

    Per Section 3: If a customer claims financial hardship, the agent
    MUST document the stated reason.

    Args:
        customer_id: The loan account identifier
        hardship_reason: The reason stated by the customer (e.g., job loss,
            medical emergency, divorce, reduced income)

    Returns:
        dict confirming the hardship was recorded
    """
    loan = LOAN_DB.get(customer_id)
    if not loan:
        return {"recorded": False, "reason": "Account not found."}

    loan["hardship_reason"] = hardship_reason
    return {
        "recorded": True,
        "customer_id": customer_id,
        "hardship_reason": hardship_reason,
        "timestamp": datetime.now().isoformat(),
    }


@tool
def offer_deferment(
    customer_id: str,
    deferment_months: int,
) -> dict:
    """Offer a payment deferment to the customer.

    Per Section 4:
    - Loan MUST be between 30 and 90 days delinquent
    - Customer MUST NOT have received a deferment in the past 12 months
    - Loan MUST NOT have been modified more than once
    - Deferment extends the loan term; interest continues to accrue

    Args:
        customer_id: The loan account identifier
        deferment_months: Number of months to defer (typically 1-3)

    Returns:
        dict with offer details or rejection reason
    """
    loan = LOAN_DB.get(customer_id)
    if not loan:
        return {"offered": False, "reason": "Account not found."}

    # Enforce Section 4 rules
    if loan["delinquency_days"] < 30 or loan["delinquency_days"] > 90:
        return {
            "offered": False,
            "reason": f"Deferment requires 30-90 days delinquency. "
            f"Current: {loan['delinquency_days']} days.",
        }
    if loan["deferment_in_past_12_months"]:
        return {
            "offered": False,
            "reason": "Customer received a deferment within the past 12 months.",
        }
    if loan["prior_modifications"] > 1:
        return {
            "offered": False,
            "reason": "Loan has been modified more than once.",
        }

    return {
        "offered": True,
        "customer_id": customer_id,
        "deferment_months": deferment_months,
        "interest_accrues": True,
        "term_extended_by": f"{deferment_months} months",
        "note": "Interest continues to accrue during the deferment period.",
        "timestamp": datetime.now().isoformat(),
    }


@tool
def offer_modified_plan(
    customer_id: str,
    modified_payment_amount: float,
    plan_duration_months: int,
) -> dict:
    """Offer a modified payment plan to the customer.

    Per Section 5:
    - Loan MUST be between 30 and 120 days delinquent
    - Modified payment MUST NOT be less than 50% of original payment
    - Plan duration MUST NOT exceed 6 months

    Args:
        customer_id: The loan account identifier
        modified_payment_amount: The proposed reduced monthly payment
        plan_duration_months: Duration of the modified plan in months

    Returns:
        dict with offer details or rejection reason
    """
    loan = LOAN_DB.get(customer_id)
    if not loan:
        return {"offered": False, "reason": "Account not found."}

    min_payment = loan["monthly_payment"] * 0.5

    if loan["delinquency_days"] < 30 or loan["delinquency_days"] > 120:
        return {
            "offered": False,
            "reason": f"Modified plan requires 30-120 days delinquency. "
            f"Current: {loan['delinquency_days']} days.",
        }
    if modified_payment_amount < min_payment:
        return {
            "offered": False,
            "reason": f"Modified payment ${modified_payment_amount:.2f} is below "
            f"50% minimum of ${min_payment:.2f} (original: ${loan['monthly_payment']:.2f}).",
        }
    if plan_duration_months > 6:
        return {
            "offered": False,
            "reason": f"Plan duration of {plan_duration_months} months exceeds "
            f"maximum of 6 months.",
        }

    return {
        "offered": True,
        "customer_id": customer_id,
        "original_payment": loan["monthly_payment"],
        "modified_payment": modified_payment_amount,
        "reduction_percent": round((1 - modified_payment_amount / loan["monthly_payment"]) * 100, 1),
        "plan_duration_months": plan_duration_months,
        "timestamp": datetime.now().isoformat(),
    }


@tool
def offer_settlement(
    customer_id: str,
    settlement_amount: float,
    justification: str,
) -> dict:
    """Offer a settlement to the customer.

    Per Section 6:
    - Loan MUST be 90+ days delinquent
    - Vehicle MUST NOT have been repossessed
    - Settlement MUST be documented and escalated to supervisor BEFORE
      being communicated to the customer

    NOTE: This tool call will be BLOCKED by Cedar policy if
    delinquency_days < 90. The policy operates at the Gateway boundary,
    outside this agent's reasoning loop.

    Args:
        customer_id: The loan account identifier
        settlement_amount: The proposed settlement amount
        justification: Reason for the settlement offer

    Returns:
        dict with offer details (pending supervisor approval) or rejection
    """
    loan = LOAN_DB.get(customer_id)
    if not loan:
        return {"offered": False, "reason": "Account not found."}

    # These checks are also enforced by Cedar policy at the Gateway
    if loan["delinquency_days"] < 90:
        return {
            "offered": False,
            "reason": f"Settlement requires 90+ days delinquency. "
            f"Current: {loan['delinquency_days']} days. Per Section 6.",
        }
    if loan["vehicle_repossessed"]:
        return {
            "offered": False,
            "reason": "Vehicle has been repossessed. Settlement not available.",
        }

    return {
        "offered": True,
        "status": "PENDING_SUPERVISOR_APPROVAL",
        "customer_id": customer_id,
        "settlement_amount": settlement_amount,
        "loan_amount": loan["loan_amount"],
        "settlement_percent": round(settlement_amount / loan["loan_amount"] * 100, 1),
        "justification": justification,
        "supervisor_approval_required": True,
        "note": "Per Section 6: Settlement MUST be approved by supervisor "
        "BEFORE being communicated to the customer.",
        "timestamp": datetime.now().isoformat(),
    }


@tool
def check_repossession_eligibility(customer_id: str) -> dict:
    """Check whether repossession steps can be initiated.

    Per Section 7:
    - Loan MUST be at least 60 days delinquent
    - Customer MUST have declined or be ineligible for ALL resolution options
    - Repossession notice MUST have been sent to customer's address
    - Notice MUST be issued at least 10 days before action (in applicable states)

    Args:
        customer_id: The loan account identifier

    Returns:
        dict with eligibility status and missing conditions
    """
    loan = LOAN_DB.get(customer_id)
    if not loan:
        return {"eligible": False, "reason": "Account not found."}

    conditions = {
        "delinquency_60_plus": loan["delinquency_days"] >= 60,
        "notice_sent": loan["repossession_notice_sent"],
        "vehicle_not_repossessed": not loan["vehicle_repossessed"],
    }
    missing = [k for k, v in conditions.items() if not v]

    return {
        "eligible": len(missing) == 0,
        "customer_id": customer_id,
        "delinquency_days": loan["delinquency_days"],
        "conditions": conditions,
        "missing_conditions": missing,
        "note": "Agent MUST also confirm all resolution options were declined "
        "or customer is ineligible before initiating repossession."
        if len(missing) == 0
        else f"Cannot initiate repossession. Missing: {', '.join(missing)}",
    }


def _compute_eligible_resolutions(loan: dict) -> list:
    """Compute which resolution options are available based on loan state."""
    eligible = []
    d = loan["delinquency_days"]

    if 30 <= d <= 90 and not loan["deferment_in_past_12_months"] and loan["prior_modifications"] <= 1:
        eligible.append("deferment")
    if 30 <= d <= 120:
        eligible.append("modified_payment_plan")
    if d >= 90 and not loan["vehicle_repossessed"]:
        eligible.append("settlement")
    if d >= 60:
        eligible.append("repossession (if all options declined)")

    return eligible
