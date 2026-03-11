"""Offer Deferment Tool — Section 4"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared_data import LOAN_DB
from datetime import datetime

def offer_deferment(customer_id: str, deferment_months: int) -> dict:
    loan = LOAN_DB.get(customer_id)
    if not loan: return {"offered": False, "reason": "Account not found."}
    if loan["delinquency_days"] < 30 or loan["delinquency_days"] > 90: return {"offered": False, "reason": f"Requires 30-90 days. Current: {loan['delinquency_days']}."}
    if loan["deferment_in_past_12_months"]: return {"offered": False, "reason": "Deferment in past 12 months."}
    if loan["prior_modifications"] > 1: return {"offered": False, "reason": "Modified more than once."}
    return {"offered": True, "customer_id": customer_id, "deferment_months": deferment_months, "interest_accrues": True, "timestamp": datetime.now().isoformat()}
