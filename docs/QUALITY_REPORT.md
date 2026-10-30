# Quality Report

Every row records a check that was **actually executed**. Counts are copied from command output. Nothing is pre-filled.

| Date | Layer | Command/check | Result | Passed | Failed | Skipped | Evidence |
|---|---|---|---:|---:|---:|---:|---|
| 2026-10-31 | Environment | Tool/version probe (`git`, `py -0p`, `node`, `npm`, `mysqld --version`, service list, port 3306, Power BI package, PyPI/npm reachability) | Completed | — | — | — | [PHASE_00_CHECKPOINT.md §3](checkpoints/PHASE_00_CHECKPOINT.md) |
| 2026-10-31 | Docs | Phase 0 consistency script, run 1 (before STATUS/QUALITY docs existed) | FAIL (expected) | 18 | 2 | 0 | C01 missing PROJECT_STATUS/QUALITY_REPORT; C09 broken link to QUALITY_REPORT |
| 2026-10-31 | Docs | Phase 0 consistency script, run 2 (after fixes) | PASS | 20 | 0 | 0 | [PHASE_00_CHECKPOINT.md §5](checkpoints/PHASE_00_CHECKPOINT.md) |
| 2026-10-31 | Python lint | `ruff check .` | Not run (N/A) | — | — | — | No Python code exists; Ruff not yet installed (Phase 3) |
| 2026-10-31 | Python tests | `pytest` | Not run (N/A) | — | — | — | No tests exist yet (Phase 3) |
| 2026-10-31 | Frontend | lint/test/build | Not run (N/A) | — | — | — | No frontend exists yet (Phase 9) |
| 2026-10-31 | Docs | Phase 0 consistency script, run 3 (after approval updates) | PASS | 20 | 0 | 0 | Re-run after DECISIONS/STATUS/TRACEABILITY/LIMITATIONS edits |
| 2026-10-31 | Git hygiene | `git add --dry-run -A`; `git check-ignore` on all 9 Olist CSVs (present locally) and on secret/venv/build paths; regex secret scan over the 31 candidate files | PASS | 31 files clean | 0 | 0 | No CSV/env/key/binary staged. One local profile path removed from the checkpoint before staging |
| 2026-10-31 | Docs | Phase 0 consistency script, run 4 (after D-012–D-014 approvals and licence wording) | PASS | 20 | 0 | 0 | Pre-staging re-run |
