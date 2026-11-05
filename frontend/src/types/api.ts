// Typed contracts for the MERIDIAN /api/v1 responses (mirrors backend/meridian/analytics/dashboard.py).

export type Provenance = "source_observed" | "derived" | "synthetic_assumption" | "forecast" | "scenario_output";
export type CoverageFlag = "default_window" | "low_coverage" | "incomplete_cutoff" | "outside_source";

export interface Kpi {
  id: string;
  name: string;
  unit: "BRL" | "%" | string;
  provenance: Provenance;
  definition: string;
  value: number | null;
  prior_value: number | null;
  change: number | null;
}

export interface MonthPoint {
  month: string;
  coverage_flag: CoverageFlag;
  delivered_merchandise_value: number;
  orders_placed: number;
  delivered_orders: number;
  average_order_value: number | null;
}

export interface Overview {
  period: { start: string; end: string };
  prior_period: { start: string; end: string; comparable: boolean; note: string | null };
  months_flagged: string[];
  kpis: Kpi[];
  monthly: MonthPoint[];
}

export interface Metadata {
  data_freshness_utc: string | null;
  default_period: { start: string; end: string };
  data_coverage: { start: string; end: string };
  month_coverage: { month: string; coverage_flag: CoverageFlag }[];
  provenance_classes: Provenance[];
  currency: string;
  kpis: { id: string; name: string; unit: string; provenance: Provenance; definition: string }[];
}

export interface Customers {
  provenance: Provenance;
  repeat_rate: { customers: number; repeat_customers: number; repeat_rate: number | null };
  concentration: { customer_top10_share: number | null; seller_top10_share: number | null; customers: number; sellers: number };
  cohorts: { cohort_month: string; cohort_size: number; observable_months: number; retention: { months_since_first: number; active_customers: number; rate: number }[] }[];
  note: string;
}

export interface Products {
  provenance: Provenance;
  total_delivered_merchandise_value: number;
  categories: {
    category: string;
    delivered_merchandise_value: number;
    share: number | null;
    delivered_items: number;
    delivered_orders: number;
    small_sample: boolean;
    is_category_missing: boolean;
    is_untranslated: boolean;
  }[];
}

export interface Operations {
  provenance: Provenance;
  delivery: {
    delivered_orders: number;
    excluded_missing_delivery_date: number;
    excluded_ambiguous_time: number;
    lead_time_orders: number;
    avg_lead_time_days: number | null;
    on_time_rate: number | null;
    late_orders: number;
    avg_days_late: number | null;
    monthly: { month: string; coverage_flag: CoverageFlag; on_time_rate: number | null; avg_lead_time_days: number | null }[];
  };
  reviews: { orders_with_review: number; avg_review_score: number | null; orders_with_shared_review: number; note: string };
  payments: {
    by_type: { payment_type: string; records: number; value: number; share_of_value: number | null }[];
    avg_installments_valid: number | null;
    invalid_installment_records_excluded: number;
  };
  payment_reconciliation_all_time: Record<string, string | number>[];
}

export interface Quality {
  latest_run: { run_id: number; started_at_utc: string; finished_at_utc: string } | null;
  files: { file_name: string; row_count: number; sha256: string }[];
  checks: { check_id: string; description: string; severity: "blocking" | "warning" | "info"; affected_rows: number; status: string }[];
  failed_runs: number;
}

export interface Forecast {
  provenance: Provenance;
  test_months: string[];
  evaluations: { method: string; mae: number; rmse: number; mape: number | null }[];
  best_baseline: string;
  model_justified: boolean;
  chosen_method: string;
  forecast: { month: string; point: number; lower_80: number; upper_80: number }[];
}

export interface ScenarioCase {
  case: string;
  uplift: number;
  incremental_revenue_proxy: number;
  incremental_contribution: number;
  net_benefit: number;
  roi: number | null;
  payback_months: number | null;
  provenance: Provenance;
}

export interface Simulation {
  provenance: Provenance;
  baseline: { monthly_delivered_merchandise_value: number; provenance: Provenance; basis: string };
  assumptions: { horizon_months: number; intervention_cost: number; contribution_margin: number; provenance: Provenance };
  cases: ScenarioCase[];
  break_even_uplift: number | null;
  sensitivity: ScenarioCase[];
  disclaimer: string;
}

export interface Campaign {
  provenance: Provenance;
  scenario_cac: number | null;
  attributed_roas: number;
  incremental_roas: number;
  incremental_revenue_proxy: number;
  net_benefit: number;
  roi: number;
  disclaimer: string;
}

export interface ApiErrorBody {
  error: { code: string; message: string; request_id: string | null; details?: { field: string; message: string }[] };
}
