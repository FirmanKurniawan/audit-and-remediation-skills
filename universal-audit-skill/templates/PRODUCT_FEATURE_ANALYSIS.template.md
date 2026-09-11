# PRODUCT FEATURE ANALYSIS — {{PROJECT_NAME}}

> Companion to `BUG_ANALYSIS.md` at commit `{{COMMIT}}`. Analysis only.
> Every statement is labeled **Fact**, **Inference**, or **Assumption**.

## 1. Document Control

| Field | Value |
|---|---|
| Repository / branch / commit | {{PROJECT_NAME}} / {{BRANCH}} / {{COMMIT}} |
| Analysis date | {{AUDIT_DATE}} |
| Platforms | {{PLATFORMS}} |
| Product scope | |
| Key assumptions | |
| Research limitations | |
| Sources reviewed | see §19 |

## 2. Product Executive Summary

What the product is, who it serves, the problem it solves, its current value, its
biggest weakness, the differentiation opportunity, and the product-market-fit
risk. Close with the three most important feature recommendations and the three
technical foundations that must land first.

Do not recommend expansion while core reliability is unproven — say so plainly if
that is the situation.

## 3. Current Product Understanding

Target users · operating context · core workflows · existing capabilities ·
configuration surface · integrations · deployment and distribution · online/offline
dependency · administrative capability · diagnostic capability · security and
privacy model as the user experiences it.

Label each item Fact / Inference / Assumption, with the evidence for facts.

## 4. Personas

Per persona: goals · tasks in this product · pain points visible in the code ·
environment · consequence of failure · required controls · success metrics.
Include only personas the evidence supports.

## 5. Feature Inventory

| Feature | User value | Implementing component | Maturity | Known limitation | Evidence |
|---|---|---|---|---|---|

Maturity: Prototype · Partial · Functional · Stable · Production-grade · Unknown.
`Production-grade` requires test, error-handling, and operational evidence.

## 6. User Journey and Failure Analysis

Per journey step: friction · error states · missing feedback · unsafe or
irreversible actions · recovery gaps · opportunity. Cover the failure and recovery
steps as thoroughly as the happy path.

## 7. Market and Industry Research

| Capability | This product | Common industry pattern | User value | Gap | Strategic relevance |
|---|---|---|---|---|---|

Publicly documented behaviour only. Note the source and date for each pattern.

## 8. Problems and Opportunity Areas

Grouped by reliability, usability, operability, security, privacy, administration,
diagnostics, scalability, deployment, integration, accessibility, observability,
offline resilience, compatibility, differentiation.

Per opportunity: problem statement · affected persona · evidence · frequency ·
severity · current workaround · business impact · feature hypothesis · validation
required.

## 9. Candidate Feature Analysis

Per candidate: problem solved · persona · evidence · user/operational/business
value · technical approach · architectural changes · security and privacy impact
with standard mapping · ISO/IEC 25010:2023 impact · dependencies **including
blocking `BUG-XXX` ids** · risks · effort · phase · validation experiment ·
acceptance criteria.

## 10. Prioritization Method

State the RICE inputs and the risk-adjusted formula explicitly, including weights
and the confidence factor. Note where the two methods disagree and which you trust
for this product.

## 11. Prioritization Table

| ID | Feature | Problem | Persona | RICE | Strategic | Effort | Risk | Blocking bugs | Priority | Recommendation |
|---|---|---|---|---|---|---|---|---|---|---|

Recommendation: Build Now · Validate First · Technical Foundation First · Later ·
Reject · Not Applicable.

## 12. Detailed Feature Proposals

Up to ten. Per proposal:

### FEAT-001 — <name>

**Problem** · **Target users** · **Current evidence** · **Proposed capability** ·
**User flow** · **Functional requirements** (testable) ·
**Non-functional requirements** (mapped to ISO/IEC 25010:2023) ·
**Security and privacy requirements** (mapped to ASVS/MASVS/applicable regulation) ·
**Technical design direction** (direction, not final implementation) ·
**Data model changes** · **API/protocol changes** · **UI/UX changes** ·
**Telemetry and metrics** (with data-minimization justification) ·
**Failure and recovery behaviour** · **Dependencies** (including `BUG-XXX`) ·
**Risks and trade-offs** · **Acceptance criteria** (Given/When/Then) ·
**Test strategy** · **Effort** · **Rollout strategy** · **Success metrics**.

## 13. Technical Foundations

Work that is not user-facing but gates everything else: state-machine
stabilization, architectural separation, dependency injection, test harness,
protocol/audio/storage abstraction, secure storage, structured logging, crash
reporting, feature flags, configuration schema and migration, CI quality gate,
release pipeline, observability. Reference the `BUG-XXX` findings that motivate
each one.

## 14. Roadmap

**Phase 0 — Stabilization**: critical defects, security blockers, test harness,
observability.
**Phase 1 — Core reliability**: the failure modes users actually hit.
**Phase 2 — Experience**: workflow, accessibility, configuration safety, feedback.
**Phase 3 — Operability at scale**: administration, fleet, provisioning, audit trail.
**Phase 4 — Differentiation**: integrations, analytics, advanced capability.

Per phase: objective · features · dependencies · exit criteria · main risk · KPI.

Use relative sprints or months. Do not invent calendar dates; state that team
capacity is needed to convert to a calendar.

## 15. Product Metrics

Proposed metrics with baselines and thresholds. Every telemetry item states what
is collected, why it is minimal, where it goes, retention, and opt-out.

## 16. Validation Plan

Per major assumption: hypothesis · target user · method · prototype requirement ·
data required · success threshold · stop condition · decision after the result.

## 17. Risks and Strategic Trade-offs

Feature creep · complexity growth · platform restrictions · performance and
battery · security versus operability · central management versus autonomy ·
telemetry versus privacy · hardening versus supportability · backward
compatibility · fragmentation · support burden · regulatory dependency.

## 18. Final Recommendations

Top 5 immediate actions · top 5 feature opportunities · features to reject with
reasons · technical blockers · research gaps · the next decision to make · a
proposed owner role per item.

## 19. References

| Source | Publisher | Version / date | URL | Accessed | Type |
|---|---|---|---|---|---|
