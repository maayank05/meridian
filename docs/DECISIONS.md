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

## D-016 — Canonical revenue definition
- **Date / status:** 2026-10-31 / **Accepted — Option A** (project owner approval, with naming clarification)
- **Context:** Olist is a marketplace; its commission income is not in the data. Northstar revenue is simulated as the merchandise value of orders (A-04). Value basis, status scope and time basis must be fixed once and reused everywhere (SQL, Python, API, Power BI, report).
- **Options:** A: Σ item price, delivered orders, purchase-date basis. B: Σ item price, all except canceled/unavailable. C: Σ price + freight, delivered. D: Σ payment value. E: as A but delivery-date basis. Full consequences are in [08_kpi_dictionary.md Part A](../business/08_kpi_dictionary.md).
- **Decision:** Option A — Σ `order_items.price` for orders with status delivered, grouped by `order_purchase_timestamp`, BRL. Displayed canonical metric name: **"Delivered Merchandise Value (Revenue Proxy)"**.
- **Conditions (user-mandated):** freight kept separate (K02); never described as audited accounting revenue or profit; documentation states that refunds and full accounting adjustments are unavailable; right-censoring warning on recent periods; one definition applied consistently in SQL, Python, API and Power BI. Payment reconciliation stays visible as K18.
- **Trade-offs:** Conservative and drillable to category/seller, but understates the final months; excludes freight from "revenue".
- **Revisit trigger:** Phase 2 profiling shows status semantics differ from the documentation (e.g. no `delivered` value, or a large share of shipped-but-undelivered orders).
- **Phase 2 check (2026-10-31):** trigger not met. `delivered` exists (96,478 orders, 97.02% of orders); shipped-not-delivered = 1,107 orders.

## D-017 — Source timestamp handling
- **Date / status:** 2026-10-31 / **Accepted — Option C with conditions** (project owner approval)
- **Context:** Source timestamps carry no timezone (H-07). Evidence: on 2017-10-15 the São Paulo DST-gap hour (00:00–00:59 local) has 0 of 604,730 timestamps vs 31 and 11 in the same hour on neighbouring days; the purchase-hour pattern is consistent with local time; 39 timestamps fall in DST fall-back (repeated) hours. Server `my.ini` sets no default time zone.
- **Options considered:** A store as recorded only; B convert and store UTC only; C store both local and UTC. Details in [PHASE3_PREPARATION.md](setup/PHASE3_PREPARATION.md).
- **Decision:** Option C, source timezone `America/Sao_Paulo`:
  - raw source text preserved unchanged;
  - staging `*_local` DATETIME for business dates and reporting periods;
  - staging `*_utc` DATETIME only where conversion is unambiguous;
  - **ambiguous (fall-back) timestamps get `*_utc` = NULL and are flagged; no UTC value is invented** unless a resolution rule is explicitly approved later;
  - non-existent (gap) times get NULL and a flag;
  - date-only columns are stored as DATE;
  - no TIMESTAMP columns; pipeline sessions use `time_zone = '+00:00'`.
- **Dependency:** `tzdata` (PyPI) is required on Windows for Python `zoneinfo` (no system IANA database); pinned so Windows and Linux CI use identical rules.
- **Tests required (Phase 3):** normal timestamps, spring-forward gap, fall-back ambiguity, boundary seconds around each transition, date-only columns, NULL/flag behaviour.
- **Consequences:** duration KPIs exclude rows with NULL `*_utc` and report the count (39 timestamps in profiling).
- **Revisit trigger:** evidence that timestamps are customer-local rather than platform São Paulo time.
## D-018 — Default analysis window
- **Date / status:** 2026-10-31 / **Accepted — option (b)** (project owner approval)
- **Context:** Profiling (DQ-15): 2016-11 has 0 orders, 2016-09 has 4 and 2016-12 has 1; 2018-09/10 have 20 orders and 0 delivered (extract cutoff). Substantial monthly volume runs from 2017-01 to 2018-08 (20 months).
- **Options:** (a) Full range 2016-09 to 2018-10 with flags. (b) **Default window 2017-01-01 to 2018-08-31** for trends, comparisons and model training, with the full range still selectable and edge months flagged. (c) Like (b) but ending 2018-07 for extra censoring margin.
- **Decision:** (b). Default window **2017-01-01 to 2018-08-31** for trends, period comparisons and forecasting (training and evaluation). The complete source range stays accessible; periods outside the window are visibly flagged (RULE-25).
- **Rationale:** removes empty and near-empty months that would otherwise show as false collapses, while keeping all data accessible. Raw and staging layers keep everything; only defaults and model windows change.
- **Consequences:** customer history (first purchase, repeat status) is still computed from the full range, so 2016 buyers are not misclassified as new in 2017 (RULE-25).

## D-019 — KPI refinements from profiling
- **Date / status:** 2026-10-31 / **Accepted with conditions** (project owner approval)
- **Approved conditions:** (a) K12 counts `canceled` only; `unavailable` is reported separately as K26 (CR-004). (b) K13 = mean review score per order, then averaged over orders; the 789 shared review_ids (linking 1,412 orders) are documented as a source of non-independence. (c) K17 retained with a low-confidence label; impossible dates excluded under documented rules (RULE-27). (d) K20 excludes zero-instalment credit-card records and reports the excluded count (2 in the profiled data).
- **Original proposal (for the record):**
- **(a) K12 cancellation scope:** count only `canceled` (625); report `unavailable` (609) as a separate "Unavailable rate". *Alternative:* combine both as "not fulfilled".
- **(b) K13 review grain:** order-level. Each order's score = mean of its reviews (grain `(review_id, order_id)`), then average over orders. Shared review_ids (789) count once per order they belong to. *Alternative:* deduplicate by review_id (review-level), which loses the order link for 789 reviews.
- **(c) K17 seller handover:** keep but label **low confidence**; exclude rows with carrier date before approval/purchase or shipping limit > 60 days after purchase, and count exclusions. *Alternative:* drop K17.
- **(d) K20 instalments:** exclude the 2 credit-card records with 0 instalments as invalid, counted in the quality report.

## D-020 — Milestone A implementation choices
- **Date / status:** 2026-11-06 / Accepted as implementation detail within the approved stack (no new library). Listed here for owner review.
- **Lean plan:** the owner approved completing the project in four milestones (A: Phase 3; B: Phases 4–7; C: Phases 8, 9, 11; D: Phases 12–13), with Power BI delivered as spec + DAX and paid hosting deferred.
- **Database TLS:** connections use TLS with MySQL's self-signed certificate, **not verified** (local server). This lets PyMySQL use `caching_sha2_password` without adding the optional `cryptography` package. Production (Phase 12, if ever) must verify certificates.
- **Package layout:** one Python package `backend/meridian/` (config, db, migrations, ingestion; later api/analytics) instead of `backend/app/` + `backend/ingestion/`. Simpler imports; D-010 layering is kept as subpackages.
- **Locking (D-003 met):** `requirements/*.in` → hashed `requirements/*.txt` via pip-tools; installs use `--require-hashes`.
- **Pipeline shape:** full refresh in **one transaction** (DELETE, not TRUNCATE) so any failure rolls back to the previous state; the audit run row is written in a separate transaction so failures are recorded.
- **Revisit trigger:** remote/managed MySQL, or certificate verification needed.

## D-021 — Milestone B analytics choices
- **Date / status:** 2026-11-06 / Accepted as implementation detail within the approved stack (Statsmodels added to the lock; part of D-001). Listed for owner review.
- **Canonical KPIs = SQL views** (`backend/sql/migrations/0004_kpi_views.sql`). API, report and Power BI read these views. Ratios over a period are recomputed from summed numerators/denominators, never averaged across months.
- **Independent check:** `backend/meridian/analytics/kpis.py` recomputes the same KPIs from the raw CSV files with pandas/Decimal. `scripts/reconcile_kpis.py` compares both on the full dataset.
- **Forecast (K25):** rolling-origin one-step evaluation (6 test months) of naive, seasonal naive and damped Holt on the D-018 window. The model is used only if it beats the best baseline. Result 2026-11-06: **not justified**; the naive baseline is used ([FORECAST_REPORT](analytics/FORECAST_REPORT.md)). No scikit-learn model: nothing more complex is defensible on 20 months.
- **Simulator:** ROI is computed on an explicitly **synthetic contribution margin** applied to incremental revenue proxy, never on revenue (RULE-18/20). Zero cost → ROI undefined.
- **M03 campaign scenario:** uses explicit user-entered assumptions (spend, attribution share, incremental lift, margin) instead of a seeded random spend generator. Deterministic inputs are simpler and equally clearly labelled; recorded as CR-005.
- **Deferred:** K09 RFM (frequency is 1 for about 97% of people, R-08, so quintile RFM adds little) and K17 seller handover (low confidence). Both are documented as not implemented.
