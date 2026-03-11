"""Simulated databases for demo. Replace with actual DB/API calls in production."""
from datetime import datetime, timedelta

CUSTOMER_DB = {
    "ACC-12345": {
        "ssn_last4": "4567", "date_of_birth": "1985-03-15",
        "account_number": "ACC-12345", "mothers_maiden_name": "Johnson",
        "registered_email": "jsmith@email.com",
    },
    "ACC-67890": {
        "ssn_last4": "8901", "date_of_birth": "1990-07-22",
        "account_number": "ACC-67890", "mothers_maiden_name": "Williams",
        "registered_email": "mwilliams@email.com",
    },
}

LOAN_DB = {
    "ACC-12345": {
        "customer_name": "John Smith", "loan_amount": 25000.00,
        "monthly_payment": 450.00, "delinquency_days": 95,
        "last_payment_date": (datetime.now() - timedelta(days=95)).strftime("%Y-%m-%d"),
        "prior_deferments": 0, "deferment_in_past_12_months": False,
        "prior_modifications": 0, "vehicle_repossessed": False,
        "repossession_notice_sent": False, "hardship_reason": None,
    },
    "ACC-67890": {
        "customer_name": "Maria Williams", "loan_amount": 18000.00,
        "monthly_payment": 320.00, "delinquency_days": 45,
        "last_payment_date": (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d"),
        "prior_deferments": 1, "deferment_in_past_12_months": True,
        "prior_modifications": 1, "vehicle_repossessed": False,
        "repossession_notice_sent": False, "hardship_reason": None,
    },
}

INTERACTION_LOG = []

APPROVED_METHODS = ["ssn_last4", "date_of_birth", "account_number", "mothers_maiden_name", "registered_email"]
PROTECTED_CHARACTERISTICS = ["race", "color", "religion", "national_origin", "sex", "marital_status", "age", "public_assistance_income"]
PERMITTED_FACTORS = ["loan_status", "payment_history", "delinquency_duration", "documented_hardship_reason"]
