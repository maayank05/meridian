# 11 — Business Analysis Documentation Package

Create and maintain these artifacts under `business/` and `docs/`.

## Required documents
1. Business case and problem statement.
2. Project objectives and scope.
3. Stakeholder register and stakeholder map.
4. BRD — business requirements.
5. FRD — functional requirements.
6. Non-functional requirements.
7. User stories and acceptance criteria.
8. Business rules catalogue.
9. KPI dictionary.
10. Data dictionary.
11. AS-IS / TO-BE process maps where meaningful.
12. Assumptions register.
13. RAID log (risks, assumptions, issues, dependencies).
14. Requirements traceability matrix.
15. Change log.
16. Decision log.
17. UAT scenarios and sign-off template.
18. Executive findings and recommendations report.

## User story format
As a [stakeholder], I want [capability], so that [business outcome].

Each story must have:
- ID and priority.
- Business value.
- Dependencies.
- Acceptance criteria in Given/When/Then form.
- Data required.
- API/UI implementation reference.
- Test ID.
- Status.

## KPI dictionary fields
- KPI ID and name.
- Business definition.
- Formula.
- Numerator/denominator.
- Grain.
- Source tables/fields.
- Filters/exclusions.
- Time basis.
- Currency/unit.
- Null handling.
- Owner/stakeholder.
- Refresh cadence.
- Limitations.
- SQL/Python/DAX implementation references.
- Reconciliation test.

## Process mapping
Use Mermaid diagrams in Markdown where useful. Keep AS-IS and TO-BE clearly distinguished. Do not invent a real company's existing process; Northstar is a simulated case.

## Recommendations
Every recommendation should include:
- Observed evidence.
- Interpretation.
- Alternative explanations.
- Proposed action.
- Estimated impact only where calculation is defensible.
- Cost/effort.
- Risk and uncertainty.
- Measurement plan.
- Owner (simulated role).
