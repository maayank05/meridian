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
| 2026-10-31 | Git hygiene | Staged-blob re-verification: paths (csv/zip/env/key/data/), secret regex, emails, local paths, binary detection (`git grep --cached`, `--numstat`) | PASS | 31 files clean | 0 | 0 | Staged for Phase 0 commit; **not committed** (awaiting user) |
| 2026-10-31 | Data (header only) | Read first line of 9 Olist CSVs (`py -3.13 -I`, no data rows) | PASS | 9 files / 57 cols | 0 | 0 | [SOURCE_HEADERS.md](data/SOURCE_HEADERS.md); BOM in 1 file, CRLF in 2, misspelled columns noted |
| 2026-10-31 | Docs | Phase 1 consistency script, run 1 | ABORTED | 35 | 1 | 0 | Checker crashed printing `→` on cp1252 console (checker bug) after P16; P12 failed for 8 stories |
| 2026-10-31 | Docs | Phase 1 consistency script, run 2 (after fixing 2 stories, checker encoding, story regex) | FAIL | 43 | 1 | 0 | P20 false positive ("nobody mistakes revenue for profit") |
| 2026-10-31 | Checker self-test | Mutation test 1: 8 violations injected into a scratch copy | PARTIAL | 8 caught | 1 missed | 0 | P20 missed a positive "profit trend" claim (line-level negation too loose) |
| 2026-10-31 | Checker self-test | P20 rule unit cases (positive/negative lines) | PASS | 6 | 0 | 0 | Windowed negation rule |
| 2026-10-31 | Checker self-test | Mutation test 2 (P20) | FAIL then PASS | — | — | — | First re-run still missed: the regex `\b` had been written as literal backspace bytes (0x08) by a heredoc. Fixed via chr() and the mutant was then caught. Control-char scan of all docs and staged blobs: none |
| 2026-10-31 | Docs | Phase 1 consistency script, final run (after all doc updates and checkpoint) | PASS | 44 | 0 | 0 | [PHASE_01_CHECKPOINT.md](checkpoints/PHASE_01_CHECKPOINT.md) |
| 2026-10-31 | Git | Pre-commit verification: staged == approved 31 (diff vs list), Phase 1 unstaged, no data/secrets/emails/local paths, LICENSE == HEAD, noreply identity | PASS | 9 checks | 0 | 0 | Commit `7270770` pushed: `286588c..7270770 main -> main`; local == origin/main; remote tree 32 files (31 + LICENSE) |
| 2026-10-31 | Docs | D-016 applied (Option A, "Delivered Merchandise Value (Revenue Proxy)"); checker extended with P23–P31 closure checks; run on real repo | PASS | 51 | 0 | 0 | Phase 1 closure verification |
| 2026-10-31 | Checker self-test | Mutation test 3: 4 violations injected (refund wording removed, KPI renumbered, finding sentence, superseded name) | PASS | 4 caught | 0 | 0 | P23, P24, P26, P31 each failed on its mutant |
