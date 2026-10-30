# Phase Checkpoint
Phase: 2 — Dataset discovery and profiling
Date: 2026-10-31
Status: **PASS WITH DOCUMENTED LIMITATIONS**

## Objective
Profile all nine Olist files from the actual data: rows, columns, types, missing values, keys, relationships, orphans, statuses, payments, date coverage, timestamp quality, delivered-order completeness and join fan-out. Record every data-quality issue and its impact on KPI definitions. No raw-file changes, no KPI calculation, no application code.

## Work completed
- Profiled 9 files / 1,550,922 rows with pandas, reading every column as text (no silent coercion).
- Re-computed 33 key figures independently with the standard library (`csv` + exact `Decimal`): **33 matched, 0 differed**.
- Ran follow-up queries for fan-out, shipping-limit outliers, review timing, the purchase-hour pattern and reconciliation profiles.
- Generated all report documents **programmatically from the JSON** (no hand-typed numbers), then reviewed them by hand. The review fixed 3 wording issues, including one unverified claim.
- Updated the KPI dictionary, business rules, assumptions, RAID, decisions, spec, limitations and traceability.
- Found and corrected a Phase 1 error: the source has **52 columns, not 57**.

## Deliverables
| # | Deliverable | File |
|---|---|---|
| 1 | Dataset profiling report | [PROFILING_REPORT.md](../data/PROFILING_REPORT.md) |
| 2 | Data dictionary (52 columns, proposed MySQL types) | [DATA_DICTIONARY.md](../data/DATA_DICTIONARY.md) |
| 3 | Data-quality issue register (23 issues) | [DATA_QUALITY_ISSUES.md](../data/DATA_QUALITY_ISSUES.md) |
| 4 | Relationship and join validation | [RELATIONSHIP_VALIDATION.md](../data/RELATIONSHIP_VALIDATION.md) |
| 5 | Impact on KPI definitions | [KPI_IMPACT.md](../data/KPI_IMPACT.md) + edits to `business/08`, `07`, `09`, `10` |
| 6 | Requirements/status updates | REQUIREMENTS_TRACEABILITY, PROJECT_STATUS, KNOWN_LIMITATIONS, PROJECT_SPEC, DECISIONS (D-018, D-019) |
| — | Machine-readable aggregates | [profile_results.json](../data/profile_results.json) (aggregates only, 44 KB) |

## Key verified facts (details in the reports)
- **Keys:** order_id, (order_id, order_item_id), (order_id, payment_sequential), product_id, seller_id and customer_id are all unique. **`review_id` is not unique** (789 shared across orders); `(review_id, order_id)` is.
- **Referential integrity:** 0 orphans on every transactional relationship. Gaps only in reference data: 2 untranslated categories, and 278 customer / 7 seller zip prefixes missing from geolocation.
- **Customers:** customer_id is 1:1 with orders; 96,096 people (customer_unique_id) across 99,441 customer_ids.
- **Statuses:** exactly the 8 expected values; `delivered` = 96,478 orders (D-016 confirmed).
- **Delivered completeness:** 8 delivered orders lack a delivery date, 1 lacks payments, 0 lack items.
- **Coverage:** 2016-11 empty; 2016-09/12 near-empty; 2018-09/10 have 0 delivered orders → D-018.
- **Payments:** match price + freight within 0.01 for 98,362 of 98,665 orders. Payments are higher in 264 orders, lower in 39.
- **Fan-out (measured):** joining items to payments turns 112,647 rows into 117,601 (2,936 orders affected; Σ price would be overstated by 4.54%).
- **Timestamps:** 0 parse failures. Estimated delivery is date-only. Ordering violations are confined to the carrier date (1,359 carrier-before-approval).

## Commands actually executed
- `sha256sum data/raw/olist/*.csv` (before) and SHA-256 re-check at the gate
- `py -3.13 -m venv <scratch>/profvenv` + `pip install pandas` → pandas 3.1.0, numpy 2.5.4
- `profvenv/python -I profile_olist.py <raw> profile.json` (35 s)
- `py -3.13 -I verify_stdlib.py <raw> profile.json`
- `profvenv/python -I followups.py <raw> followups.json`
- `py -3.13 -I build_reports.py`, `apply_phase2.py`, `apply_phase2_control.py`
- `py -3.13 -I phase2_check.py <repo> <scratch>` (2 runs) and `phase1_check.py` (regression); 2 mutation-test rounds on scratch copies
- `git commit` / `git push` for Phase 1 (`8517a64`)

## Test results
| Check | Result |
|---|---|
| Phase 2 gate, run 1 | 17 passed, 1 failed (Q04 → the 52-vs-57 column error) |
| Phase 2 gate, run 2 | **18 passed, 0 failed, 0 skipped** |
| Phase 1 regression | **51 passed, 0 failed, 0 skipped** |
| Independent recomputation | **33 matched, 0 differed** |
| Raw-file hashes | **9/9 unchanged** |
| Mutation tests | 5/5 caught (after correcting one test-setup error) |
| Ruff / Pytest / frontend | Not applicable: no application code (profilers stay in the scratchpad) |

Q10 deserves a mention: the checker computes K01, K02 and AOV in memory and asserts that none of those values appears in any document. This is how "no KPI calculated in the docs" is proven rather than just claimed.

## Acceptance criteria evidence
| Scope item | Evidence |
|---|---|
| All 9 files: rows, columns, types, missing | PROFILING_REPORT §1–2; DATA_DICTIONARY (Q04: 52/52 columns) |
| PK/FK, duplicates, orphans | PROFILING_REPORT §3; RELATIONSHIP_VALIDATION §1–2 |
| Statuses and payment distributions | PROFILING_REPORT §4, §7 |
| Date coverage and timestamp quality | PROFILING_REPORT §6 |
| Delivered-order completeness | PROFILING_REPORT §5 |
| Fan-out / double counting | RELATIONSHIP_VALIDATION §3 (measured) |
| All DQ issues documented | DATA_QUALITY_ISSUES (23; Q06/Q07) |
| Raw files unmodified | Q01 |
| No unsupported KPIs or invented findings | Q10, Q11; every number generated from JSON and cross-verified (Q03, Q09) |

## Defects and unresolved issues
- **Corrected:** the Phase 1 column total (57 → 52). Correction notes were added to the historical documents.
- No open defects in the deliverables.

## Known limitations
- Business meaning of fields (e.g. "seller deadline") comes from public documentation and can't be proven from the data.
- The timezone is still an assumption (A-02). The hour-of-day pattern is consistent with local time but isn't proof.
- Proposed MySQL types are not yet validated by DDL (Phase 3).
- The profiler scripts aren't committed (no application code allowed in Phase 2). Proposal: commit them under `scripts/profiling/` with tests in Phase 3.

## Requirements traceability changes
In progress: FR-011, FR-015 and NFR-010 (profiling evidence; pipeline not built), plus FR-040 (data dictionary). Nothing is marked Complete.

## Decisions requested
- **D-018** default analysis window: recommend 2017-01-01 to 2018-08-31, with the full range selectable and flagged.
- **D-019** (a) K12 = `canceled` only, with `unavailable` reported separately; (b) K13 at order level with `(review_id, order_id)` grain; (c) K17 kept but labelled low confidence, with exclusions; (d) K20 excludes the 2 zero-instalment credit-card records.

## Next phase recommendation
Phase 3 — MySQL design and ingestion. Prerequisites: Q-5 (local databases, app user, `.env`), the D-017 timestamp decision, and D-018/D-019.

## User approval requested
Approve the Phase 2 checkpoint and decide D-018/D-019. The Phase 2 commit will be prepared as a separate staged list for your review.

---
## Post-review addendum (2026-10-31)
The body above is a point-in-time record. Outcome of the user's review:
- **Accepted with documented limitations** as a completed dataset-profiling milestone. This does **not** validate the future application or analytics.
- **D-018 accepted:** default window 2017-01-01 to 2018-08-31; full range accessible with flags (RULE-25).
- **D-019 accepted with conditions:** K12 `canceled` only, with `unavailable` reported as new K26 (CR-004); K13 mean per order, with 789 shared review_ids linking 1,412 orders documented as non-independent (RULE-15); K17 low-confidence with RULE-27 exclusions; K20 excludes 2 zero-instalment credit-card records with the count reported (RULE-28).
- The KPI catalogue now has 26 observed/derived KPIs (K01–K26).
