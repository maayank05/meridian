# 01 — Project Charter

## Working title
**MERIDIAN — Business Intelligence & Decision Intelligence Platform**

## Business case
Northstar Commerce is a simulated online retail business. Management has fragmented sales, customer, product, seller, payment and fulfilment information. It needs a reliable analytical foundation and decision-support experience to investigate performance, understand customers and operations, evaluate financial scenarios and communicate evidence-based actions.

## Primary dataset
Brazilian E-Commerce Public Dataset by Olist:
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce

Treat it as the primary real-world case dataset. Confirm actual files, schema, row counts, date coverage, relationships, licensing and usage terms before modelling.

## Target users
- CEO / executive leadership: overall performance, risks and decisions.
- Finance / FP&A: revenue definitions, planning assumptions, variance and scenario economics.
- Marketing: acquisition and campaign performance only where data supports it.
- Commercial / category managers: products, categories, sellers and customer behaviour.
- Operations: fulfilment, delivery and service performance.
- Data / BI analysts: definitions, lineage, quality and drill-down.
- Business analysts: requirements, rules, process and acceptance evidence.

## Objectives
1. Deliver a reproducible data ingestion and transformation pipeline.
2. Create a tested MySQL analytical data model.
3. Deliver trustworthy SQL and Python analytical outputs.
4. Provide a React application backed by FastAPI.
5. Provide Power BI reporting specifications and a genuine report where possible.
6. Quantify business scenarios transparently.
7. Deliver a complete BA/BI documentation set.
8. Make the product teachable through a structured learning guide.

## Success measures
- A new developer can set up the project using documented instructions.
- A valid dataset can be ingested reproducibly.
- Core metrics reconcile to source records or documented reference calculations.
- Important business logic has automated tests.
- All ten modules have an explicit status; no module is represented as complete when it is not.
- CI runs without private credentials using fixtures.
- A deployed application can be reached and smoke-tested.
- A reviewer can trace key KPIs to definitions, SQL/Python logic and source data.
- Simulated assumptions are visibly labelled.

## Out of scope for initial release
- Real-time streaming.
- Production multi-tenant SaaS.
- Payment processing.
- Actual customer outreach or campaign execution.
- Causal claims without experimental/quasi-experimental evidence.
- Full ERP integration.
- Complex cloud infrastructure not justified by requirements.
