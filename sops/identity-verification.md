# Identity Verification SOP

## Overview
Verify customer identity before any collections discussion.
Maps to: Loan Collections Decision Policy — Section 2.

## Parameters
- **customer_id** (required): The loan account identifier
- **channel** (required): "phone" | "chat" | "email"

## Steps

### 1. Initiate Verification
The agent MUST request at least two of the following from the customer:
  - Last four digits of SSN (`ssn_last4`)
  - Date of birth (`date_of_birth`)
  - Account number (`account_number`)
  - Mother's maiden name (`mothers_maiden_name`)
  - Registered email address (`registered_email`)

**Constraints:**
- You MUST NOT proceed to any collections discussion until identity verification is complete.
- You MUST NOT accept fewer than 2 verification methods.
- You SHOULD explain to the customer why verification is required.

### 2. Execute Verification
Call the `verify_customer_identity` tool with the customer_id and both verification methods.

**Constraints:**
- You MUST use the exact method types listed above (e.g., `ssn_last4`, not `SSN`).
- You MUST pass both methods in a single tool call.

### 3. Evaluate Result
- If `verified: true` → The customer is VERIFIED. Proceed to the next step in the collections workflow.
- If `verified: false` → Verification has FAILED.

**On FAILURE:**
- You MUST NOT disclose any account information (balance, delinquency, payment history, etc.).
- You MUST terminate the interaction politely.
- You MUST inform the customer they can call back with proper identification.
- You MUST log the failed verification attempt.

### 4. Log Outcome
- You MUST record the verification method(s) used and the outcome.
- This information is required for Section 9 compliance documentation.

## Output
Return a structured response indicating:
- `verified`: boolean
- `methods_used`: list of methods
- `next_step`: "proceed_to_hardship_assessment" or "terminate_call"
