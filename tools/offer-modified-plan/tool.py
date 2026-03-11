"""Offer Modified Plan Tool — Section 5"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared_data import LOAN_DB
from datetime import datetime

def offer_modified_plan(customer_id: str, modified_payment_amount: float, plan_duration_months: int) -> dict:
    loan = LOAN_DB.get(customer_id)
    if not loan: return {"offered": False, "reason": "Account not found."}
    min_pay = loan["monthly_payment"] * 0.5
    if loan["delinquency_days"] < 30 or loan["delinquency_days"] > 120: return {"offered": False, "reason": f"Requires 30-120 days. Current: {loan['delinquency_days']}."}
    if modified_payment_amount < min_pay: return {"offered": False, "reason": f"${modified_payment_amount:.2f} below 50% min of ${min_pay:.2f}."}
    if plan_duration_months > 6: return {"offered": False, "reason": f"{plan_duration_months} months exceeds 6-month max."}
    return {"offered": True, "customer_id": customer_id, "original_payment": loan["monthly_payment"], "modified_payment": modified_payment_amount, "plan_duration_months": plan_duration_months, "timestamp": datetime.now().isoformat()}
