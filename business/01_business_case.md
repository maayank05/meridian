# 01 — Business Case, Problem Statement, Objectives and Scope

Status: Draft v0.1 (Phase 1) · Last updated: 2026-10-31

> **Simulation notice.** Northstar Commerce is a **simulated** company. Its "observed" sales, customers, products, sellers, payments, reviews and deliveries are the public Olist Brazilian e-commerce records (CC BY-NC-SA 4.0). Its organisation, stakeholders, processes, pains and budgets are **illustrative assumptions** written for this project. Nothing here describes Olist's real organisation or a real company's processes.

## 1. Problem statement
Northstar's management has sales, customer, product, seller, payment, review and fulfilment information spread across separate extracts. There is no single agreed definition of revenue, no regular data-quality checks, and no structured way to test a proposed decision against stated assumptions. As a result (illustrative, not measured):
- Different teams can report different "revenue" figures for the same period.
- Operational problems (late deliveries, poor reviews) are hard to tie to specific sellers, categories or regions.
- Proposed actions (discounts, delivery improvements, marketing spend) are debated without consistent, transparent economics.
- Data issues are found late, after they have distorted reports.

## 2. Business case
MERIDIAN creates one governed analytical foundation and decision-support layer:
- **Trust:** one canonical definition per KPI, reconciled across SQL, Python, API, React and Power BI.
- **Diagnosis:** drill-down from headline KPIs to category, seller, geography and customer cohorts.
- **Decision support:** scenario models with explicit assumptions, ranges and downside cases.
- **Transparency:** every number labelled as observed, derived, synthetic assumption, forecast or scenario output.

**Benefit statement.** No financial benefit is claimed. The Olist data contains no cost, margin or decision-outcome data, so any benefit estimate would be fabricated. Benefits are expressed as capabilities with measurable acceptance criteria (§5). Scenario estimates produced later are labelled hypothetical.

## 3. Objectives (from charter `instructions/01`)
| ID | Objective |
|---|---|
| Obj 1 | Reproducible data ingestion and transformation pipeline |
| Obj 2 | Tested MySQL analytical data model |
| Obj 3 | Trustworthy SQL and Python analytical outputs |
| Obj 4 | React application backed by FastAPI |
| Obj 5 | Power BI reporting specification and genuine report where possible |
| Obj 6 | Transparent quantification of business scenarios |
| Obj 7 | Complete BA/BI documentation set |
| Obj 8 | Teachable product via structured learning guide |

## 4. Scope
**In scope (initial release):** the ten modules M01–M10, ingestion pipeline, MySQL model, FastAPI, React app, Power BI specification (plus a PBIX authored by the project owner per D-012), HTML executive report, BA documentation, learning guide, CI, and Render deployment with persistent managed MySQL.

**M03 scope (D-015):** a synthetic campaign scenario model plus methodology and limitations documentation. No observed marketing performance is claimed.

**Out of scope:** real-time streaming; multi-tenant SaaS; payment processing; real customer outreach or campaign execution; causal claims without experimental or quasi-experimental evidence; ERP integration; infrastructure not justified by requirements.

## 5. Success measures (testable)
| ID | Measure | Evidence type |
|---|---|---|
| SM-01 | A new developer sets up the project from documented instructions | Clean-clone run log (Phase 13) |
| SM-02 | The dataset ingests reproducibly; a re-run produces identical row counts and checksums | Pytest integration evidence (Phase 3) |
| SM-03 | Core KPIs reconcile to source records or documented reference calculations | Reconciliation tests (Phases 4–5) |
| SM-04 | Important business logic has automated tests | QUALITY_REPORT counts |
| SM-05 | All ten modules carry an explicit, evidence-backed status | Traceability matrix |
| SM-06 | CI runs without private credentials using fixtures | GitHub Actions run (Phase 12) |
| SM-07 | The deployed app is reachable and smoke-tested | Deployment smoke log (Phase 12) |
| SM-08 | Key KPIs trace to definition → SQL/Python → source field | KPI dictionary + tests |
| SM-09 | Simulated assumptions are visibly labelled | UI/API provenance tests (Phases 8–9) |

## 6. Constraints
Approved stack only (D-001). Olist data cannot be redistributed in the repo (D-013). The project is built and run by a single project owner using an AI coding agent; budget for hosting is still open (Q-6).
