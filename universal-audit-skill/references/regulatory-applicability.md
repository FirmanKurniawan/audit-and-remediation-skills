# Regulatory Applicability Model

A repository audit can observe what the code does. It cannot determine legal
compliance, which depends on the data-subject population, the processing purpose,
contracts, the organisation's records, and — in the end — a lawyer. Confusing the
two produces findings that are simultaneously alarming and useless.

## Applicability is a recorded judgement

Every regulatory finding declares one of:

| Value | Meaning |
|---|---|
| `Applicable` | A trigger is established by evidence (product is sold in the EU; cardholder data is processed in this code; the product is a medical device). |
| `Potentially Applicable` | The code shows a trigger-shaped signal, but the deciding fact is outside the repository. |
| `Not Applicable` | Checked and ruled out, with the reason. |
| `Applicability Unconfirmed` | Not yet assessed. Honest, and better than guessing. |

`rationale` is mandatory (F053). It states what evidence established the value
and what is still missing.

## Finding types

| Value | Use when |
|---|---|
| `Potential Compliance Gap` | Applicability is `Applicable` or `Potentially Applicable`, and the code does not implement a control the regime expects. |
| `Control Gap With Evidence` | Applicability is `Applicable` **and** the missing control is demonstrated in code. Not permitted at lower applicability (F055). |
| `Observation` | Worth knowing, not yet a gap. |
| `Not Applicable` | Recorded so a later pass does not redo the analysis. |

## Language

These phrases are rejected by the validator (F057) anywhere in a regulatory
finding: *non-compliant*, *violates GDPR*, *GDPR violation*, *breaches GDPR*,
*certified compliant*, *is compliant with*, *fully compliant*, *legally
compliant*.

Write instead:

> **Potential Compliance Gap — UU PDP No. 27/2022 (Potentially Applicable).** No
> retention period is defined for stored contact records
> (`src/store/contacts.ts:41`, verified 2026-09-10) and no deletion path exists
> (absence evidence: `.audit/evidence/delete-path-search.txt`). Applicability
> depends on whether data subjects are in Indonesia, which the repository does
> not establish; confirm with the product owner. A data-protection specialist
> should assess the retention obligation.

That is defensible, actionable, and does not pretend to be legal advice.

## Common triggers

| Regime | Trigger established by | Usually confirmable in the repo? |
|---|---|---|
| GDPR | Personal data of EU data subjects | No — jurisdiction is external |
| UU PDP 27/2022 | Personal data of Indonesian data subjects | No |
| CCPA/CPRA | California residents, business thresholds | No |
| PCI DSS | Cardholder data stored, processed or transmitted | Often yes — look for PAN handling |
| HIPAA | Protected health information, covered entity relationship | Partly |
| EU CRA | Product with digital elements placed on the EU market | No — market placement is external |
| NIS2 | Sector and entity size | No |
| IEC 62443 | Industrial control system context | Partly — the code shows the domain |
| EN 301 549 | Public-sector procurement in the EU | No |

Notice how many are "no". That is the point: for most regimes the honest default
is `Potentially Applicable` or `Applicability Unconfirmed`, and the audit's job
is to surface the control gap and name the question that decides applicability.

## What the audit *can* assert

Accessibility criteria (WCAG 2.2 success criteria are testable), the presence or
absence of a machine-readable SBOM, whether a deletion path exists, whether
consent is collected before a tracking SDK initialises, whether logs contain
personal data. These are code facts. Report them as code facts and let the
applicability field carry the legal uncertainty.
