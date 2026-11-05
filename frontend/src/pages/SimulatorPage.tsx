import { useState, type FormEvent } from "react";
import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api, ApiError, type Period } from "../services/api";
import { Card, ErrorState, ProvenanceBadge } from "../components/ui";
import { formatBRL, formatCompactBRL, formatPct } from "../lib/format";
import type { Campaign, Simulation } from "../types/api";

type Status<T> = { kind: "idle" } | { kind: "loading" } | { kind: "error"; error: ApiError } | { kind: "done"; data: T };

function NumberField({ label, name, value, onChange, step = "any", hint }: {
  label: string; name: string; value: string; onChange: (v: string) => void; step?: string; hint?: string;
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <input name={name} type="number" inputMode="decimal" step={step} value={value} onChange={(e) => onChange(e.target.value)} required />
      {hint && <small className="muted">{hint}</small>}
    </label>
  );
}

function ScenarioForm({ period }: { period: Period }) {
  const [f, setF] = useState({ cost: "50000", margin: "0.25", horizon: "12", down: "0", base: "0.02", up: "0.05" });
  const [status, setStatus] = useState<Status<Simulation>>({ kind: "idle" });
  const set = (k: keyof typeof f) => (v: string) => setF({ ...f, [k]: v });

  async function submit(e: FormEvent) {
    e.preventDefault();
    setStatus({ kind: "loading" });
    try {
      const data = await api.simulate({
        start_month: period.start, end_month: period.end, horizon_months: Number(f.horizon), intervention_cost: f.cost,
        contribution_margin: f.margin, downside_uplift: f.down, base_uplift: f.base, upside_uplift: f.up,
      });
      setStatus({ kind: "done", data });
    } catch (err) {
      setStatus({ kind: "error", error: err instanceof ApiError ? err : new ApiError(0, String(err)) });
    }
  }

  return (
    <Card title="Intervention scenario" provenance="scenario_output">
      <form className="form-grid" onSubmit={submit} aria-label="Intervention scenario inputs">
        <NumberField label="Intervention cost (BRL)" name="cost" value={f.cost} onChange={set("cost")} />
        <NumberField label="Contribution margin (0–1)" name="margin" value={f.margin} onChange={set("margin")} hint="Synthetic assumption: no cost data exists" />
        <NumberField label="Horizon (months)" name="horizon" value={f.horizon} onChange={set("horizon")} step="1" />
        <NumberField label="Downside uplift" name="down" value={f.down} onChange={set("down")} hint="0.02 = +2%" />
        <NumberField label="Base uplift" name="base" value={f.base} onChange={set("base")} />
        <NumberField label="Upside uplift" name="up" value={f.up} onChange={set("up")} />
        <button className="button" type="submit" disabled={status.kind === "loading"}>
          {status.kind === "loading" ? "Calculating…" : "Compare scenarios"}
        </button>
      </form>
      {status.kind === "error" && (
        <>
          <ErrorState error={status.error} onRetry={() => setStatus({ kind: "idle" })} />
          {status.error.details.length > 0 && (
            <ul className="field-error">
              {status.error.details.map((d) => (
                <li key={d.field}>
                  {d.field}: {d.message}
                </li>
              ))}
            </ul>
          )}
        </>
      )}
      {status.kind === "done" && <ScenarioResult data={status.data} />}
    </Card>
  );
}

function ScenarioResult({ data }: { data: Simulation }) {
  return (
    <div className="result" aria-live="polite">
      <p className="note">{data.disclaimer}</p>
      <p>
        Baseline <ProvenanceBadge value={data.baseline.provenance} />: {formatBRL(data.baseline.monthly_delivered_merchandise_value)} per month ({data.baseline.basis}).
        Break-even uplift: <strong>{data.break_even_uplift === null ? "undefined" : formatPct(data.break_even_uplift, 2)}</strong>.
      </p>
      <div className="table-scroll">
        <table className="table">
          <caption className="sr-only">Scenario comparison</caption>
          <thead>
            <tr>
              <th scope="col">Case</th>
              <th scope="col">Uplift</th>
              <th scope="col">Incremental revenue proxy</th>
              <th scope="col">Incremental contribution</th>
              <th scope="col">Net benefit</th>
              <th scope="col">ROI</th>
              <th scope="col">Payback</th>
            </tr>
          </thead>
          <tbody>
            {data.cases.map((c) => (
              <tr key={c.case}>
                <td>{c.case}</td>
                <td>{formatPct(c.uplift)}</td>
                <td>{formatBRL(c.incremental_revenue_proxy)}</td>
                <td>{formatBRL(c.incremental_contribution)}</td>
                <td className={c.net_benefit < 0 ? "neg" : "pos"}>{formatBRL(c.net_benefit)}</td>
                <td>{c.roi === null ? "undefined (zero cost)" : formatPct(c.roi)}</td>
                <td>{c.payback_months === null ? "none" : `${c.payback_months.toFixed(1)} months`}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <figure className="chart" aria-label="Sensitivity of net benefit to uplift">
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={data.sensitivity} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--grid)" />
            <XAxis dataKey="uplift" tickFormatter={(v) => `${Math.round(Number(v) * 100)}%`} tick={{ fontSize: 11 }} />
            <YAxis tickFormatter={formatCompactBRL} tick={{ fontSize: 11 }} width={70} />
            <ReferenceLine y={0} stroke="var(--muted)" />
            <Tooltip formatter={(v) => [formatBRL(Number(v)), "Net benefit"]} labelFormatter={(l) => `Uplift ${formatPct(Number(l))}`} />
            <Line dataKey="net_benefit" stroke="var(--accent)" strokeWidth={2} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
        <figcaption className="muted">Net benefit across uplift assumptions (scenario output).</figcaption>
      </figure>
    </div>
  );
}

function CampaignForm() {
  const [f, setF] = useState({ spend: "20000", customers: "4000", revenue: "800000", attributed: "0.2", lift: "0.03", margin: "0.25" });
  const [status, setStatus] = useState<Status<Campaign>>({ kind: "idle" });
  const set = (k: keyof typeof f) => (v: string) => setF({ ...f, [k]: v });

  async function submit(e: FormEvent) {
    e.preventDefault();
    setStatus({ kind: "loading" });
    try {
      const data = await api.campaign({
        synthetic_spend: f.spend, baseline_new_customers: Number(f.customers), baseline_revenue_proxy: f.revenue,
        attributed_share: f.attributed, incremental_lift: f.lift, contribution_margin: f.margin,
      });
      setStatus({ kind: "done", data });
    } catch (err) {
      setStatus({ kind: "error", error: err instanceof ApiError ? err : new ApiError(0, String(err)) });
    }
  }

  return (
    <Card title="Marketing campaign scenario (synthetic)" provenance="synthetic_assumption">
      <p className="note">No observed marketing data exists. Every input below is an assumption; outputs are scenario estimates (D-015).</p>
      <form className="form-grid" onSubmit={submit} aria-label="Campaign scenario inputs">
        <NumberField label="Synthetic spend (BRL)" name="spend" value={f.spend} onChange={set("spend")} />
        <NumberField label="Baseline new customers" name="customers" value={f.customers} onChange={set("customers")} step="1" />
        <NumberField label="Baseline revenue proxy (BRL)" name="revenue" value={f.revenue} onChange={set("revenue")} />
        <NumberField label="Attributed share (0–1)" name="attributed" value={f.attributed} onChange={set("attributed")} hint="Credited by an attribution rule" />
        <NumberField label="Incremental lift (0–1)" name="lift" value={f.lift} onChange={set("lift")} hint="Would not have happened otherwise" />
        <NumberField label="Contribution margin (0–1)" name="margin" value={f.margin} onChange={set("margin")} />
        <button className="button" type="submit" disabled={status.kind === "loading"}>
          Evaluate campaign
        </button>
      </form>
      {status.kind === "error" && <ErrorState error={status.error} onRetry={() => setStatus({ kind: "idle" })} />}
      {status.kind === "done" && (
        <div className="result" aria-live="polite">
          <div className="grid-3">
            <div className="stat"><span className="stat-label">Scenario CAC</span><span className="stat-value">{formatBRL(status.data.scenario_cac)}</span></div>
            <div className="stat"><span className="stat-label">Attributed ROAS</span><span className="stat-value">{status.data.attributed_roas.toFixed(2)}×</span></div>
            <div className="stat"><span className="stat-label">Incremental ROAS</span><span className="stat-value">{status.data.incremental_roas.toFixed(2)}×</span></div>
          </div>
          <p>
            Net benefit: <strong className={status.data.net_benefit < 0 ? "neg" : "pos"}>{formatBRL(status.data.net_benefit)}</strong>. Attributed ROAS is usually
            higher than incremental ROAS because attribution credits sales that may have happened anyway.
          </p>
        </div>
      )}
    </Card>
  );
}

export function SimulatorPage({ period }: { period: Period }) {
  return (
    <div className="page">
      <h1>Decision simulator</h1>
      <p className="lede">Hypothetical “what-if” estimates. ROI uses your assumed contribution margin, never revenue. Nothing here is an observed result.</p>
      <ScenarioForm period={period} />
      <CampaignForm />
    </div>
  );
}
