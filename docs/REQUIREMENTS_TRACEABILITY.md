# Requirements Traceability Matrix

Last updated: 2026-10-31 (Phase 0)

A requirement is **Complete** only when it maps to implementation, an executed test, and recorded evidence. Statuses: Not started · In progress · Complete · Partial (documented limitation) · Blocked · Deferred · Unsupported by source data.

"—" means not yet assigned. Test IDs are allocated when tests are written; none are invented in advance.

## Functional requirements

| Requirement ID | Requirement | Business objective | Module | Files/API | Test ID | Evidence | Status |
|---|---|---|---|---|---|---|---|
| FR-001 | Responsive React app with clear navigation | Obj 4 | Platform | — | — | — | Not started |
| FR-002 | FastAPI REST endpoints: health, metadata, filters, analytics | Obj 4 | Platform | — | — | — | Not started |
| FR-003 | Consistent loading/empty/validation/error states | Obj 4 | Platform | — | — | — | Not started |
| FR-004 | Documented date and dimension filters | Obj 3, 4 | Platform | — | — | — | Not started |
| FR-005 | Show freshness, source, definition, provenance class | Obj 3, 6 | Platform | — | — | — | Not started |
| FR-010 | Repeatable Python ingestion of local Olist files | Obj 1 | Data | — | — | — | Not started (needs dataset, Q-2) |
| FR-011 | Validate files, columns, types, keys, relationships | Obj 1, 2 | Data / M09 | — | — | — | Not started |
| FR-012 | Preserve raw data, record ingestion metadata | Obj 1 | Data | — | — | — | Not started |
| FR-013 | Ordered SQL transformations to analytical tables | Obj 2 | Data | — | — | — | Not started |
| FR-014 | Explicit, safe rebuild/reload | Obj 1 | Data | — | — | — | Not started |
| FR-015 | Ingestion and data-quality reports | Obj 1, 3 | Data / M09 | — | — | — | Not started |
| FR-020 | Executive commercial KPIs | Obj 3 | M01 | — | — | — | Not started |
| FR-021 | Customer purchase, cohort, segmentation | Obj 3 | M02 | — | — | — | Not started |
| FR-022 | Product/category performance | Obj 3 | M04 | — | — | — | Not started |
| FR-023 | Seller and fulfilment analysis | Obj 3 | M05 | — | — | — | Not started |
| FR-024 | Financial reconciliation and scenarios, no unsupported profit | Obj 3, 6 | M06 | — | — | — | Not started |
| FR-025 | Data-quality monitoring and downstream impact | Obj 3 | M09 | — | — | — | Not started |
| FR-026 | Scenario comparison with documented assumptions | Obj 6 | M07 | — | — | — | Not started |
| FR-027 | Statistics and forecasts only when justified | Obj 3 | M08 | — | — | — | Not started |
| FR-028 | Reproducible executive report | Obj 3 | M10 | — | — | — | Not started |
| FR-029 | Power BI model + DAX docs with reconciliation tests | Obj 5 | Power BI | — | — | — | Not started |
| FR-040 | BRD, FRD, stories, AC, process flows, KPI/data dictionaries, RAID, traceability | Obj 7 | M09 / BA | This file (skeleton) | — | Phase 0: matrix created | In progress |
| FR-041 | Architecture, lineage, decisions, limitations | Obj 7 | Docs | [PROJECT_SPEC.md](PROJECT_SPEC.md), [DECISIONS.md](DECISIONS.md), [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) | — | Phase 0: drafts created; lineage pending Phase 3 | In progress |
| FR-042 | Learning materials | Obj 8 | Learning | — | — | — | Not started |
| FR-043 | Reproducible setup/test/pipeline/deploy instructions | Obj 8 | Docs | [DEPLOYMENT_RUNBOOK.md](DEPLOYMENT_RUNBOOK.md) (skeleton) | — | — | In progress |

## Non-functional requirements

| Requirement ID | Requirement | Business objective | Module | Files/API | Test ID | Evidence | Status |
|---|---|---|---|---|---|---|---|
| NFR-001 | Security: secrets in env/secret manager, none in Git | All | Platform | [.gitignore](../.gitignore), [SECURITY.md](SECURITY.md) | — | Phase 0: `.env` ignore rules created; not yet tested by a secret scan | In progress |
| NFR-002 | Reliability: failure modes, transactions, retries | Obj 1 | Platform | — | — | — | Not started |
| NFR-003 | Performance: pagination, aggregate in MySQL | Obj 4 | Platform | — | — | — | Not started |
| NFR-004 | Maintainability: layered backend, modular React | All | Platform | [PROJECT_SPEC.md §3](PROJECT_SPEC.md) | — | Design only | Not started |
| NFR-005 | Testability: unit/integration/API/SQL/frontend/E2E | All | Platform | [TEST_STRATEGY.md](TEST_STRATEGY.md) | — | Strategy only | Not started |
| NFR-006 | Accessibility | Obj 4 | Frontend | — | — | — | Not started |
| NFR-007 | Observability: structured, non-sensitive logs | Obj 4 | Platform | — | — | — | Not started |
| NFR-008 | Reproducibility: pinned deps, deterministic fixtures | Obj 1 | Platform | — | — | — | Not started |
| NFR-009 | Portability: local setup + Render deploy docs | Obj 8 | Docs | — | — | — | Not started |
| NFR-010 | Data integrity: constraints, RI, reconciliation | Obj 2 | Data | — | — | — | Not started |

## Module acceptance criteria (from `instructions/05`)

| Requirement ID | Acceptance criterion | Module | Files/API | Test ID | Evidence | Status |
|---|---|---|---|---|---|---|
| AC-M01 | Every metric traceable to canonical calculation; filters work; no fabricated values | M01 | — | — | — | Not started |
| AC-M02 | No future leakage; cohort boundaries tested; customer-level reconciles to aggregate | M02 | — | — | — | Not started |
| AC-M03 | Observed and synthetic measures separated; assumptions/uncertainty visible | M03 | — | — | — | Not started. Scope decided (D-015): synthetic campaign scenario model + methodology/limitations docs |
| AC-M04 | Ranking grain and missing categories documented; small samples flagged | M04 | — | — | — | Not started |
| AC-M05 | Time calculations validated; invalid/missing records reported | M05 | — | — | — | Not started |
| AC-M06 | Currency, rounding, refunds, cancellations documented; missing costs never zero | M06 | — | — | — | Not started |
| AC-M07 | Calculations in Python service; known input/output tests; assumptions visible | M07 | — | — | — | Not started |
| AC-M08 | No leakage; held-out evaluation; model report; uncertainty shown | M08 | — | — | — | Not started |
| AC-M09 | Every major requirement maps to implementation, tests, evidence | M09 | This file | — | — | In progress |
| AC-M10 | Report from real outputs, timestamped, reconciled with app, includes limitations | M10 | — | — | — | Not started |
