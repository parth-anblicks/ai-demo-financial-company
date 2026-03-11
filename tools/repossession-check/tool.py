"""Repossession Eligibility Tool — Section 7"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared_data import LOAN_DB

def check_repossession_eligibility(customer_id: str) -> dict:
    loan = LOAN_DB.get(customer_id)
    if not loan: return {"eligible": False, "reason": "Account not found."}
    conditions = {"delinquency_60_plus": loan["delinquency_days"] >= 60, "notice_sent": loan["repossession_notice_sent"], "vehicle_not_repossessed": not loan["vehicle_repossessed"]}
    missing = [k for k, v in conditions.items() if not v]
    return {"eligible": len(missing) == 0, "customer_id": customer_id, "delinquency_days": loan["delinquency_days"], "conditions": conditions, "missing_conditions": missing}
