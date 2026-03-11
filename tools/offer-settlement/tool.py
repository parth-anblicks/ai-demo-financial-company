"""Offer Settlement Tool — Section 6 [CEDAR-GATED]"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared_data import LOAN_DB
from datetime import datetime

def offer_settlement(customer_id: str, settlement_amount: float, justification: str) -> dict:
    """NOTE: This tool is also gated by Cedar policy at the Gateway. If delinquency < 90, the Gateway blocks the call before it reaches this code."""
    loan = LOAN_DB.get(customer_id)
    if not loan: return {"offered": False, "reason": "Account not found."}
    if loan["delinquency_days"] < 90: return {"offered": False, "reason": f"Requires 90+ days. Current: {loan['delinquency_days']}. Section 6."}
    if loan["vehicle_repossessed"]: return {"offered": False, "reason": "Vehicle repossessed. Settlement unavailable."}
    return {"offered": True, "status": "PENDING_SUPERVISOR_APPROVAL", "customer_id": customer_id, "settlement_amount": settlement_amount, "loan_amount": loan["loan_amount"], "settlement_percent": round(settlement_amount / loan["loan_amount"] * 100, 1), "justification": justification, "supervisor_approval_required": True, "timestamp": datetime.now().isoformat()}
