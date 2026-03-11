"""Hardship Recorder Tool — Section 3"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared_data import LOAN_DB
from datetime import datetime

def record_hardship(customer_id: str, hardship_reason: str) -> dict:
    loan = LOAN_DB.get(customer_id)
    if not loan: return {"recorded": False, "reason": "Account not found."}
    loan["hardship_reason"] = hardship_reason
    return {"recorded": True, "customer_id": customer_id, "hardship_reason": hardship_reason, "timestamp": datetime.now().isoformat()}
