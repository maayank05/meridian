import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api, type Period } from "../services/api";
import { useApi } from "../features/useApi";
import { AsyncSection, Card, EmptyState, ProvenanceBadge } from "../components/ui";
import { formatBRL, formatChange, formatCompactBRL, formatInt, formatValue, monthLabel } from "../lib/format";
import type { Forecast, Kpi, MonthPoint } from "../types/api";

function KpiCard({ kpi, comparable }: { kpi: Kpi; comparable: boolean }) {
  const direction = kpi.change === null ? "" : kpi.change > 0 ? "up" : kpi.change < 0 ? "down" : "";
  return (
    <article className="kpi" aria-label={kpi.name}>
      <header>
        <h3 title={kpi.definition}>{kpi.name}</h3>
        <ProvenanceBadge value={kpi.provenance} />
      </header>
      <p className="kpi-value">{formatValue(kpi.value, kpi.unit)}</p>
      <p className="kpi-change">
        {comparable ? (
          <>
            <span className={`delta ${direction}`}>
              {direction === "up" ? "▲" : direction === "down" ? "▼" : ""} {formatChange(kpi.change)}
            </span>{" "}
            vs {formatValue(kpi.prior_value, kpi.unit)}
          </>
        ) : (
          <span className="muted">No comparable prior period</span>
        )}
      </p>
      <details>
        <summary>Definition</summary>
        <p>{kpi.definition}</p>
      </details>
    </article>
  );
}

function FlagDot(props: { cx?: number; cy?: number; payload?: MonthPoint }) {
  const { cx, cy, payload } = props;
  if (cx === undefined || cy === undefined || !payload) return null;
  const flagged = payload.coverage_flag !== "default_window";
  return <circle cx={cx} cy={cy} r={flagged ? 5 : 3} fill={flagged ? "var(--warn)" : "var(--accent)"} stroke="var(--surface)" />;
}

function TrendChart({ data }: { data: MonthPoint[] }) {
  if (!data.length) return <EmptyState message="No months in this period." />;
  return (
    <figure className="chart" aria-label="Monthly Delivered Merchandise Value">
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--grid)" />
          <XAxis dataKey="month" tickFormatter={monthLabel} tick={{ fontSize: 11 }} />
          <YAxis tickFormatter={formatCompactBRL} tick={{ fontSize: 11 }} width={70} />
          <Tooltip
            formatter={(v) => [formatBRL(Number(v)), "Delivered Merchandise Value"]}
            labelFormatter={(l) => {
              const p = data.find((d) => d.month === l);
              return `${monthLabel(String(l))}${p && p.coverage_flag !== "default_window" ? ` (${p.coverage_flag.replace("_", " ")})` : ""}`;
            }}
          />
          <Line type="linear" dataKey="delivered_merchandise_value" stroke="var(--accent)" strokeWidth={2} dot={<FlagDot />} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
      <figcaption className="muted">
        BRL by purchase month. Amber points are low-coverage (2016) or incomplete (2018-09/10) months: not a real decline (RULE-25).
      </figcaption>
    </figure>
  );
}

function ForecastPanel({ data }: { data: Forecast }) {
  return (
    <>
      <p>
        {data.model_justified ? (
          <>The statistical model beat the best baseline and is used.</>
        ) : (
          <>
            <strong>The statistical model did not beat the {data.best_baseline.replace("_", " ")} baseline</strong>, so the baseline is used.
          </>
        )}{" "}
        Evaluated one step ahead on {data.test_months[0]} to {data.test_months[data.test_months.length - 1]}.
      </p>
      <table className="table">
        <caption className="sr-only">Forecast evaluation</caption>
        <thead>
          <tr>
            <th scope="col">Method</th>
            <th scope="col">MAE (BRL)</th>
            <th scope="col">MAPE</th>
          </tr>
        </thead>
        <tbody>
          {[...data.evaluations].sort((a, b) => a.mae - b.mae).map((e) => (
            <tr key={e.method}>
              <td>{e.method.replace("_", " ")}</td>
              <td>{formatBRL(e.mae)}</td>
              <td>{e.mape === null ? "n/a" : `${(e.mape * 100).toFixed(1)}%`}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <table className="table">
        <caption className="sr-only">Forecast</caption>
        <thead>
          <tr>
            <th scope="col">Month</th>
            <th scope="col">Forecast</th>
            <th scope="col">Approx. 80% interval</th>
          </tr>
        </thead>
        <tbody>
          {data.forecast.map((f) => (
            <tr key={f.month}>
              <td>{f.month}</td>
              <td>{formatBRL(f.point)}</td>
              <td>
                {formatBRL(f.lower_80)} – {formatBRL(f.upper_80)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}

export function OverviewPage({ period }: { period: Period }) {
  const overview = useApi(() => api.overview(period), `ov-${period.start}-${period.end}`);
  const forecast = useApi(() => api.forecast(), "forecast");
  return (
    <div className="page">
      <h1>Executive overview</h1>
      <p className="lede">
        “Revenue” is the <strong>Delivered Merchandise Value (Revenue Proxy)</strong>: item value of delivered orders. Not accounting revenue, not
        profit.
      </p>
      <AsyncSection state={overview}>
        {(d) => (
          <>
            {!d.prior_period.comparable && <p className="note">{d.prior_period.note}</p>}
            <div className="kpi-grid">
              {d.kpis.map((k) => (
                <KpiCard key={k.id} kpi={k} comparable={d.prior_period.comparable} />
              ))}
            </div>
            <Card title="Monthly trend" provenance="derived">
              <TrendChart data={d.monthly} />
              <p className="muted">
                {formatInt(d.monthly.reduce((s, m) => s + m.orders_placed, 0))} orders placed across {d.monthly.length} months.
              </p>
            </Card>
          </>
        )}
      </AsyncSection>
      <Card title="Forecast: next 3 months" provenance="forecast">
        <AsyncSection state={forecast}>{(f) => <ForecastPanel data={f} />}</AsyncSection>
      </Card>
    </div>
  );
}
