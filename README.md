# Loan Collections AI Agents — Governed Financial Services Templates

> **Deployable from the [Multitenant Agentic Platform](https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/05-blueprints/multitenant-agentic-platform) dashboard.**

## Overview

This repository contains **4 production-ready agent templates** for a Loan Collections Decision Policy workflow. Each agent is designed to be deployed on **Amazon Bedrock AgentCore Runtime** and demonstrates how to close the 5 Enterprise AI Trust Gap barriers in a regulated financial services context.

| Agent | File Path | Trust Gap Barrier | AgentCore Services Used |
|-------|-----------|-------------------|------------------------|
| Identity Verification | `agents/identity-verification/main.py` | #2 Identity Crisis (KYA) | Runtime, Identity, Memory |
| Hardship Assessment | `agents/hardship-assessment/main.py` | #3 Data Exfiltration + #4 Governance Vacuum | Runtime, Gateway, Guardrails, Policy |
| Compliance Documentation | `agents/compliance-documentation/main.py` | #5 Audit Blind Spots | Runtime, Observability, Evaluations |
| Collections Orchestrator | `agents/collections-orchestrator/main.py` | #1 Shadow AI (all barriers) | Runtime, Gateway, Identity, Memory, Observability |

## Deploying from the Multitenant Platform Dashboard

1. In the **Bedrock Agent Dashboard**, click **Deploy New Agent**
2. Set **GitHub Repository** to: `your-org/loan-collections-agents`
3. Set **File Path** to one of the agent paths above (e.g., `agents/identity-verification/main.py`)
4. Set **Branch** to: `main`
5. Click **Load Available Tools** to discover registered MCP tools from your Gateway
6. Click **Deploy Agent**

Repeat for each agent with the corresponding file path.

## Architecture

```
Customer Call → Collections Orchestrator
                    ├─→ Identity Verification Agent (Section 2)
                    │       └─ verify_customer_identity tool
                    ├─→ Hardship Assessment Agent (Sections 3-6)
                    │       ├─ check_loan_status tool
                    │       ├─ check_deferment_history tool
                    │       ├─ offer_deferment tool
                    │       ├─ offer_modified_plan tool
                    │       └─ offer_settlement tool (Cedar-gated)
                    ├─→ Compliance Documentation Agent (Sections 8-9)
                    │       ├─ log_interaction tool
                    │       └─ validate_fair_lending tool
                    └─→ [Supervisor Gate for settlements]
```

## Agent SOPs

Each agent loads its corresponding SOP (Standard Operating Procedure) from the `sops/` directory as its system prompt. SOPs use RFC 2119 keywords (MUST, SHOULD, MAY) for precise behavioral control.

## Cedar Policies

The `policies/` directory contains Cedar policy files that enforce deterministic rules at the AgentCore Gateway boundary — **outside the agent's reasoning loop**.

## Tools

The `tools/` directory contains `@tool`-decorated functions that agents can invoke. In production, these would be registered as MCP tools in the AgentCore Gateway. For local development, they use simulated data.

## Prerequisites

- Python 3.10+
- AWS credentials configured with Bedrock access
- Claude Sonnet 4 model access enabled in Bedrock console (us-east-1)
- `pip install strands-agents bedrock-agentcore boto3`

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run any agent locally
python agents/identity-verification/main.py

# Or use AgentCore CLI
agentcore configure --entrypoint agents/identity-verification/main.py --name identity-agent
agentcore launch --local
```

## License

Apache-2.0
