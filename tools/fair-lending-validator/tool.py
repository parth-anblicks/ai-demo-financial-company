"""Fair Lending Validator Tool — Section 8"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared_data import PROTECTED_CHARACTERISTICS, PERMITTED_FACTORS
from datetime import datetime

def validate_fair_lending(customer_id: str, decision_factors: str) -> dict:
    factors = [f.strip().lower() for f in decision_factors.split(",")]
    violations = []
    for factor in factors:
        for protected in PROTECTED_CHARACTERISTICS:
            if protected in factor:
                violations.append(f"VIOLATION: '{factor}' references protected characteristic '{protected}'")
    has_permitted = any(any(p in f for p in PERMITTED_FACTORS) for f in factors)
    compliant = len(violations) == 0 and has_permitted
    return {"customer_id": customer_id, "compliant": compliant, "decision_factors_reviewed": factors, "permitted_factors_present": has_permitted, "violations": violations, "timestamp": datetime.now().isoformat(), "warning": None if compliant else f"FAIR LENDING VIOLATION: {'; '.join(violations)}"}
