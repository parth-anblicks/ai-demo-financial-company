"""Compliance Logger Tool — Section 9"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared_data import INTERACTION_LOG
from datetime import datetime

REQUIRED_FIELDS = ["identity_verification_method", "identity_verification_outcome", "hardship_reason", "resolution_options_discussed", "resolution_option_offered_or_declined", "next_action_date"]

def log_interaction(customer_id: str, identity_verification_method: str, identity_verification_outcome: str, hardship_reason: str, resolution_options_discussed: str, resolution_option_offered_or_declined: str, next_action_date: str, supervisor_approval_reference: str = None) -> dict:
    entry = {"customer_id": customer_id, "timestamp": datetime.now().isoformat(), "identity_verification_method": identity_verification_method, "identity_verification_outcome": identity_verification_outcome, "hardship_reason": hardship_reason, "resolution_options_discussed": resolution_options_discussed, "resolution_option_offered_or_declined": resolution_option_offered_or_declined, "next_action_date": next_action_date, "supervisor_approval_reference": supervisor_approval_reference}
    missing = [f for f in REQUIRED_FIELDS if not entry.get(f, "").strip()] if all(isinstance(entry.get(f), str) for f in REQUIRED_FIELDS) else [f for f in REQUIRED_FIELDS if not entry.get(f)]
    if "settlement" in resolution_options_discussed.lower() and not supervisor_approval_reference:
        missing.append("supervisor_approval_reference (settlement discussed)")
    compliant = len(missing) == 0
    entry["compliant"] = compliant
    INTERACTION_LOG.append(entry)
    return {"logged": True, "compliant": compliant, "missing_fields": missing, "interaction_id": f"INT-{customer_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}", "warning": None if compliant else f"NON-COMPLIANT: Missing: {', '.join(missing)}"}
