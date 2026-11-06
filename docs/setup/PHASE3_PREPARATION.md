# Phase 3 Preparation: Timestamp Handling (D-017) and Local MySQL Setup (Q-5)

Status: **Approved for the project owner to execute, 2026-10-31.** The AI assistant does **not** execute any of the setup SQL or change the MySQL server. Phase 3 migrations and ingestion start only after the owner runs §B and the reported permissions are verified.

---

## Part A — D-017 (Accepted with conditions, 2026-10-31)

**Source timezone:** `America/Sao_Paulo`. Evidence: a São Paulo DST-gap hour with 0 of 604,730 events vs 31/11 on neighbouring days; a purchase-hour pattern consistent with local time; see [DECISIONS.md D-017](../DECISIONS.md).

| Rule | Requirement |
|---|---|
| T1 | Raw layer (`raw_*`) stores the source timestamp **text unchanged** |
| T2 | Staging stores `*_local` as `DATETIME` (as recorded). Business dates and reporting periods use `*_local` |
| T3 | Staging stores `*_utc` as `DATETIME`, converted with `zoneinfo("America/Sao_Paulo")` **only where the conversion is unambiguous**. Durations use `*_utc` |
| T4 | **Ambiguous** local times (the repeated hour at DST fall-back; 39 found in profiling): `*_utc` = **NULL**, flag `*_tz_status = 'ambiguous'`. No resolution rule is applied unless explicitly approved later |
| T5 | **Non-existent** local times (DST spring-forward gap): `*_utc` = NULL, flag `'nonexistent'` (0 found in profiling) |
| T6 | Date-only columns (`order_estimated_delivery_date`, `review_creation_date`) are stored as `DATE`; no conversion |
| T7 | No `TIMESTAMP` columns for source data; every pipeline session sets `time_zone = '+00:00'` |
| T8 | Duration KPIs skip rows whose required `*_utc` is NULL and report the count as an exclusion |
| T9 | **`tzdata`** (PyPI, Python Software Foundation): Windows has no system IANA database, so Python's `zoneinfo` needs it. It is pinned in the lockfile so Windows and Linux CI use identical rules |
| T10 | Tests (Phase 3): normal timestamps, spring-forward gap (2017-10-15 00:00–00:59 local), fall-back repeat (2018-02-17 23:00–23:59 local), boundary seconds either side of each transition, date-only columns, and NULL/flag behaviour |

---

## Part B — Local MySQL setup (Q-5): exact instructions

### B1. What will exist afterwards
| Object | Name | Host | Scope |
|---|---|---|---|
| Database | `meridian_dev` | — | utf8mb4 / utf8mb4_0900_ai_ci |
| Database | `meridian_test` | — | utf8mb4 / utf8mb4_0900_ai_ci |
| User | `meridian_owner` | `localhost` only | `meridian_dev.*` only |
| User | `meridian_reader` | `localhost` only | `meridian_dev.*` only, read-only |
| User | `meridian_test` | `localhost` only | `meridian_test.*` only |

| User | Privileges (database level, no global privileges) |
|---|---|
| meridian_owner | SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES, CREATE VIEW, SHOW VIEW, CREATE TEMPORARY TABLES, LOCK TABLES — on `meridian_dev.*` |
| meridian_reader | SELECT, SHOW VIEW — on `meridian_dev.*` |
| meridian_test | Same list as owner — on `meridian_test.*` |

- **No global privileges.** `SHOW GRANTS` will still print `GRANT USAGE ON *.* TO ...`. In MySQL, `USAGE` means "no privileges"; it is the placeholder every account has.
- **Not granted:** `GRANT OPTION`, `FILE`, `SUPER`, `PROCESS`, `RELOAD`, `CREATE USER`, `EXECUTE`, `TRIGGER`, `EVENT`, `CREATE ROUTINE`, any privilege on `mysql.*` or `*.*`.
- **Why localhost-only matters:** your `my.ini` has no `bind-address`, so the server may listen on all interfaces. `@'localhost'` accounts cannot log in from other machines.

### B2. Password-handling rules
- Passwords exist **only** in your local `.env`, which is gitignored (verified by the setup script before it runs).
- They are never typed on a command line (which would land in PowerShell history), never shown in the terminal, and never sent to the AI assistant.
- The setup script reads them from `.env` into memory and pipes the SQL into `mysql.exe`. MySQL error messages do not echo statement text.
- The root password is typed only at MySQL's own hidden prompt.

### B3. Steps

Run everything in **Windows PowerShell** from the repository root (the folder that contains `.git`, `.gitignore` and `docs/`). Use `cd <your MERIDIAN folder>` first.

**Step 1 — Pre-check the server** (prompts for the root password, hidden):
```powershell
$mysql = 'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe'
& $mysql -u root -p -h localhost --protocol=TCP -e "SELECT VERSION(), @@lower_case_table_names, @@sql_mode, @@local_infile, @@character_set_server, @@system_time_zone, @@time_zone; SELECT user, host FROM mysql.user WHERE user LIKE 'meridian%';"
```
Expected: version 8.0.38, `lower_case_table_names` = 1, strict mode present, and **no** `meridian%` rows yet (if rows exist, see Rollback first).

**Step 2 — Create `.env`** (gitignored). Open Notepad on a new `.env` in the repo root:
```powershell
notepad .env
```
Paste this template, then save:
```dotenv
# MERIDIAN local configuration. NEVER commit this file.
MERIDIAN_ENV=development
DB_HOST=localhost
DB_PORT=3306
DB_NAME=meridian_dev
DB_OWNER_USER=meridian_owner
DB_OWNER_PASSWORD=
DB_READER_USER=meridian_reader
DB_READER_PASSWORD=
TEST_DB_NAME=meridian_test
TEST_DB_USER=meridian_test
TEST_DB_PASSWORD=
DB_CONNECT_TIMEOUT_SECONDS=10
DB_POOL_SIZE=5
OLIST_RAW_DIR=data/raw/olist
SOURCE_TIMEZONE=America/Sao_Paulo
LOG_LEVEL=INFO
```

**Step 3 — Generate three passwords**, one per empty `*_PASSWORD=` line. Each run copies a new random 30–32 character letters-and-digits password to the clipboard without displaying it. Paste it after the `=` in Notepad (Ctrl+V), then run the command again for the next line. Save `.env`.
```powershell
$b = New-Object byte[] 24; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b); ([Convert]::ToBase64String($b) -replace '[+/=]','') | Set-Clipboard; Remove-Variable b
```
Afterwards clear the clipboard: `Set-Clipboard -Value $null`

**Step 4 — Run the setup script.** Paste the whole block into PowerShell. It refuses to run if `.env` is not gitignored, or if any password is missing, too short, non-alphanumeric or duplicated; error messages never include the value. Then it asks for the root password at MySQL's hidden prompt.
```powershell
& {
  $ErrorActionPreference = 'Stop'
  $mysql = 'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe'
  if (-not (Test-Path '.\.env')) { throw '.env not found: run this from the repository root' }
  & git check-ignore -q .env
  if ($LASTEXITCODE -ne 0) { throw '.env is NOT gitignored: stopping' }
  $cfg = @{}
  foreach ($line in Get-Content '.\.env') {
    if ($line -match '^\s*([A-Z_]+)\s*=\s*([^\s#]*)') { $cfg[$Matches[1]] = $Matches[2] }
  }
  $keys = 'DB_OWNER_PASSWORD', 'DB_READER_PASSWORD', 'TEST_DB_PASSWORD'
  foreach ($k in $keys) {
    if ($cfg[$k] -notmatch '^[A-Za-z0-9]{20,}$') { throw "$k is missing or invalid (needs 20+ letters/digits; value not shown)" }
  }
  if (@($keys | ForEach-Object { $cfg[$_] } | Select-Object -Unique).Count -ne 3) { throw 'The three passwords must all be different' }
  $sql = @"
CREATE DATABASE IF NOT EXISTS meridian_dev  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE DATABASE IF NOT EXISTS meridian_test CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER 'meridian_owner'@'localhost'  IDENTIFIED BY '$($cfg['DB_OWNER_PASSWORD'])';
CREATE USER 'meridian_reader'@'localhost' IDENTIFIED BY '$($cfg['DB_READER_PASSWORD'])';
CREATE USER 'meridian_test'@'localhost'   IDENTIFIED BY '$($cfg['TEST_DB_PASSWORD'])';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES, CREATE VIEW, SHOW VIEW, CREATE TEMPORARY TABLES, LOCK TABLES ON meridian_dev.*  TO 'meridian_owner'@'localhost';
GRANT SELECT, SHOW VIEW ON meridian_dev.* TO 'meridian_reader'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP, INDEX, REFERENCES, CREATE VIEW, SHOW VIEW, CREATE TEMPORARY TABLES, LOCK TABLES ON meridian_test.* TO 'meridian_test'@'localhost';
"@
  Write-Host 'Enter the MySQL ROOT password at the prompt (input hidden):'
  $sql | & $mysql -u root -p -h localhost --protocol=TCP --batch
  $code = $LASTEXITCODE
  Remove-Variable sql, cfg
  if ($code -ne 0) { throw "mysql exited with code $($code) - setup NOT complete (see Rollback before re-running)" }
  Write-Host 'Setup SQL completed. Now run Step 5.'
}
```
`CREATE USER` (without `IF NOT EXISTS`) is deliberate: if an account already exists, the script fails loudly rather than silently keeping an old password.

*Fallback if MySQL's password prompt does not appear when input is piped* (it should on Windows, but this pipe-plus-prompt combination has not been tested on your machine): stop and report it. An alternative that also avoids displaying passwords will be provided. Do not switch to typing passwords on the command line.

**Step 5 — Verify** (each command prompts for a password, hidden).

5a. As root: accounts, hosts and privileges (no passwords in output):
```powershell
$mysql = 'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe'
& $mysql -u root -p -h localhost --protocol=TCP -e "SELECT user, host FROM mysql.user WHERE user LIKE 'meridian%' ORDER BY user; SELECT GRANTEE, PRIVILEGE_TYPE FROM information_schema.USER_PRIVILEGES WHERE GRANTEE LIKE '%meridian%'; SELECT GRANTEE, TABLE_SCHEMA, COUNT(*) AS n_privs FROM information_schema.SCHEMA_PRIVILEGES WHERE GRANTEE LIKE '%meridian%' GROUP BY GRANTEE, TABLE_SCHEMA ORDER BY GRANTEE; SELECT SCHEMA_NAME, DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME LIKE 'meridian%';"
```
Expected:
- **3 users, all host `localhost`.**
- `USER_PRIVILEGES` shows **only `USAGE`** for each (no global privileges).
- Schema privileges: owner → `meridian_dev` (13), reader → `meridian_dev` (2), test → `meridian_test` (13).
- Both databases are utf8mb4 / utf8mb4_0900_ai_ci.

5b. Each account logs in over TCP, the way the Python driver will connect:
```powershell
& $mysql -u meridian_owner  -p -h localhost --protocol=TCP -e "SELECT CURRENT_USER(); SHOW GRANTS;"
& $mysql -u meridian_reader -p -h localhost --protocol=TCP -e "SELECT CURRENT_USER(); SHOW GRANTS;"
& $mysql -u meridian_test   -p -h localhost --protocol=TCP -e "SELECT CURRENT_USER(); SHOW GRANTS;"
```
If a login fails with `Access denied for user 'meridian_…'@'127.0.0.1'`, the server is not mapping loopback to `localhost`. Stop and report it; the fix (accounts on host `127.0.0.1`, still loopback-only) will be proposed for approval.

5c. Negative checks: **each must FAIL** with an access-denied error:
```powershell
& $mysql -u meridian_reader -p -h localhost --protocol=TCP meridian_dev  -e "CREATE TABLE should_fail (id INT);"   # expect ERROR 1142
& $mysql -u meridian_test   -p -h localhost --protocol=TCP meridian_dev  -e "SELECT 1;"                            # expect ERROR 1044
& $mysql -u meridian_owner  -p -h localhost --protocol=TCP meridian_test -e "SELECT 1;"                            # expect ERROR 1044
```

**Step 6 — Report back:** the output of 5a and 5b, and the three error codes from 5c. None of these contain passwords. Do **not** send `.env` or any password.

### B4. Rollback (destructive; undoes everything in Step 4)
Run as root only if you need to start over:
```powershell
$mysql = 'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe'
& $mysql -u root -p -h localhost --protocol=TCP -e "DROP USER IF EXISTS 'meridian_owner'@'localhost', 'meridian_reader'@'localhost', 'meridian_test'@'localhost'; DROP DATABASE IF EXISTS meridian_test; DROP DATABASE IF EXISTS meridian_dev;"
```
`meridian_dev` and `meridian_test` are empty until Phase 3, so nothing is lost now. After ingestion, dropping `meridian_dev` deletes loaded data (it can be rebuilt from the raw files).

### B5. Safeguards Phase 3 code will add (planned; tested in Phase 3)
- Tests abort unless the database name ends with `_test` **and** the user is `meridian_test`.
- Destructive rebuild requires an explicit flag and refuses `MERIDIAN_ENV=production`.
- Configuration errors name the missing variable, never its value; passwords are never logged.
- A committed `.env.example` contains the template above with empty passwords.

---

## Part C — Profiling scripts (approved for Phase 3)
To be added under `scripts/profiling/` during Phase 3 with synthetic-fixture tests, reading `data/raw/olist/` read-only and writing aggregates only to `docs/data/`. Reproduction instructions go in `scripts/profiling/README.md`. No raw rows, review text or personal data are committed.
