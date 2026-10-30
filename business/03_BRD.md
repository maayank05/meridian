# 03 — Business Requirements Document (BRD)

Status: Draft v0.1 (Phase 1) · Last updated: 2026-10-31

Business requirements state **what the business needs and why**. Functional detail is in [04_FRD.md](04_FRD.md). Each BR maps to at least one FR. Priorities use MoSCoW (Must / Should / Could / Won't-this-release).

| BR ID | Business requirement | Rationale | Stakeholders | Objective | Priority | Realised by (FR) |
|---|---|---|---|---|---|---|
| BR-01 | Leadership needs a single, trusted view of commercial performance with drill-down and period comparison | Conflicting revenue figures undermine decisions | SH-01, SH-02 | Obj 3, 4 | Must | FR-001, FR-002, FR-003, FR-004, FR-005, FR-020 |
| BR-02 | Commercial teams need to understand customer purchase behaviour, repeat purchasing and retention | Retention and concentration risk are invisible today | SH-01, SH-03, SH-04 | Obj 3 | Must | FR-021 |
| BR-03 | Category managers need product and category performance, including review patterns | Under-performing categories are found late | SH-04 | Obj 3 | Must | FR-022 |
| BR-04 | Operations needs seller and fulfilment performance with explicit denominators | Delivery problems cannot be traced to sellers or regions | SH-05, SH-04 | Obj 3 | Must | FR-023 |
| BR-05 | Finance needs revenue reconciliation and scenario economics **without** unsupported profit claims | Missing costs must not be hidden or assumed zero | SH-02 | Obj 3, 6 | Must | FR-024 |
| BR-06 | Leadership needs to compare decision scenarios with visible assumptions and downside cases | Decisions are debated without consistent economics | SH-01, SH-02 | Obj 6 | Must | FR-026 |
| BR-07 | Leadership wants forward-looking estimates and statistical evidence **only where justified** | Forecasts without baselines and uncertainty mislead | SH-01, SH-02, SH-06 | Obj 3 | Should | FR-027 |
| BR-08 | All users need to trust the data: validated ingestion, lineage, quality monitoring and impact explanations | Data issues currently surface after reports are distributed | SH-06, SH-08 | Obj 1, 2 | Must | FR-010, FR-011, FR-012, FR-013, FR-014, FR-015, FR-025 |
| BR-09 | Leadership needs a regular, reproducible executive report built from the same numbers as the app | Manual reporting drifts from source | SH-01 | Obj 3 | Must | FR-028 |
| BR-10 | BI users need equivalent, reconciled reporting in Power BI | Power BI is the organisation's BI tool (simulated) | SH-06, SH-02 | Obj 5 | Should | FR-029 |
| BR-11 | Marketing needs a transparent way to reason about campaign investment, while being honest that observed marketing data does not exist | No spend or attribution data is available (H-05) | SH-03, SH-02 | Obj 6 | Should | FR-030 |
| BR-12 | The organisation needs governed, documented, reproducible and teachable delivery | Knowledge transfer and auditability | SH-07, SH-09, SH-10 | Obj 7, 8 | Must | FR-040, FR-041, FR-042, FR-043 |

Non-functional requirements (NFR-001 … NFR-010) support all BRs; see [05_NFR.md](05_NFR.md).
