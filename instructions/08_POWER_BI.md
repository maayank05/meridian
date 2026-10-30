# 08 — Power BI Deliverable

Power BI is a complementary BI deliverable and must reconcile to the canonical analytical layer.

## Deliverables
- Semantic model diagram and table grain documentation.
- Fact/dimension definitions.
- Relationship direction/cardinality documentation.
- KPI dictionary and DAX measure specification.
- Report wireframes/page specification.
- Data source connection instructions.
- Refresh/connectivity notes for local and deployed environments.
- Reconciliation checklist against MySQL/API outputs.
- Screenshots of actual completed report.
- Genuine `.pbix` only if it can be authored and verified. Never create a fake or empty PBIX.

## Suggested report pages
1. Executive Overview
2. Commercial Performance
3. Customer Intelligence
4. Product & Seller Performance
5. Operations & Delivery
6. Financial Scenarios
7. Data Quality

## DAX governance
- Use explicit measures, not implicit aggregations for important KPIs.
- Document filter context and time intelligence assumptions.
- Avoid duplicating logic that belongs in canonical SQL without reason.
- Reconcile totals across Power BI and API for identical filters and periods.
- Document when Power BI cannot connect directly to a private database from the service.

## Deployment caution
Render hosting does not automatically make MySQL reachable from Power BI Service. Verify network access, gateway needs, supported connector and refresh mode. Never expose production MySQL publicly merely to make a dashboard refresh.
