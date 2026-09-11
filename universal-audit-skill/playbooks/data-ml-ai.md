# Playbook — Data / ML / AI

Standards: OWASP LLM Top 10 (2025), NIST AI RMF, ISO/IEC 42001, ISO/IEC 25012
(data quality), plus the backend playbook for any serving surface.

## Data pipeline
- Schema validation and contract testing at ingestion
- Missing/duplicate/late data handling; idempotent reprocessing
- Silent type coercion and precision loss
- Partition and timezone handling; off-by-one on date boundaries
- PII flowing into training data, feature stores, logs, or notebooks
- Data lineage: can you tell where a production number came from?
- Backfill correctness and its effect on downstream aggregates

## Training and model lifecycle
- Train/serve skew: different preprocessing in the two paths
- Data leakage across the train/test split
- Reproducibility: seeds, pinned data versions, pinned dependency versions
- Model registry, versioning, and rollback
- Evaluation beyond aggregate accuracy: slices, fairness, worst-case behaviour
- Drift detection and the action taken when it fires

## Serving
- Input validation and size limits on inference endpoints
- Resource exhaustion via large or adversarial inputs
- Timeout and fallback when the model is unavailable
- Caching correctness for personalized outputs
- Model artifact integrity: signed, verified before load
- Unsafe deserialization of model files (pickle-based formats are code execution)

## LLM-specific
- Prompt injection through any untrusted content the model reads (documents, web
  pages, tool output, user profiles) — and what the model can *do* as a result
- Tool/function-calling permissions: least privilege, confirmation for destructive
  or irreversible actions, no ambient authority
- Output handling: model output rendered as HTML/markdown/SQL/shell without
  treating it as untrusted
- Secret and system-prompt leakage; sensitive data in prompts sent to third parties
- Retrieval: access control on the index (can a user retrieve another tenant's
  documents?), source attribution
- Rate limiting and cost controls; unbounded agent loops
- Logging of prompts and completions versus privacy commitments
- Evaluation harness for regressions; a prompt change is a code change

## Governance
- Documented purpose, limitations, and intended use
- Human oversight for consequential decisions
- Disclosure to users that they are interacting with an AI system
- Retention of inference data and opt-out
