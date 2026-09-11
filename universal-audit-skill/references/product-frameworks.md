# Product Prioritization Frameworks

## RICE

`RICE = (Reach × Impact × Confidence) / Effort`

- **Reach** — users or events affected per period. Use a real number and say where
  it came from. If you have no usage data, use a defensible proxy (number of code
  paths that touch it, share of critical flows) and label it `Assumption`.
- **Impact** — 3 massive, 2 high, 1 medium, 0.5 low, 0.25 minimal.
- **Confidence** — 100% only with data; 80% with strong evidence; 50% with an
  informed guess; below 50%, the item goes to `Validate First` rather than into
  the build queue.
- **Effort** — person-months (or person-weeks; be consistent and state the unit).

Show the inputs, not just the score. A RICE score with hidden inputs is theatre.

## Risk-adjusted strategic score

Score 1–5 each:

**Benefit:** operational impact `O`, user impact `U`, reliability improvement `R`,
security improvement `S`, differentiation `D`, commercial relevance `C`.

**Cost/risk:** implementation complexity `X`, regression risk `G`,
maintenance burden `M`, dependency risk `P`.

```
Benefit = (2·O + 2·U + 1.5·R + 1.5·S + 1·D + 1·C) / 9
Cost    = (1.5·X + 1.5·G + 1·M + 1·P) / 5
Strategic = (Benefit / Cost) × ConfidenceFactor
```

`ConfidenceFactor`: 1.0 validated with users · 0.8 strong internal evidence ·
0.6 reasonable inference · 0.4 unvalidated assumption.

State the formula and the raw scores in the report. If you change the weights for
a specific product, say why before showing results — not after.

## Disagreement handling

When RICE and the strategic score rank differently, do not average them into
mush. Present both, name the divergence, and give a recommendation with a reason.
Typically RICE favours breadth and the strategic score favours risk reduction; for
a product with reliability problems, trust the strategic score.

## Recommendation values

- `Build Now` — problem proven, design clear, no blocking defects
- `Validate First` — plausible but confidence below 60%; run the named experiment
- `Technical Foundation First` — blocked by an open Critical/High finding; name
  the `BUG-XXX` ids
- `Later` — real but outranked; state what would promote it
- `Reject` — with the reason (not the persona's problem, disproportionate cost,
  legal/licensing barrier, or it makes a worse product)
- `Not Applicable` — out of the product's scope

## Complementary frameworks

- **Kano** — separate must-be, performance, and delight features. Reliability
  fixes are usually must-be: they generate no satisfaction when present and
  severe dissatisfaction when absent, which is exactly why they get under-prioritized.
- **Jobs to be Done** — write the job story (`When <situation>, I want <motivation>,
  so I can <outcome>`) before the feature. If you cannot, you have a solution
  looking for a problem.
- **Opportunity Solution Tree** — outcome → opportunities → solutions →
  experiments. Keeps proposals traceable to an outcome.
- **MoSCoW** — only for scoping a fixed release, never for ranking a backlog.
- **Cost of Delay / WSJF** — when there is a deadline or a compliance date
  (an EU CRA milestone, a platform target-API deadline), this beats RICE.

## Foundation-first rule

A feature whose subsystem has an open Critical or High finding cannot be
`Build Now`. Building on an unstable base multiplies the defect surface and makes
the original defect harder to fix. The recommendation is
`Technical Foundation First` with the blocking ids named. This rule is not
negotiable by score.

## Metrics discipline

Every proposed feature needs a success metric defined before the build, with a
baseline and a threshold. "Improves reliability" is not a metric. "Reconnect
success rate within 30s rises from an unmeasured baseline to ≥95%, measured in
the client with a privacy-preserving counter" is.

Telemetry proposals must state what is collected, why it is the minimum needed,
where it goes, how long it is kept, and how the user can opt out.
