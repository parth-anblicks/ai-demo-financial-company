"""Loan Status Tool — Section 1"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared_data import LOAN_DB

def check_loan_status(customer_id: str) -> dict:
    loan = LOAN_DB.get(customer_id)
    if not loan: return {"found": False, "reason": "Loan not found."}
    d = loan["delinquency_days"]
    eligible = []
    if 30 <= d <= 90 and not loan["deferment_in_past_12_months"] and loan["prior_modifications"] <= 1: eligible.append("deferment")
    if 30 <= d <= 120: eligible.append("modified_payment_plan")
    if d >= 90 and not loan["vehicle_repossessed"]: eligible.append("settlement")
    if d >= 60: eligible.append("repossession (if all options declined)")
    return {"found": True, "customer_name": loan["customer_name"], "loan_amount": loan["loan_amount"], "monthly_payment": loan["monthly_payment"], "delinquency_days": d, "last_payment_date": loan["last_payment_date"], "prior_modifications": loan["prior_modifications"], "vehicle_repossessed": loan["vehicle_repossessed"], "eligible_resolutions": eligible}
