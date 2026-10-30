# 12 — Process Maps (AS-IS and TO-BE)

Status: Draft v0.1 (Phase 1) · Last updated: 2026-10-31

> **AS-IS is illustrative.** Northstar is simulated. The AS-IS map describes a *plausible* fragmented reporting process used to motivate the design (A-11). It is not a description of Olist or any real company. The TO-BE map describes MERIDIAN as designed. Components in it are **planned, not built**.

## P-01 AS-IS — Monthly performance reporting (illustrative)

```mermaid
flowchart LR
    A[Teams export CSVs<br/>from separate systems] --> B[Analysts clean data<br/>in personal spreadsheets]
    B --> C{Revenue definition?}
    C -->|Team A: incl. freight| D1[Sales deck]
    C -->|Team B: payments| D2[Finance pack]
    C -->|Team C: items only| D3[Category report]
    D1 & D2 & D3 --> E[Leadership meeting:<br/>numbers disagree]
    E --> F[Ad-hoc reconciliation<br/>after the fact]
    F -.->|issues found late| A
```

Pain points (illustrative): inconsistent definitions, no quality checks before distribution, no lineage, decisions debated without consistent scenario economics.

## P-02 TO-BE — MERIDIAN data and decision flow (planned)

```mermaid
flowchart LR
    S[Olist CSVs<br/>source_observed] --> I[Python ingestion<br/>+ validation]
    I -->|fail fast| Q[(audit_* runs<br/>& quality results)]
    I --> R[(raw_*)]
    R --> T[Ordered SQL scripts]
    T --> ST[(stg_*)] --> M[(dim_* / fact_*<br/>derived)]
    SY[Seeded generators<br/>synthetic_assumption] --> SC[(scenario_*)]
    M --> SV[Python analytics services<br/>canonical KPIs]
    SC --> SV
    SV --> API[FastAPI /api/v1]
    API --> UI[React app<br/>provenance badges]
    API --> REP[HTML executive report]
    M --> PBI[Power BI<br/>reconciled measures]
    Q --> SV
```

## P-03 TO-BE — Decision scenario evaluation (planned)

```mermaid
flowchart TD
    U[Stakeholder defines intervention<br/>cost, response, horizon] --> V{Inputs valid?}
    V -->|No| E[Validation error<br/>explained]
    V -->|Yes| B[Load observed baseline<br/>K01, K03]
    B --> C[Compute base / upside / downside<br/>RULE-20]
    C --> D{Cost = 0?}
    D -->|Yes| N[ROI undefined;<br/>net benefit shown]
    D -->|No| R[ROI, net benefit,<br/>payback if defined]
    N & R --> L[Label: Scenario output<br/>+ assumptions list]
    L --> O[Decision discussion;<br/>measurement plan]
```

## P-04 TO-BE — Data-quality incident handling (planned)

```mermaid
flowchart LR
    RUN[Ingestion run] --> CHK[Quality checks]
    CHK -->|all pass| PUB[Publish freshness timestamp]
    CHK -->|failure| SEV{Blocking?}
    SEV -->|yes: missing file/column| STOP[Abort run; no partial writes]
    SEV -->|no: orphans, nulls| WARN[Record + map to affected KPIs]
    WARN --> PUB
    WARN --> UIW[UI/report quality warnings]
```
