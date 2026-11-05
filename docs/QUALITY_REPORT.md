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
| 2026-10-31 | Data (header only) | Read first line of 9 Olist CSVs (`py -3.13 -I`, no data rows) | PASS | 9 files / 52 cols [corrected 2026-10-31; originally recorded as 57 in error] | 0 | 0 | [SOURCE_HEADERS.md](data/SOURCE_HEADERS.md); BOM in 1 file, CRLF in 2, misspelled columns noted |
| 2026-10-31 | Docs | Phase 1 consistency script, run 1 | ABORTED | 35 | 1 | 0 | Checker crashed printing `→` on cp1252 console (checker bug) after P16; P12 failed for 8 stories |
| 2026-10-31 | Docs | Phase 1 consistency script, run 2 (after fixing 2 stories, checker encoding, story regex) | FAIL | 43 | 1 | 0 | P20 false positive ("nobody mistakes revenue for profit") |
| 2026-10-31 | Checker self-test | Mutation test 1: 8 violations injected into a scratch copy | PARTIAL | 8 caught | 1 missed | 0 | P20 missed a positive "profit trend" claim (line-level negation too loose) |
| 2026-10-31 | Checker self-test | P20 rule unit cases (positive/negative lines) | PASS | 6 | 0 | 0 | Windowed negation rule |
| 2026-10-31 | Checker self-test | Mutation test 2 (P20) | FAIL then PASS | — | — | — | First re-run still missed: the regex `\b` had been written as literal backspace bytes (0x08) by a heredoc. Fixed via chr() and the mutant was then caught. Control-char scan of all docs and staged blobs: none |
| 2026-10-31 | Docs | Phase 1 consistency script, final run (after all doc updates and checkpoint) | PASS | 44 | 0 | 0 | [PHASE_01_CHECKPOINT.md](checkpoints/PHASE_01_CHECKPOINT.md) |
| 2026-10-31 | Git | Pre-commit verification: staged == approved 31 (diff vs list), Phase 1 unstaged, no data/secrets/emails/local paths, LICENSE == HEAD, noreply identity | PASS | 9 checks | 0 | 0 | Commit `7270770` pushed: `286588c..7270770 main -> main`; local == origin/main; remote tree 32 files (31 + LICENSE) |
| 2026-10-31 | Docs | D-016 applied (Option A, "Delivered Merchandise Value (Revenue Proxy)"); checker extended with P23–P31 closure checks; run on real repo | PASS | 51 | 0 | 0 | Phase 1 closure verification |
| 2026-10-31 | Checker self-test | Mutation test 3: 4 violations injected (refund wording removed, KPI renumbered, finding sentence, superseded name) | PASS | 4 caught | 0 | 0 | P23, P24, P26, P31 each failed on its mutant |
| 2026-10-31 | Git | Phase 1 pre-commit verification (staged == approved 22, no data/secrets/personal paths, LICENSE == HEAD) | PASS | 22 files | 0 | 0 | Commit `8517a64` pushed: `7270770..8517a64 main -> main`; local == origin/main; working tree clean |
| 2026-10-31 | Data integrity | SHA-256 of 9 raw CSVs before profiling and at the Phase 2 gate | PASS | 9 | 0 | 0 | Identical (raw files never modified) |
| 2026-10-31 | Environment | Scratch venv: Python 3.13.2 + pandas 3.1.0 + numpy 2.5.4 (`pip install pandas`) | PASS | — | — | — | Installed and ran; early D-002/D-003 compatibility evidence (not the locked project env) |
| 2026-10-31 | Data profiling | `profile_olist.py` (pandas, all columns as text) over 9 files / 1,550,922 rows | Completed | — | — | — | [profile_results.json](data/profile_results.json), 35 s runtime |
| 2026-10-31 | Data profiling | Independent stdlib re-computation (`csv` + `Decimal`, no pandas) of 33 key figures | PASS | 33 matched | 0 | 0 | Row counts, keys, orphans, distributions, Decimal reconciliation, fan-out, monthly coverage |
| 2026-10-31 | Docs | Generated-report review (human read-through) | 3 fixes | — | — | — | Removed unverified "lowercase, unaccented" claim; zip ranges shown as text lengths; line-break sentence corrected; description-provenance note added |
| 2026-10-31 | Docs | Phase 2 gate checks, run 1 | FAIL | 17 | 1 | 0 | Q04 exposed a Phase 1 error: source has **52** columns, not 57 (hand-addition). Corrected with notes in SOURCE_HEADERS, Phase 1 checkpoint, this report, traceability |
| 2026-10-31 | Docs | Phase 2 gate checks, run 2 | PASS | 18 | 0 | 0 | Includes Q10: K01/K02/K04 computed in memory and proven absent from all documents |
| 2026-10-31 | Docs | Phase 1 regression checks after Phase 2 edits | PASS | 51 | 0 | 0 | |
| 2026-10-31 | Checker self-test | Phase 2 mutation tests (KPI-value leak, dictionary column, record ID, stale placeholder, self-approved decision) | PASS | 5 caught | 0 | 0 | The first Q13 attempt did not apply its mutation (test-setup error); re-run with an asserted mutation was caught |
| 2026-10-31 | Data (read-only) | Orders linked to shared review_ids (stdlib, aggregate) | Completed | — | — | — | 789 shared review_ids → 1,412 distinct orders (764 shared by 2 orders, 25 by 3) |
| 2026-10-31 | Docs | D-018/D-019 applied; checkers updated (K01–K26; Q13 expects approval; new Q19 for approval conditions) | PASS | 19 (Phase 2) + 51 (Phase 1) | 0 | 0 | Q19 mutation (removed 1,412 figure) caught |
| 2026-10-31 | Checker fix | C17 credential regex crossed line breaks (false positive on an empty `DB_OWNER_PASSWORD=`); limited to same-line matching | PASS | 7 unit cases | 0 | 0 | A literal-tab artefact from shell quoting was also removed from the checker |
| 2026-10-31 | Git | Phase 2 pre-commit verification: staged == 20; 0 of 31,839 distinct review texts present; no record IDs, secrets, personal paths or data; LICENSE == HEAD | PASS | 8 checks | 0 | 0 | Commit `b0ba8a9` pushed: `8517a64..b0ba8a9 main -> main`; local == origin/main |
| 2026-10-31 | Setup script | PHASE3_PREPARATION Step 4 PowerShell block, extracted verbatim and run in PowerShell 5.1 with a stub mysql.exe and fake .env values (no MySQL server touched) | PASS | 13 | 0 | 0 | Happy path, missing/duplicate/invalid passwords, .env not ignored, mysql failure; no password printed in any case |
| 2026-10-31 | Setup script | Harness self-test: original `$code:` parse bug reinstated in a copy | Detected | 5 | 8 | 0 | Bug was found by review and fixed before testing; harness confirms it would have failed |
| 2026-11-06 | Environment | `.venv` (Python 3.13.2); `pip install --require-hashes -r requirements/requirements.txt -r requirements/requirements-dev.txt`; `pip check` | PASS | — | — | — | D-002/D-003 compatibility verified (pandas 3.1.1, SQLAlchemy 2.1.8) |
| 2026-11-06 | Database | Account verification via app engines: CURRENT_USER, TLS, session tz, SHOW GRANTS | PASS | 3 accounts | 0 | 0 | All @localhost; global USAGE only; 13 / 2 / 13 privileges as approved; TLS on; tz +00:00 |
| 2026-11-06 | Python lint | `ruff check .` and `ruff format --check .` | PASS | — | 0 | — | First run: import order, line length, 2 script issues; fixed |
| 2026-11-06 | Python unit | `pytest backend/tests/unit` | PASS | 26 | 0 | 0 | Timezone DST cases, header validation, SQL parsing, safety guards |
| 2026-11-06 | MySQL integration | `pytest backend/tests/integration` (meridian_test) | PASS | 13 | 0 | 0 | One run failed on a wrong exception import (PyMySQL vs SQLAlchemy DataError); fixed and tightened |
| 2026-11-06 | Profiling scripts | `pytest scripts/profiling/tests` | PASS | 3 | 0 | 0 | First run found a real bug in followups.py (empty selection); fixed |
| 2026-11-06 | Full data load | `python -m meridian.ingestion` into meridian_dev | PASS | run 1 | — | — | 1,550,922 rows in 271.5 s; 39 ambiguous timestamps (38 distinct); 0 non-existent |
| 2026-11-06 | Reconciliation | `python scripts/verify_dev_load.py` | PASS | 28 | 0 | 0 | Row counts, SHA-256, Decimal sums CSV vs marts, no fan-out, profile cross-checks |
| 2026-11-06 | Reproducibility | Re-ran the 4 profiling scripts and diffed the generated docs | PASS | 5 files identical | 0 | — | Byte-identical to committed Phase 2 reports, before and after the followups.py fix |
| 2026-11-06 | Data integrity | Raw CSV SHA-256 vs Phase 2 hashes | PASS | 9 | 0 | 0 | Raw files unchanged |
| 2026-11-06 | Git hygiene | Pre-commit content check: 64 staged files; secrets, .env, personal paths/emails; fixture CSVs regenerated from the generator and compared with staged bytes; 32-hex IDs vs all real Olist IDs; 31,839 real review texts vs staged content | PASS | 64 files | 0 | 0 | First pass found autocrlf converting the CRLF/BOM fixtures; fixed with `.gitattributes` (`-text`). 26 synthetic IDs, 0 overlap with real IDs; 0 review texts; LICENSE untouched |
