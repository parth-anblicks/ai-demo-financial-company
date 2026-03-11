"""Deferment History Tool — Section 4"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared_data import LOAN_DB

def check_deferment_history(customer_id: str) -> dict:
    loan = LOAN_DB.get(customer_id)
    if not loan: return {"found": False}
    eligible = not loan["deferment_in_past_12_months"] and loan["prior_modifications"] <= 1 and 30 <= loan["delinquency_days"] <= 90
    reasons = []
    if loan["deferment_in_past_12_months"]: reasons.append("Deferment in past 12 months")
    if loan["prior_modifications"] > 1: reasons.append("Modified more than once")
    if loan["delinquency_days"] < 30 or loan["delinquency_days"] > 90: reasons.append(f"Delinquency {loan['delinquency_days']}d outside 30-90 range")
    return {"found": True, "deferment_in_past_12_months": loan["deferment_in_past_12_months"], "prior_modifications": loan["prior_modifications"], "deferment_eligible": eligible, "ineligibility_reasons": reasons if not eligible else []}
