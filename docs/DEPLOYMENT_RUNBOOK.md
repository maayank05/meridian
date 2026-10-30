# Deployment Runbook

Last updated: 2026-10-31. **Status: skeleton.** Nothing is deployed. No URL, provider or cost in this file is real until filled in with verified evidence in Phase 12.

## 1. Local development environment (verified 2026-10-31 on the build machine)

| Tool | Found | Notes |
|---|---|---|
| Git | 2.55.0.windows.5 | Repo initialised locally, no remote |
| Python | 3.13.2 (`py -3.13`) | Use this. `python` on PATH is 3.11.4 **without pip** |
| Node / npm | v24.18.0 / 11.16.0 | pnpm/yarn not installed |
| MySQL Server | 8.0.38 Community, Windows service `MySQL80`, running, port 3306 | Client at `C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe` (not on PATH); MySQL Shell 8.0.38 on PATH |
| Power BI Desktop | 2.159.883.0 (Store app) | |
| Docker / WSL | Not installed | |
| gh / Render CLI / Kaggle CLI | Not installed | |

## 2. Local setup (to be completed in Phase 3 and verified from a clean clone in Phase 13)
1. Clone repository.
2. `py -3.13 -m venv .venv` then activate.
3. Install locked dependencies (command fixed in Phase 3).
4. Create `meridian_dev` and `meridian_test` databases and an app user (SQL provided in Phase 3); copy `.env.example` → `.env` and fill in locally.
5. Download Olist CSVs to `data/raw/olist/`.
6. Run migrations, ingestion, transformations (commands fixed in Phase 3).
7. Start API and frontend (commands fixed in Phases 8–9).

## 3. Production topology (target)
- Frontend: Render Static Site.
- API: Render Web Service (FastAPI + Uvicorn, binds `$PORT`).
- Database: external managed MySQL — provider **undecided** (D-011).

## 4. Sections to be completed in Phase 12
- Provider comparison with verified pricing and features.
- Environment variables (names only).
- Migration procedure.
- Backup configuration and **tested** restore procedure.
- Health/readiness checks.
- Persistence-across-redeploy test.
- Rollback procedure.
- Power BI connectivity notes.
- Expected monthly cost.
