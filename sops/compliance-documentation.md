# Compliance Documentation SOP

## Overview
Log all required fields and validate fair lending compliance after every collections call.
Maps to: Loan Collections Decision Policy — Sections 8 and 9.

## Parameters
- **customer_id** (required): The loan account identifier
- **interaction_data** (required): Summary of the collections interaction

## Steps

### 1. Collect Required Fields (Section 9)
After every collections call, you MUST log ALL of the following:
1. Identity verification method used and outcome
2. Customer-stated hardship reason
3. Resolution option(s) discussed
4. Resolution option offered or declined
5. Supervisor approval reference (if a settlement was discussed)
6. Next action date

**Constraints:**
- You MUST NOT mark the interaction as complete until all 6 fields are logged.
- If ANY field is not completed, the interaction is considered NON-COMPLIANT.
- Call `log_interaction` with all required fields.

### 2. Validate Fair Lending (Section 8)
Call `validate_fair_lending` with the decision factors that influenced the resolution.

**Constraints:**
- Decision factors MUST include ONLY: loan status, payment history, delinquency duration, documented hardship reason.
- Decision factors MUST NOT reference: race, color, religion, national origin, sex, marital status, age, or receipt of income from public assistance programs.
- If a violation is detected, you MUST flag it for immediate escalation to a compliance officer.

### 3. Generate Compliance Report
- Summarize the interaction's compliance status.
- Flag any missing fields or fair lending violations.
- Record the next action date.

## Output
Return a structured response indicating:
- `compliant`: boolean
- `missing_fields`: list (empty if compliant)
- `fair_lending_compliant`: boolean
- `violations`: list (empty if compliant)
- `interaction_id`: unique identifier for the logged interaction
- `next_action_date`: scheduled follow-up date
