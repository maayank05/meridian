# 13 — UAT Plan and Sign-off Template

Status: **Template only** (Phase 1). Scenarios are written and executed in Phase 11 against the working application. No results are recorded here until they are actually executed.

## 1. Purpose
Confirm with the (simulated) business stakeholders, represented by the project owner, that MERIDIAN meets the acceptance criteria in [06_user_stories.md](06_user_stories.md).

## 2. Entry criteria
- Phase 8 (API) and Phase 9 (React) gates passed.
- Full Olist dataset ingested in the UAT environment; latest quality report available.
- Known limitations documented.

## 3. Exit criteria
- All Must stories passed, or failed with an approved deviation.
- No open Severity-1 defects.
- Sign-off recorded below.

## 4. Scenario template

| UAT ID | Story | Scenario (Given / When / Then) | Test data | Expected result | Actual result | Pass/Fail | Defect ID | Tester | Date |
|---|---|---|---|---|---|---|---|---|---|
| UAT-001 | US-xxx | … | … | … | *(filled on execution)* | | | | |

## 5. Defect severity
| Severity | Definition |
|---|---|
| 1 | Wrong number, mislabelled provenance, data loss, or security exposure |
| 2 | Feature unusable, but no wrong numbers shown |
| 3 | Usability or cosmetic issue |

## 6. Sign-off

| Role | Name | Decision (Accept / Accept with conditions / Reject) | Conditions | Date |
|---|---|---|---|---|
| Project owner (SH-09) | | | | |
