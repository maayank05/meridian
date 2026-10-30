# 02 — Requirements and Acceptance

Assign unique IDs to every requirement. Maintain a traceability matrix with requirement, business objective, implementation location, test ID, evidence and status.

## Functional requirements

### Platform and access
- FR-001: Provide a responsive React application with clear navigation.
- FR-002: Provide FastAPI REST endpoints for health, metadata, filters and analytical results.
- FR-003: Provide consistent loading, empty, validation and error states.
- FR-004: Support documented date and dimension filters.
- FR-005: Display data freshness, source, metric definition and whether values are observed, derived, simulated or forecast.

### Data foundation
- FR-010: Ingest locally supplied Olist files through a repeatable Python process.
- FR-011: Validate required files, columns, types, candidate keys and relationships.
- FR-012: Preserve raw source data and record ingestion metadata.
- FR-013: Transform source data through ordered SQL scripts into analytical tables.
- FR-014: Make rebuild/reload behaviour explicit and safe.
- FR-015: Produce ingestion and data-quality reports.

### Analytics
- FR-020: Provide executive commercial KPIs.
- FR-021: Provide customer purchase, cohort and segmentation analysis.
- FR-022: Provide product/category performance analysis.
- FR-023: Provide seller and fulfilment analysis.
- FR-024: Provide financial reconciliation and scenario estimates without unsupported profit claims.
- FR-025: Provide data quality monitoring and downstream impact explanations.
- FR-026: Provide scenario comparison with documented assumptions.
- FR-027: Provide statistical analysis and forecasts only when justified.
- FR-028: Generate a reproducible executive report.
- FR-029: Provide Power BI model and DAX documentation with reconciliation tests.

### Governance and learning
- FR-040: Provide BRD, FRD, user stories, acceptance criteria, process flows, KPI/data dictionaries, RAID and traceability.
- FR-041: Provide architecture, data lineage, decisions and limitations.
- FR-042: Provide learning materials that explain core implementation concepts.
- FR-043: Provide reproducible setup, test, pipeline and deployment instructions.

## Non-functional requirements
- NFR-001 Security: secrets in environment variables/secret manager; no credentials in Git.
- NFR-002 Reliability: clear failure modes, transaction boundaries and retry behaviour where appropriate.
- NFR-003 Performance: paginate large responses; aggregate in MySQL; avoid loading full tables into API memory.
- NFR-004 Maintainability: layered backend, reusable analytics services, readable SQL and modular React.
- NFR-005 Testability: unit, integration, API, SQL, frontend and end-to-end smoke tests.
- NFR-006 Accessibility: semantic markup, keyboard navigation, readable contrast and labels.
- NFR-007 Observability: structured logs without secrets or unnecessary customer data.
- NFR-008 Reproducibility: pinned dependencies and deterministic test fixtures.
- NFR-009 Portability: documented local setup and Render deployment.
- NFR-010 Data integrity: MySQL constraints, referential integrity and reconciliation.

## Acceptance criteria standard
Every feature must define:
- Given / When / Then behaviour or equivalent testable conditions.
- Expected input and output.
- Valid, invalid, missing and boundary cases.
- Test IDs and evidence.
- Known limitations.

Do not mark requirements complete based on UI presence alone.
