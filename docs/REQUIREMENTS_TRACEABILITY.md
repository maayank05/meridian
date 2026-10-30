# Requirements Traceability Matrix

Last updated: 2026-10-31 (Phase 1)

A requirement is **Complete** only when it maps to implementation, an executed test, and recorded evidence. Statuses: Not started · In progress · Complete · Partial (documented limitation) · Blocked · Deferred · Unsupported by source data.

"—" means not yet assigned. Test IDs ending in **(planned)** are reservations from the user stories. They are **not evidence**: a test counts only after it appears in QUALITY_REPORT with an executed result.

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
| FR-030 | Synthetic marketing campaign scenario model with methodology and limitations (added via CR-001 / D-015) | Obj 6 | M03 | [14_M03_marketing_methodology.md](../business/14_M03_marketing_methodology.md) (methodology draft) | TST-US-027, TST-US-028 (planned) | Phase 1: methodology drafted; model not built | In progress |
| FR-040 | BRD, FRD, stories, AC, process flows, KPI/data dictionaries, RAID, traceability | Obj 7 | M09 / BA | [business/](../business/) 01–14; data dictionary deferred to Phase 2 (CR-003) | TST-US-029 (planned) | Phase 1: 14 BA documents drafted; automated doc-consistency checks pass (see QUALITY_REPORT) | In progress |
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

## Business requirement → functional requirement → user story

Generated from [04_FRD.md](../business/04_FRD.md) and [06_user_stories.md](../business/06_user_stories.md); verified by the Phase 1 consistency check.

| BR | FR | User stories (priority) | Planned test IDs |
|---|---|---|---|
| BR-01 | FR-001 | US-001 (Must) | TST-US-001 |
| BR-01 | FR-002 | US-002 (Must) | TST-US-002 |
| BR-01 | FR-003 | US-003 (Must) | TST-US-003 |
| BR-01 | FR-004 | US-004 (Must) | TST-US-004 |
| BR-01 | FR-005 | US-005 (Must) | TST-US-005 |
| BR-08 | FR-010 | US-006 (Must) | TST-US-006 |
| BR-08 | FR-011 | US-007 (Must) | TST-US-007 |
| BR-08 | FR-012 | US-008 (Must) | TST-US-008 |
| BR-08 | FR-013 | US-009 (Must) | TST-US-009 |
| BR-08 | FR-014 | US-010 (Must) | TST-US-010 |
| BR-08 | FR-015 | US-011 (Must) | TST-US-011 |
| BR-01 | FR-020 | US-012 (Must), US-013 (Should) | TST-US-012, TST-US-013 |
| BR-02 | FR-021 | US-014 (Must), US-015 (Should) | TST-US-014, TST-US-015 |
| BR-03 | FR-022 | US-016 (Must) | TST-US-016 |
| BR-04 | FR-023 | US-017 (Must), US-018 (Should) | TST-US-017, TST-US-018 |
| BR-05 | FR-024 | US-019 (Must), US-020 (Must) | TST-US-019, TST-US-020 |
| BR-08 | FR-025 | US-021 (Should) | TST-US-021 |
| BR-06 | FR-026 | US-022 (Must) | TST-US-022 |
| BR-07 | FR-027 | US-023 (Should), US-024 (Could) | TST-US-023, TST-US-024 |
| BR-09 | FR-028 | US-025 (Must) | TST-US-025 |
| BR-10 | FR-029 | US-026 (Should) | TST-US-026 |
| BR-11 | FR-030 | US-027 (Should), US-028 (Must) | TST-US-027, TST-US-028 |
| BR-12 | FR-040 | US-029 (Must) | TST-US-029 |
| BR-12 | FR-041 | US-030 (Must) | TST-US-030 |
| BR-12 | FR-042 | US-031 (Must) | TST-US-031 |
| BR-12 | FR-043 | US-032 (Must) | TST-US-032 |

NFRs are verified through measurable criteria in [05_NFR.md](../business/05_NFR.md), not user stories.
