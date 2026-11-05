# Phase Checkpoint — Milestone A (Phase 3: MySQL design and ingestion)
Date: 2026-11-06
Status: **PASS WITH DOCUMENTED LIMITATIONS**

## Delivered
- **Environment:** `.venv` (Python 3.13.2) with hashed lockfiles (`requirements/*.txt`, installed with `--require-hashes`); `pyproject.toml` (package, Pytest, Ruff); `.env.example` with empty passwords.
- **Config and DB access:** `backend/meridian/config.py` (passwords as `SecretStr`), `db.py` (SQLAlchemy Core + PyMySQL, TLS, UTC sessions, test-database guard).
- **Migrations:** runner with `schema_version` and checksum guard; `0001` audit + raw, `0002` staging (+ `stg_tz_map`), `0003` marts (`dim_date`, `dim_customer`, `dim_product`, `dim_seller`, `fact_orders`, `fact_order_items`, `fact_payments`, `fact_reviews`) with stated grain, PK/FK/CHECK constraints.
- **Pipeline:** `python -m meridian.ingestion`. Strict file/header validation, then one transaction: clear → raw load → staging → D-017 timezone map → 27 data-quality checks (6 blocking) → marts → audit. Failed runs roll back and are audited.
- **Profiling scripts:** `scripts/profiling/` (4 scripts, README, fixture tests). **Reconciliation:** `scripts/verify_dev_load.py`.
- **Synthetic fixture:** deterministic generator + 9 small CSVs with planted edge cases; hand-calculated expectations in `backend/tests/expected.py`.

## Evidence (commands actually run)
| Check | Result |
|---|---|
| DB accounts via app engines | 3 accounts @localhost, global `USAGE` only, 13 / 2 / 13 privileges, TLS on, session tz `+00:00` |
| `ruff check .` / `ruff format --check .` | Pass |
| `pytest` (all) | **42 passed, 0 failed, 0 skipped** (26 unit, 13 MySQL integration, 3 profiling) |
| Full load into `meridian_dev` | Run 1 succeeded: 1,550,922 raw rows in 271.5 s |
| `scripts/verify_dev_load.py` | **28 matched, 0 differed**: row counts, per-file SHA-256, Decimal sums (price, freight, payments) CSV vs marts, item vs order grain (no fan-out), profile cross-checks |
| Full-data DQ results | Identical to the Phase 2 profile (e.g. 775 orders without items, 1,359 carrier-before-approval, 789 shared review_ids, 303 payment mismatches) |
| D-017 timezones | 39 ambiguous timestamps (38 distinct values) with UTC NULL + flag; 0 non-existent |
| Phase 2 reproducibility | 4 scripts re-run → 5 generated documents byte-identical to the committed ones |
| Raw files | SHA-256 identical to Phase 2 |

## Acceptance criteria
| Criterion (Milestone A) | Evidence |
|---|---|
| Locked dependencies, config, `.env.example` | `--require-hashes` install; `test_settings_repr_never_shows_passwords` |
| Migration runner + schema version | `test_migrations_are_recorded_and_edits_detected` |
| Raw, staging, audit, dims, facts | Migrations 0001–0003; `test_clean_load_row_counts` |
| Ingestion of all 9 files | Run 1; `verify_dev_load.py` 28/28 |
| Validation, audit metadata, DQ checks | `test_quality_results_match_hand_calculation`, `test_missing_file_fails_before_any_write` |
| Idempotent repeat load | `test_repeat_load_is_idempotent` (table checksums identical) |
| Rollback | `test_failed_run_rolls_back_and_is_audited`, `test_invalid_value_fails_under_strict_mode_and_rolls_back` |
| Deterministic rebuild | `test_rebuild_from_scratch_is_deterministic` |
| Relationships, reconciliation | `test_relationships_and_flags`, `test_reconciliation_raw_to_marts` |
| D-017 tests (normal / gap / ambiguous / boundaries) | `test_timezones.py` (15 cases) + `test_timezone_columns` |
| Profiling scripts with fixture tests and reproduction guide | `scripts/profiling/tests`, `scripts/profiling/README.md` |

## Defects found and fixed during the milestone
1. `followups.py` crashed on empty selections (latent Phase 2 bug, exposed by the fixture test). Fixed; real-data outputs unchanged (byte-identical).
2. A rollback test accepted any exception. Tightened to MySQL error 1366, which revealed that driver errors arrive unwrapped (PyMySQL `DataError`).
3. Hashed dependency compilation took over 10 minutes (it downloads every platform wheel). It ran in the background and the hashed lock was adopted, so D-003 is met.

## Limitations
See [KNOWN_LIMITATIONS.md](../KNOWN_LIMITATIONS.md) (L-A02–L-A06): full refresh only; local TLS not certificate-verified (D-020); geolocation averaged per zip; 85 review dates with a time stored as DATE; reload determinism proven on the fixture, not by a second full-data run. **No KPI values are calculated or reported yet** (Milestone B).

## Next
Milestone B: core SQL analytics, Python services, SQL/Python reconciliation, one forecast vs a naive baseline, compact decision simulator.
