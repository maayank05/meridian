# 13 — Learning Guide: Build First, Learn From Scratch Afterwards

The user intends to have the product implemented first and then learn the underlying concepts from the ground up. The project must not become an unexplained AI-generated black box.

## Learning folder
Create `learning/` with:
- `README.md`
- `curriculum.md`
- `00_project_orientation/`
- `01_business_analysis/`
- `02_excel_and_business_metrics/`
- `03_sql_fundamentals/`
- `04_advanced_sql/`
- `05_python_fundamentals/`
- `06_pandas_and_data_cleaning/`
- `07_statistics/`
- `08_mysql_and_data_modelling/`
- `09_power_bi_and_dax/`
- `10_fastapi_and_backend/`
- `11_react_and_frontend/`
- `12_predictive_analytics/`
- `13_financial_modelling/`
- `14_testing_git_and_deployment/`
- `15_capstone_exercises/`

## Every learning topic must explain
1. What the concept is in plain language.
2. Why a business uses it.
3. Where it appears in MERIDIAN.
4. Which exact files/functions/queries implement it.
5. Inputs and outputs.
6. Step-by-step explanation.
7. Common mistakes and edge cases.
8. How to test/validate it.
9. Alternatives and trade-offs.
10. Exercises using the actual project.
11. Interview questions and model answers.
12. A practical task to recreate or modify the implementation.

## Example
For customer cohort retention, explain:
- Cohort meaning and business purpose.
- Cohort assignment rule.
- Eligible customer population.
- SQL date functions/windowing/aggregation used.
- Query walkthrough.
- Expected output shape.
- Edge cases and test fixtures.
- How to interpret the heatmap.
- Why retention definitions vary.
- Exercises to change the cohort period or eligibility definition.

## Learning quality
- Teach from beginner to advanced.
- Do not simply paste generated code and call it a lesson.
- Explain every important business formula.
- Include exercises with solutions in separate files.
- Add a glossary and a project-wide concept map.
- Keep lessons aligned with the actual final code; update them when implementation changes.
