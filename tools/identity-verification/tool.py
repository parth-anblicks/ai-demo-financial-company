"""Identity Verification Tool — Section 2"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared_data import CUSTOMER_DB, APPROVED_METHODS

def verify_customer_identity(customer_id: str, method1_type: str, method1_value: str, method2_type: str, method2_value: str) -> dict:
    """Verify customer identity using two of five approved methods."""
    if method1_type not in APPROVED_METHODS:
        return {"verified": False, "methods_used": [], "reason": f"Invalid method: {method1_type}"}
    if method2_type not in APPROVED_METHODS:
        return {"verified": False, "methods_used": [], "reason": f"Invalid method: {method2_type}"}
    if method1_type == method2_type:
        return {"verified": False, "methods_used": [], "reason": "Two DIFFERENT methods required."}
    customer = CUSTOMER_DB.get(customer_id)
    if not customer:
        return {"verified": False, "methods_used": [], "reason": "Customer not found."}
    m1_ok = customer.get(method1_type, "").lower() == method1_value.lower()
    m2_ok = customer.get(method2_type, "").lower() == method2_value.lower()
    if m1_ok and m2_ok:
        return {"verified": True, "methods_used": [method1_type, method2_type], "reason": "Identity verified."}
    failed = []
    if not m1_ok: failed.append(method1_type)
    if not m2_ok: failed.append(method2_type)
    return {"verified": False, "methods_used": [], "reason": f"Failed: {', '.join(failed)}. MUST terminate call."}
