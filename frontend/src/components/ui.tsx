import type { ReactNode } from "react";
import type { ApiError } from "../services/api";
import type { ApiState } from "../features/useApi";
import type { Provenance } from "../types/api";

const PROVENANCE_LABEL: Record<Provenance, string> = {
  source_observed: "Observed",
  derived: "Derived",
  synthetic_assumption: "Synthetic",
  forecast: "Forecast",
  scenario_output: "Scenario",
};

export function ProvenanceBadge({ value }: { value: Provenance }) {
  return (
    <span className={`badge badge-${value}`} title={`Provenance: ${value}`}>
      {PROVENANCE_LABEL[value]}
    </span>
  );
}

export function Loading({ label = "Loading data…" }: { label?: string }) {
  return (
    <div className="state" role="status" aria-live="polite">
      <div className="skeleton" />
      <div className="skeleton short" />
      <span className="sr-only">{label}</span>
    </div>
  );
}

export function ErrorState({ error, onRetry }: { error: ApiError; onRetry: () => void }) {
  return (
    <div className="state state-error" role="alert">
      <strong>Could not load this section.</strong>
      <p>{error.message}</p>
      {error.requestId && <p className="muted">Request ID: {error.requestId}</p>}
      <button type="button" className="button" onClick={onRetry}>
        Retry
      </button>
    </div>
  );
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="state state-empty">
      <p>{message}</p>
    </div>
  );
}

/** Render loading / error / success consistently for any API state (FR-003). */
export function AsyncSection<T>({ state, children }: { state: ApiState<T> & { retry: () => void }; children: (data: T) => ReactNode }) {
  if (state.status === "loading") return <Loading />;
  if (state.status === "error") return <ErrorState error={state.error} onRetry={state.retry} />;
  return <>{children(state.data)}</>;
}

export function Card({ title, provenance, children, footer }: { title: string; provenance?: Provenance; children: ReactNode; footer?: ReactNode }) {
  return (
    <section className="card" aria-label={title}>
      <header className="card-head">
        <h2>{title}</h2>
        {provenance && <ProvenanceBadge value={provenance} />}
      </header>
      {children}
      {footer && <footer className="card-foot">{footer}</footer>}
    </section>
  );
}

export function Stat({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="stat">
      <span className="stat-label">{label}</span>
      <span className="stat-value">{value}</span>
      {hint && <span className="stat-hint">{hint}</span>}
    </div>
  );
}
