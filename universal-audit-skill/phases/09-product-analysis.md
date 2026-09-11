# Phase 9 — Product and Feature Analysis

**Goal:** understand what the product is trying to be, where it falls short, and
what to build next — grounded in the codebase, not in a generic feature wishlist.

Load `references/product-frameworks.md` for the scoring mechanics.

## 9.1 Derive the product from the code

Separate three kinds of statement and label them:

- **Fact** — present in the repository (a feature exists, a config supports X).
- **Inference** — strongly implied (this is built for offline field use because
  of the sync queue and the aggressive retry policy).
- **Assumption** — needs validation with a human (we assume operators wear gloves).

Cover: target users, operating context, core workflows, existing capabilities,
configuration surface, integrations, deployment model, offline behaviour,
administrative capability, diagnostic capability, and the security/privacy model
as experienced by the user.

## 9.2 Personas

Only include personas the evidence supports. For each: goals, tasks in this
product, pain points visible in the code (missing feedback, unrecoverable states),
environment, consequence of failure, and success metrics.

Typical candidates — end user, power user, administrator, support engineer,
integrator, security/compliance reviewer, and whoever operates the thing at 3am.

## 9.3 Feature inventory

| Feature | User value | Implementing component | Maturity | Known limitation | Evidence |
|---|---|---|---|---|---|

Maturity: `Prototype` · `Partial` · `Functional` · `Stable` · `Production-grade` ·
`Unknown`. `Production-grade` requires evidence of tests, error handling, and
operational readiness — not just that the code exists and looks finished.

## 9.4 Journey and failure analysis

Walk the real journey for this product (install → configure → first success →
routine use → failure → recovery → support → offboarding). For each step:
friction, error states, missing feedback, unsafe or irreversible actions,
recovery gaps, and the opportunity that follows.

The most valuable findings usually live in the failure and recovery steps, which
teams rarely design deliberately.

## 9.5 Market research

Research current, publicly documented behaviour of comparable products. Use
primary sources: official docs, release notes, public issue trackers, and
standards. Store listings and community forums are hypothesis sources only.

| Capability | This product | Common industry pattern | User value | Gap | Strategic relevance |
|---|---|---|---|---|---|

Do not copy a competitor feature without checking relevance to the persona,
complexity, dependencies, security impact, licensing constraints, operational
cost, and whether it actually differentiates.

## 9.6 Opportunity areas

Group by: reliability, usability, operability, security, privacy, administration,
diagnostics, scalability, deployment, integration, accessibility, observability,
offline resilience, compatibility, differentiation.

Each opportunity: problem statement, affected persona, evidence, frequency,
severity, current workaround, business impact, feature hypothesis, and what
validation is required before building.

## 9.7 Candidate features

For each candidate: problem solved, persona, evidence, user value, operational
value, business value, technical approach, architectural changes required,
security/privacy impact with standard mapping, quality-characteristic impact,
dependencies (including `BUG-XXX` blockers), risks, effort, phase, validation
experiment, and acceptance criteria.

**Gate:** if a feature depends on a subsystem that has an open Critical or High
finding, its recommendation is `Technical Foundation First` — regardless of how
attractive the feature is. Name the blocking `BUG-XXX` explicitly.

## 9.8 Prioritization

Score with both RICE and a risk-adjusted strategic score (formula in
`references/product-frameworks.md`). State the formula. Low confidence must lower
the score — never inflate confidence to promote a favourite. Where the two methods
disagree, say so and explain which you trust for this product and why.

## Exit gate

- [ ] Fact / inference / assumption labeled throughout
- [ ] Personas supported by evidence
- [ ] Feature inventory with maturity justified
- [ ] Every proposed feature traced to a problem statement
- [ ] Foundation-first gate applied against open findings
