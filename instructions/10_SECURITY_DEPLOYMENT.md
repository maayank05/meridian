# 10 — Security, Persistence and Render Deployment

## Secrets
- Use local `.env` excluded by `.gitignore`.
- Commit only `.env.example` with placeholder values.
- Store production secrets in Render/provider secret configuration.
- Rotate any credential accidentally committed.
- Never print environment values in logs or error messages.

## MySQL persistence
- Use a managed MySQL service with persistent storage.
- Do not use a container-local database or ephemeral disk as the system of record.
- Confirm provider region, Render region, private networking, TLS, backup retention, restore process, storage limits, connection limits and pricing.
- Use least-privilege application credentials.
- Keep admin credentials separate from application credentials.
- Enable automated backups and document restore steps.
- Test a restore before release.
- Use schema migrations and backup before destructive changes.

## Render topology
- React: Render Static Site or suitable web service.
- FastAPI: Render Web Service.
- MySQL: external managed MySQL provider selected after current compatibility and pricing verification.
- Configure `DATABASE_URL`/separate connection variables securely.
- Configure `PORT` according to Render's runtime contract.
- Add health checks and graceful startup/shutdown.
- Use allowed-origin CORS.
- Configure persistent uploads only if required; do not store authoritative dataset state in ephemeral service filesystem.

## Deployment checklist
- Local setup works from clean clone.
- Tests pass.
- Production build passes.
- Environment variables documented.
- Secrets absent from Git history.
- Database accessible securely.
- Migrations applied.
- Backup configured.
- Health endpoint returns expected result.
- Frontend calls correct API URL.
- CORS works only for approved origin.
- Logs are useful and non-sensitive.
- Database data survives service redeploy/restart.
- Restore procedure documented and tested.
- Power BI connectivity/refresh limitations documented.

## Cost caution
Check current Render and database-provider pricing before selecting paid services. Do not assume free tiers include persistent storage, backups, always-on services or reliable Power BI refresh. Document expected monthly cost and usage constraints.

## Security minimum
- Validate inputs.
- Parameterize SQL.
- Avoid SQL injection.
- Apply rate limiting where appropriate.
- Use authentication if the deployed app exposes non-public or administrative functions.
- Do not put admin/DB credentials in frontend variables.
- Restrict CORS.
- Minimize personal/customer identifiers in logs and screenshots.
- Keep dependencies patched.
