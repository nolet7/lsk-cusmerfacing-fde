# LSK Customer-Facing Data & AI FDE

A fictional B2B SaaS customer implementation lab, built for discovery, presales POCs, pilot adoption, and controlled production handover.

## CTO mandate
Enable enterprise customers to connect CRM, ERP and support datasets via versioned REST/JSON APIs, ask questions about their data with auditable AI assistance, and automate safe read-only workflows. Prove value in live demonstrations before investing in a controlled pilot. Deliver repeatable integration accelerators and customer enablement.

## Branch strategy
- `main`: mandate, architecture, discovery, acceptance criteria and project charter.
- `poc`: runnable legacy SaaS CRM/support simulator plus Python/SQL integration API, seeded demo data and optional live LLM support.
- `pilot`: POC plus tenant-access enforcement, adoption telemetry, evaluation and pilot runbooks.
- `production`: pilot plus health/readiness endpoints, container setup, release/handover and security review checklist.

Branches are progressive snapshots; production is NOT proof of a cloud deployment or production certification.

## Customer journey
Sales discovery -> requirements -> reusable demo environment -> integration mapping -> technical workshop -> POC acceptance -> pilot onboarding -> monitored launch -> support handover -> product-feedback backlog.

## Start
See branch-specific README, `docs/` and `architecture/`. No real customer data. Demo credentials and sample records are fictional.

## Safety
AI never executes database queries or arbitrary HTTP requests supplied by an LLM. It uses pre-approved read-only tool results. Avoid putting customer secrets or sensitive records in prompts.
