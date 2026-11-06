# Phase Checkpoint
Phase: 0 — Repository and environment audit
Date: 2026-10-31
Status: **PASS WITH DOCUMENTED LIMITATIONS**

## 1. Objective
Understand the full requirement pack, audit the repository and local environment, identify constraints and conflicts, and create the project control documents. No application code.

## 2. Work completed
- Read all 19 pack files in full.
- Inspected repository: contained only the instruction pack (19 files, ~56 KB); no code, no data; not a Git repository.
- Ran environment audit (below).
- Initialised a local Git repo (branch `main`, **no commits**, no remote).
- Created `.gitignore` and the 10 mandated `docs/` control files; appended owner rules and environment notes to the project rules file (now `CONTRIBUTING.md`).
- Ran a document-consistency check script (20 checks).

## 3. Environment audit (from executed commands)

| Item | Result |
|---|---|
| Git | 2.55.0.windows.5 |
| Python | 3.10, 3.11.4, 3.13.2 installed. **3.11 (first on PATH) has no pip.** 3.13.2 has pip 24.3.1, venv and OpenSSL 3.0.15 working |
| uv / poetry / pipx | Not installed |
| Node / npm | v24.18.0 / 11.16.0; pnpm, yarn not installed |
| MySQL Server | 8.0.38 Community, service `MySQL80` Running/Automatic, TCP 3306 open. `mysql.exe`, `mysqldump.exe` present in `C:\Program Files\MySQL\MySQL Server 8.0\bin` but not on PATH. MySQL Shell, Workbench, Router 8.0 installed |
| MySQL credentials | Not accessed. Connection **not tested** (needs credentials from user via `.env`) |
| Power BI Desktop | Installed, Store package 2.159.883.0 |
| Docker / WSL | Not installed |
| gh / Render CLI / Kaggle CLI | Not installed; no `~/.kaggle/kaggle.json` |
| Olist files | None found in Desktop/Downloads (searched for `olist_*.csv`, depth 3) |
| Package registries | PyPI reachable (fastapi 0.162.0 listed; `pymysql` and `mysqlclient` Windows wheels downloaded OK). npm reachable (react 19.3.1, vite 8.3.5, recharts 3.10.1 MIT) |
| Hardware | 7.7 GB RAM; ~109 GB free on C: |

## 4. Approved stack and contradictions resolved
Stack confirmed and locked (D-001): Python, MySQL, Pandas, SQL scripts, FastAPI, React, Matplotlib, Seaborn, SciPy, Statsmodels, Scikit-learn, Pytest, Ruff, Git/GitHub, GitHub Actions, Power BI, Render.

| # | Conflict / gap found | Resolution |
|---|---|---|
| 1 | `12` layout has both `backend/tests/` and top-level `tests/` | Single Python suite in `backend/tests/` (D-010) |
| 2 | Master prompt requires DEPLOYMENT_RUNBOOK/SECURITY/TEST_STRATEGY; `12` tree omits them | Placed in `docs/` (D-010) |
| 3 | SQLite allowed "for isolated tests" vs. MySQL must be tested | No SQLite at all; real MySQL locally and in CI (D-008) |
| 4 | Several required capabilities need libraries not on the stack list (pooling, ASGI server, React build/test/chart/E2E) | Listed in PROJECT_SPEC §2.1 as **Proposed, not installed**, awaiting your approval (Q-1) |
| 5 | `docker-compose.yml` suggested, Docker unavailable | Use native MySQL80 service; Linux parity via GitHub Actions (D-010) |
| 6 | Render has no native managed MySQL | Provider choice deferred to Phase 12 with live pricing verification (D-011) |
| 7 | "Genuine PBIX only if authoring/testing possible" | Desktop exists, but the GUI can't be automated → owner authors the PBIX from the spec; totals are reconciled against generated targets (D-012) |
| 8 | M03 marketing data does not exist in Olist | Your decision needed (D-015 / Q-3) |
| 9 | Raw `schemas` vs `prefixes` left open by `04` | One DB per environment + table prefixes (D-009) |

## 5. Files created/modified
Created: `.gitignore`, `docs/PROJECT_SPEC.md`, `docs/IMPLEMENTATION_PLAN.md`, `docs/PROJECT_STATUS.md`, `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/DECISIONS.md`, `docs/KNOWN_LIMITATIONS.md`, `docs/QUALITY_REPORT.md`, `docs/DEPLOYMENT_RUNBOOK.md`, `docs/SECURITY.md`, `docs/TEST_STRATEGY.md`, `docs/checkpoints/PHASE_00_CHECKPOINT.md`, `.git/` (init).
Modified: the project rules file, now `CONTRIBUTING.md` (appended sections only; original content unchanged).
Not modified: all other pack files.

## 6. Commands actually executed
- Tool probes: `git --version`, `py -0p`, `python -m pip --version` (3.11 → no pip), `py -3.13 -m pip --version`, `node/npm --version`, `mysqld.exe --version`, `Get-Service *mysql*`, TCP probe 127.0.0.1:3306, `Get-AppxPackage *PowerBI*`, Docker/WSL/kaggle/gh checks, `pip index versions fastapi`, `pip download pymysql mysqlclient` (to temp), `npm view react|vite|recharts`.
- `git init -b main`
- `py -3.13 -I phase0_check.py <repo_root>` (scratchpad script, two runs)

## 7. Test/lint/build results
| Check | Result |
|---|---|
| Phase 0 consistency script, run 1 | 18 passed, 2 failed (expected: two docs not yet written + one link to them) |
| Phase 0 consistency script, run 2 | 20 passed, 0 failed, 0 skipped |
| Ruff, Pytest, frontend lint/test/build | **Not run** — no code exists and tools are not installed yet. Not a pass. |

Checks covered: mandated docs present; all 35 FR/NFR IDs from `02` in traceability with none invented; M01–M10 acceptance rows; nothing marked Complete; every `D-xxx`/`Q-x` reference defined; relative doc links resolve; every approved stack item named in spec; banned tech mentioned only as prohibited; `.env`/raw data ignored while `.env.example`/fixtures are not (`git check-ignore`); no code/PBIX created; no credential-like strings.

## 8. Acceptance criteria evidence
| Criterion | Evidence |
|---|---|
| All instruction files read | §2; contradictions in §4 cite specific files |
| Repo and environment inspected without assumptions | §3 (each value from command output) |
| Data acquisition constraints identified | §3 (no files, no Kaggle creds); D-013; L-S05/L-S06 |
| Architecture and phase plan proposed | PROJECT_SPEC §3, IMPLEMENTATION_PLAN |
| Control documents only | C16 passed (no code files) |
| Checks run | §7 |

## 9. Defects and unresolved issues
- None in deliverables. The consistency script is a throwaway in the session scratchpad; it becomes a committed test in Phase 3 once Pytest is approved.

## 10. Known limitations
See [KNOWN_LIMITATIONS.md](../KNOWN_LIMITATIONS.md). Key ones: dataset not present; MySQL connectivity untested (no credentials); Olist licence unverified; no GitHub remote; production DB provider undecided.

## 11. Requirements traceability changes
Matrix created: 25 FR + 10 NFR + 10 module AC rows. In progress: FR-040, FR-041, FR-043, NFR-001, AC-M09 (documentation only). All others Not started. Nothing Complete.

## 12. Next phase recommendation
Phase 1 — Business analysis and specification (`business/` artefacts, KPI dictionary with every metric tied to an expected Olist field or marked unsupported/synthetic). Phase 1 needs no dataset or installs, so it can start right after approval. Download the dataset in parallel so Phase 2 isn't blocked.

## 13. User approval requested
Please approve or amend: Proposed decisions D-002 to D-010 and D-012 to D-014, and the supporting-library list (Q-1). Answer Q-3 (M03 scope). Optional now: Q-2 dataset download, Q-4 GitHub repo.

---
## Post-review addendum (2026-10-31)
The body above is a point-in-time record. Outcomes of the user's review:
- Phase 0 approved. D-002 to D-010 accepted, subject to dependency compatibility verification. D-012, D-013 and D-014 accepted. D-015 accepted as option A + B.
- Olist licence CC BY-NC-SA 4.0 verified by the project owner; the user placed the dataset in `data/raw/olist/`.
- GitHub remote: https://github.com/maayank05/meridian (public, MIT licence for project code/docs only).
- Current state lives in [PROJECT_STATUS.md](../PROJECT_STATUS.md) and [DECISIONS.md](../DECISIONS.md).
