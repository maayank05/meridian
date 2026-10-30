# Decision Log

Statuses: **Accepted** (mandated by the pack or approved by the user), **Proposed** (awaiting user approval — not acted on), **Open** (needs more information), **Superseded**.

## Approval record — 2026-10-31 (Phase 0 review)
The user approved:
- **D-002 to D-010 → Accepted**, *subject to dependency compatibility verification*. That means each library version must install and pass an import/smoke check on Python 3.13 (local Windows) and in CI (Linux) before it is locked. A failure gets a new decision entry, and nothing is silently swapped.
- The proposed Python / React / MySQL / FastAPI / testing architecture (PROJECT_SPEC §2.1, §3), which covers the supporting libraries that D-004 to D-006 name, including Recharts (D-005).
- **D-015 → Accepted: option A + B** (synthetic campaign scenario model plus methodology/limitations documentation).
- Dataset: the user downloads manually into `data/raw/olist/`. Claude must not use or request Kaggle credentials (reinforces D-013).
- GitHub repository: **public**, https://github.com/maayank05/meridian. The remote already holds an MIT `LICENSE` that must be preserved.

Second approval (2026-10-31): **D-012, D-013, D-014 → Accepted.** D-013 updated with user-confirmed licence wording.

Still open: D-011 (Phase 12).

---

## D-001 — Approved technology stack is locked
- **Date / status:** 2026-10-31 / Accepted (mandated by pack)
- **Context:** Pack specifies the stack exactly; user reiterated "never silently change the approved technology stack".
- **Decision:** Python, MySQL, Pandas, SQL scripts, FastAPI, React, Matplotlib, Seaborn, SciPy, Statsmodels, Scikit-learn, Pytest, Ruff, Git/GitHub, GitHub Actions, Power BI, Render.
- **Consequences:** Any substitution requires a new decision entry with evidence, alternatives and explicit user approval before implementation.
- **Revisit trigger:** A genuine technical blocker proven by executed evidence.

## D-002 — Python 3.13 as the runtime
- **Date / status:** 2026-10-31 / Accepted (user approval, subject to dependency compatibility verification)
- **Context:** Machine has Python 3.10, 3.11 and 3.13. Python 3.11 at `C:\Python311` has **no pip module** (verified: `No module named pip`) and is first on PATH. Python 3.13.2 has pip 24.3.1 and working `venv`/`ssl`.
- **Options:** (a) 3.13 via `py -3.13`; (b) repair 3.11; (c) 3.12 install.
- **Decision (proposed):** Create the project venv with `py -3.13 -m venv .venv`; pin the same minor version on Render.
- **Trade-offs:** Must confirm wheels for all scientific packages on 3.13 at install time (Phase 3); fall back to 3.12 with a new decision if any fails.
- **Revisit trigger:** A required package lacks 3.13 support, or Render cannot run 3.13.

## D-003 — Python dependency management: pip-tools lockfiles
- **Date / status:** 2026-10-31 / Accepted (user approval, subject to dependency compatibility verification)
- **Context:** Master prompt requires a sensible dependency manager with locked dependencies. `uv`, `poetry`, `pipx` are not installed.
- **Options:** (a) pip-tools (`requirements.in` → hashed `requirements.txt`), installed inside the venv; (b) uv (fast, single lockfile, needs global install); (c) poetry.
- **Decision (proposed):** pip-tools. Separate `requirements.txt` (runtime) and `requirements-dev.txt` (test/lint).
- **Rationale:** Nothing to install globally; Render's native Python build runs `pip install -r requirements.txt` without extra configuration; output is plain and reviewable.
- **Trade-offs:** Slower resolution than uv; lockfiles are platform-sensitive for a few packages (verify on Linux in CI).

## D-004 — Frontend tooling: Vite + React + TypeScript + npm
- **Date / status:** 2026-10-31 / Accepted (user approval, subject to dependency compatibility verification)
- **Context:** Node v24.18.0 and npm 11.16.0 present; pnpm/yarn absent. npm registry reachable (checked: react 19.3.1, vite 8.3.5 published).
- **Decision (proposed):** Vite React-TS template, React Router, Vitest + React Testing Library, ESLint. Exact versions pinned via `package-lock.json` at Phase 9 after compatibility check.
- **Rationale:** npm already installed; Vite is the maintained mainstream React build tool; TypeScript recommended by `03`/`07`.

## D-005 — React chart library: Recharts
- **Date / status:** 2026-10-31 / Accepted (user approval, subject to dependency compatibility verification)
- **Context:** `07` forbids rendering Matplotlib as the browser chart solution and requires a documented, licence-checked React chart library.
- **Options:** Recharts (MIT, checked `npm view recharts license` → MIT, v3.10.1), Apache ECharts, Chart.js + react-chartjs-2, Nivo.
- **Decision (proposed):** Recharts — declarative React components, MIT, adequate for line/bar/area/heatmap-like charts. Re-verify React 19 compatibility at Phase 9.

## D-006 — Database access: SQLAlchemy Core + PyMySQL, no ORM
- **Date / status:** 2026-10-31 / Accepted (user approval, subject to dependency compatibility verification)
- **Context:** `06` requires a maintained MySQL driver, connection pool, timeouts, transactions and parameterized SQL. SQL scripts are the transformation layer, so an ORM would duplicate schema definitions.
- **Options:** (a) SQLAlchemy Core + PyMySQL; (b) raw PyMySQL + hand-written pool; (c) mysqlclient (C extension, Windows build friction); (d) SQLAlchemy ORM.
- **Decision (proposed):** (a). Plain SQL via `text()` with bound parameters; pooling/timeouts from the engine. Also requires Uvicorn, pydantic-settings, httpx (test), pytest-cov.
- **Trade-offs:** One extra dependency vs. re-implementing pooling.

## D-007 — Migrations: ordered SQL scripts + schema_version table
- **Date / status:** 2026-10-31 / Accepted (user approval, subject to dependency compatibility verification)
- **Decision (proposed):** `backend/sql/migrations/NNNN_description.sql`, applied in order by a small Python runner that records checksum and timestamp in `schema_version`. No Alembic.
- **Rationale:** Keeps SQL scripts as the single source of schema truth (approved stack item "SQL scripts"). Checksums detect edited, already-applied migrations.

## D-008 — Test database: real MySQL, no SQLite
- **Date / status:** 2026-10-31 / Accepted (user approval, subject to dependency compatibility verification)
- **Context:** Pack permits SQLite for isolated tests only. Local MySQL 8.0.38 server is installed and running (service `MySQL80`, port 3306 open). GitHub Actions Ubuntu runners support a `mysql:8.0` service container.
- **Decision (proposed):** Pure-Python logic tested without a DB; all SQL/repository tests run against MySQL (`meridian_test` locally, service container in CI). No SQLite anywhere.
- **Rationale:** Avoids dialect drift (window functions, DECIMAL, date functions) between test and production.

## D-009 — One database per environment, layers by table prefix
- **Date / status:** 2026-10-31 / Accepted (user approval, subject to dependency compatibility verification)
- **Options:** (a) separate MySQL schemas `meridian_raw`, `meridian_stg`, `meridian_mart`; (b) one database with `raw_`/`stg_`/`dim_`/`fact_`/`audit_`/`scenario_` prefixes.
- **Decision (proposed):** (b).
- **Rationale:** Many managed MySQL plans provide a single database/user; cross-schema grants complicate least-privilege; prefixes satisfy `04`. A read-only reporting user can be granted SELECT on mart/audit tables only.

## D-010 — Repository layout deviations from `instructions/12`
- **Date / status:** 2026-10-31 / Accepted (user approval, subject to dependency compatibility verification)
- **Deviations:** (1) Python tests only in `backend/tests/` — the template lists both `backend/tests/` and a top-level `tests/`, which would split the suite. (2) Add `docs/DEPLOYMENT_RUNBOOK.md`, `SECURITY.md`, `TEST_STRATEGY.md` (required by master prompt, missing from tree). (3) `docker-compose.yml` omitted — Docker is not installed and local MySQL already runs natively. (4) `data/raw/olist/` added (gitignored) for local source files.

## D-011 — Hosted MySQL provider for production
- **Date / status:** 2026-10-31 / Open — decide in Phase 12
- **Context:** `03`/`10` state Render has no native managed MySQL and require comparing current providers on persistence, backups, region, TLS, networking, Power BI reachability and cost.
- **Candidates to evaluate (prices/features to be verified live at Phase 12, not assumed):** Aiven for MySQL, DigitalOcean Managed MySQL, AWS RDS for MySQL, Railway MySQL; MySQL-compatible engines (TiDB, PlanetScale/Vitess) would need separate approval because they are not MySQL.
- **Dependency:** User budget (Q-6).

## D-012 — Power BI authoring
- **Date / status:** 2026-10-31 / Accepted (user approval)
- **Context:** Power BI Desktop is installed (`Microsoft.MicrosoftPowerBIDesktop` 2.159.883.0). Claude cannot operate its GUI or verify a PBIX visually.
- **Decision (proposed):** Claude delivers model spec, DAX measures, page spec, connection steps and an automated reconciliation script (MySQL/API side). The user authors the PBIX in Desktop against local MySQL and captures screenshots; Claude then reconciles the reported totals. No PBIX is created by Claude (no fake/empty PBIX).
- **Risk:** Power BI Desktop's MySQL connector may require the MySQL Connector/NET driver — verify at Phase 10. Power BI Service refresh from a cloud MySQL generally needs a gateway or public endpoint — document, never expose production DB publicly.

## D-013 — Dataset acquisition and redistribution
- **Date / status:** 2026-10-31 / Accepted (user approval)
- **Context:** No Kaggle credentials (`~/.kaggle/kaggle.json` absent); no Olist CSVs found on Desktop/Downloads. **Licence: CC BY-NC-SA 4.0 — verified by the project owner on 2026-10-31** (attribution required; non-commercial use only; adaptations shared under the same licence). The user has since placed all 9 CSVs in `data/raw/olist/` manually.
- **Decision:** Manual download by the user to `data/raw/olist/`. Claude never uses or requests Kaggle credentials. The folder is gitignored and raw data is never committed. Tests/CI use hand-built synthetic fixtures labelled as such. Attribution and licence recorded in README and data docs.
- **Public-repo consequence (2026-10-31):** The repository is public with an MIT `LICENSE`. **The MIT licence applies only to MERIDIAN's original code and documentation, not to the Olist dataset**, which stays under CC BY-NC-SA 4.0. The README must say so and give the Olist attribution. A pre-commit staging check must confirm that no `olist_*.csv` / `product_category_name_translation.csv` file is ever staged.

## D-014 — End-to-end testing: Playwright
- **Date / status:** 2026-10-31 / Accepted (user approval; version compatibility verified at Phase 9)
- **Rationale:** `09` requires E2E smoke tests; Playwright runs headless in GitHub Actions and on Windows.

## D-015 — M03 Marketing scope
- **Date / status:** 2026-10-31 / Accepted — option A + B
- **Context:** Olist contains no marketing spend, campaign, attribution or experiment data. CAC, ROAS and lift are not observable.
- **Options:** (a) Synthetic campaign scenario model in `scenario_*` tables, labelled synthetic, with methodology for attributed vs incremental outcomes; (b) M03 reduced to a methodology page stating what is unsupported and what data would be required.
- **Decision:** Both. Build (a) with a documented generator seed, distributions and rationale, kept in `scenario_*` tables and labelled `synthetic_assumption`/`scenario_output` everywhere it appears. Also deliver (b) as methodology and limitations documentation explaining that CAC, ROAS and lift are not observable in Olist and what real data would be required.
- **Consequences:** No M03 output may be presented as Northstar's or Olist's actual marketing performance.
