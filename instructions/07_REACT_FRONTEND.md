# 07 — React Frontend Requirements

## Product experience
Build a polished, responsive enterprise analytics application. Avoid a generic template look. Use consistent design tokens, typography, spacing, colour, chart formatting and navigation.

## Main navigation
1. Overview
2. Customers
3. Products
4. Operations
5. Financial Intelligence
6. Decision Simulator
7. Forecasting & Risk
8. Data Quality
9. Executive Reports
10. Methodology & Definitions

## Common components
- App shell/sidebar/top bar.
- Date range and dimension filters.
- KPI cards with comparison period and definitions.
- Trend charts and breakdown charts.
- Sortable/paginated tables.
- Data provenance badges: Observed, Derived, Synthetic, Forecast, Scenario.
- Loading skeletons, empty states, error states and retry actions.
- Metric definition drawer/modal.
- Export controls only where export is implemented and tested.

## UX rules
- Every chart has title, unit, date range, source/provenance and readable axes.
- Do not use red/green alone to communicate status.
- Do not imply causality with chart titles.
- Explain denominators and exclusions.
- Avoid overloading pages with too many charts.
- Filters must have documented behaviour and reset controls.
- Currency and date formatting must be consistent.
- Never display mock data in production mode.
- For no data, show a useful empty state rather than a fake chart.

## React engineering
- Use TypeScript if feasible.
- Keep API client centralized.
- Use typed response models.
- Avoid duplicating business logic in components.
- Add component/page tests and frontend lint/build checks.
- Add error boundaries where useful.
- Ensure keyboard access and responsive layouts.

## Visualizations
Python Matplotlib/Seaborn are used for analytical notebooks/reports. For interactive React charts, select and document a suitable React-compatible chart library only after checking current compatibility and license. Do not attempt to render Matplotlib figures as the entire frontend chart solution.
