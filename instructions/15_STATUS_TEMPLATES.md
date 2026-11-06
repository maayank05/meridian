# 15 — Project Status and Reporting Templates

These living documents are maintained in `docs/`.

## PROJECT_STATUS.md
```md
# Project Status
Last updated:
Current phase:
Overall status: NOT STARTED / IN PROGRESS / BLOCKED / RELEASED

## Completed
- [ ] ...

## In progress
- ...

## Blocked
- ...

## Latest verified checks
| Check | Command | Result | Evidence/date |
|---|---|---|---|

## Next actions
1. ...

## Latest checkpoint
Status: PASS / PASS WITH DOCUMENTED LIMITATIONS / BLOCKED
```

## QUALITY_REPORT.md
```md
# Quality Report
| Date | Layer | Command/check | Result | Passed | Failed | Skipped | Evidence |
|---|---|---|---|---:|---:|---:|---|
```

## REQUIREMENTS_TRACEABILITY.md
```md
| Requirement ID | Requirement | Business objective | Module | Files/API | Test ID | Evidence | Status |
|---|---|---|---|---|---|---|---|
```

## DECISIONS.md
For each decision:
- ID/date/status.
- Context.
- Options considered.
- Decision.
- Rationale.
- Trade-offs.
- Consequences.
- Revisit trigger.

## KNOWN_LIMITATIONS.md
Group limitations into:
- Source-data limitations.
- Metric limitations.
- Statistical/model limitations.
- Synthetic assumptions.
- Technical/deployment limitations.
- Power BI connectivity limitations.
- Deferred features.
- Known defects.

## Checkpoint report
```md
# Phase Checkpoint
Phase:
Status: PASS / PASS WITH DOCUMENTED LIMITATIONS / BLOCKED

## Objective
## Work completed
## Files created/modified
## Commands actually executed
## Test/lint/build results
## Acceptance criteria evidence
## Defects and unresolved issues
## Known limitations
## Requirements traceability changes
## Next phase recommendation
## User approval requested
```

Never fill these templates with invented dates, test results, deployment URLs or findings.
