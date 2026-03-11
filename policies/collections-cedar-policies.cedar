// ============================================================
// Loan Collections Cedar Policies
// ============================================================
// These policies are enforced at the AgentCore Gateway boundary,
// OUTSIDE the agent's reasoning loop. They are deterministic
// and cannot be bypassed by prompt injection.
//
// Deploy via: AgentCore Policy → Natural Language or Cedar code
// ============================================================

// ----- SECTION 6: Settlement Rules -----

// Block settlement offers for loans less than 90 days delinquent
forbid (
    principal,
    action == Action::"InvokeTool",
    resource == Gateway::"collections-gateway"
)
when {
    context.toolName == "offer_settlement" &&
    context.parameters.delinquencyDays < 90
};

// Block settlement if vehicle has been repossessed
forbid (
    principal,
    action == Action::"InvokeTool",
    resource == Gateway::"collections-gateway"
)
when {
    context.toolName == "offer_settlement" &&
    context.parameters.vehicleRepossessed == true
};

// ----- SECTION 7: Repossession Rules -----

// Block repossession for loans less than 60 days delinquent
forbid (
    principal,
    action == Action::"InvokeTool",
    resource == Gateway::"collections-gateway"
)
when {
    context.toolName == "check_repossession_eligibility" &&
    context.parameters.delinquencyDays < 60
};

// ----- SECTION 5: Modified Payment Plan Rules -----

// Block modified plans below 50% of original payment
forbid (
    principal,
    action == Action::"InvokeTool",
    resource == Gateway::"collections-gateway"
)
when {
    context.toolName == "offer_modified_plan" &&
    context.parameters.modifiedPaymentPercent < 50
};

// Block modified plans exceeding 6 months
forbid (
    principal,
    action == Action::"InvokeTool",
    resource == Gateway::"collections-gateway"
)
when {
    context.toolName == "offer_modified_plan" &&
    context.parameters.planDurationMonths > 6
};

// ----- AGENT SCOPING: Know Your Agent (KYA) -----

// Repossession agent cannot access settlement tools
forbid (
    principal == Agent::"repossession-agent",
    action == Action::"InvokeTool",
    resource == Gateway::"collections-gateway"
)
when {
    context.toolName == "offer_settlement"
};

// Identity agent can only access identity verification tools
forbid (
    principal == Agent::"identity-verification-agent",
    action == Action::"InvokeTool",
    resource == Gateway::"collections-gateway"
)
when {
    context.toolName != "verify_customer_identity"
};

// Compliance agent cannot access resolution tools
forbid (
    principal == Agent::"compliance-documentation-agent",
    action == Action::"InvokeTool",
    resource == Gateway::"collections-gateway"
)
when {
    context.toolName in ["offer_deferment", "offer_modified_plan", "offer_settlement"]
};

// ----- SETTLEMENT SUPERVISOR GATE -----

// Block communicating settlement without supervisor approval
forbid (
    principal,
    action == Action::"InvokeTool",
    resource == Gateway::"collections-gateway"
)
when {
    context.toolName == "communicate_settlement" &&
    !context.parameters.supervisorApproved
};
