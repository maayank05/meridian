# 11 — Change Log

Status: Living document · Last updated: 2026-10-31

Records changes to approved scope, requirements or definitions. Decisions with their rationale are in [DECISIONS.md](../docs/DECISIONS.md).

| CR ID | Date | Change | Reason | Requested / approved by | Affected items | Status |
|---|---|---|---|---|---|---|
| CR-001 | 2026-10-31 | Add **FR-030**: synthetic marketing campaign scenario model with methodology and limitations | M03 has no functional requirement in `instructions/02`; the user selected option A + B (D-015) | Project owner | BR-11, FR-030, US-027, US-028, Y01–Y04, M03 | Approved |
| CR-002 | 2026-10-31 | Business rules use the prefix `RULE-` and business requirements use `BR-` | Avoid ID collision between the two BA artefacts | Implementer (documentation convention) | 03_BRD, 07_business_rules | Applied (no scope change) |
| CR-003 | 2026-10-31 | Data dictionary moved from Phase 1 to Phase 2; executive findings report to Phase 11 | The data dictionary needs profiled types, nulls and domains; findings need validated analysis | Approved in Phase 1 plan | FR-040 deliverables | Approved |
| CR-005 | 2026-11-06 | M03 synthetic campaign scenario uses deterministic, user-entered assumptions instead of a seeded random spend generator | Lean scope; random generation adds no analytical value | Implementer (within D-015 scope; flagged for owner review) | FR-030, Y01-Y04, 14_M03 §3 | Applied |
| CR-004 | 2026-10-31 | Add **K26 Unavailable Order Rate**; K12 restricted to `canceled` | D-019(a): report `unavailable` separately from cancellation | Project owner | K12, K26, RULE-26 | Approved |
