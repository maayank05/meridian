import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api, type Period } from "../services/api";
import { useApi } from "../features/useApi";
import { AsyncSection, Card, EmptyState, Stat } from "../components/ui";
import { formatBRL, formatCompactBRL, formatInt, formatPct, monthLabel } from "../lib/format";

const TOP = 12;

export function ProductsOpsPage({ period }: { period: Period }) {
  const key = `${period.start}-${period.end}`;
  const products = useApi(() => api.products(period), `pr-${key}`);
  const ops = useApi(() => api.operations(period), `op-${key}`);
  return (
    <div className="page">
      <h1>Products &amp; operations</h1>
      <AsyncSection state={products}>
        {(p) =>
          p.categories.length === 0 ? (
            <EmptyState message="No delivered orders in this period." />
          ) : (
            <Card title={`Top ${TOP} categories by Delivered Merchandise Value`} provenance="derived"
              footer={<span className="muted">* fewer than 30 orders (small sample). “unknown” = product without category.</span>}>
              <ResponsiveContainer width="100%" height={Math.min(TOP, p.categories.length) * 30 + 40}>
                <BarChart data={p.categories.slice(0, TOP)} layout="vertical" margin={{ left: 40, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--grid)" horizontal={false} />
                  <XAxis type="number" tickFormatter={formatCompactBRL} tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="category" width={170} tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(v) => [formatBRL(Number(v)), "Delivered Merchandise Value"]} />
                  <Bar dataKey="delivered_merchandise_value" fill="var(--accent)" isAnimationActive={false} />
                </BarChart>
              </ResponsiveContainer>
              <div className="table-scroll">
                <table className="table">
                  <caption className="sr-only">Categories</caption>
                  <thead>
                    <tr>
                      <th scope="col">Category</th>
                      <th scope="col">Value</th>
                      <th scope="col">Share</th>
                      <th scope="col">Orders</th>
                    </tr>
                  </thead>
                  <tbody>
                    {p.categories.slice(0, TOP).map((c) => (
                      <tr key={c.category}>
                        <td>
                          {c.category}
                          {c.small_sample && " *"}
                          {c.is_untranslated && <span className="muted"> (untranslated)</span>}
                        </td>
                        <td>{formatBRL(c.delivered_merchandise_value)}</td>
                        <td>{formatPct(c.share)}</td>
                        <td>{formatInt(c.delivered_orders)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )
        }
      </AsyncSection>
      <AsyncSection state={ops}>
        {(o) => (
          <>
            <div className="grid-3">
              <Card title="Delivery" provenance="derived"
                footer={<span className="muted">Delivered orders only. {formatInt(o.delivery.excluded_missing_delivery_date)} without delivery date and {formatInt(o.delivery.excluded_ambiguous_time)} with ambiguous DST time excluded from lead time.</span>}>
                <Stat label="On time (on or before estimate)" value={formatPct(o.delivery.on_time_rate)} />
                <Stat label="Average lead time" value={o.delivery.avg_lead_time_days === null ? "n/a" : `${o.delivery.avg_lead_time_days.toFixed(1)} days`} />
                <Stat label="Late orders" value={formatInt(o.delivery.late_orders)}
                  hint={o.delivery.avg_days_late === null ? undefined : `${o.delivery.avg_days_late.toFixed(1)} days late on average`} />
              </Card>
              <Card title="Reviews" provenance="derived" footer={<span className="muted">{o.reviews.note}</span>}>
                <Stat label="Average score (1–5)" value={o.reviews.avg_review_score === null ? "n/a" : o.reviews.avg_review_score.toFixed(2)}
                  hint={`${formatInt(o.reviews.orders_with_review)} orders reviewed`} />
                <Stat label="Orders sharing a review record" value={formatInt(o.reviews.orders_with_shared_review)} />
              </Card>
              <Card title="Payments" provenance="derived"
                footer={<span className="muted">{formatInt(o.payments.invalid_installment_records_excluded)} invalid credit-card records (0 instalments) excluded from the average.</span>}>
                {o.payments.by_type.map((t) => (
                  <Stat key={t.payment_type} label={t.payment_type.replace("_", " ")} value={formatPct(t.share_of_value)} hint={`${formatInt(t.records)} records`} />
                ))}
                <Stat label="Average instalments" value={o.payments.avg_installments_valid?.toFixed(2) ?? "n/a"} />
              </Card>
            </div>
            <Card title="On-time delivery rate by purchase month" provenance="derived">
              {o.delivery.monthly.length === 0 ? (
                <EmptyState message="No delivered orders in this period." />
              ) : (
                <ResponsiveContainer width="100%" height={240}>
                  <LineChart data={o.delivery.monthly} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--grid)" />
                    <XAxis dataKey="month" tickFormatter={monthLabel} tick={{ fontSize: 11 }} />
                    <YAxis domain={[0, 1]} tickFormatter={(v) => `${Math.round(Number(v) * 100)}%`} tick={{ fontSize: 11 }} />
                    <Tooltip formatter={(v) => [formatPct(Number(v)), "On time"]} labelFormatter={(l) => monthLabel(String(l))} />
                    <Line dataKey="on_time_rate" stroke="var(--accent)" strokeWidth={2} dot={false} isAnimationActive={false} connectNulls={false} />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </Card>
            <Card title="Payments vs item value + freight (all time, by order status)" provenance="derived">
              <div className="table-scroll">
                <table className="table">
                  <caption className="sr-only">Payment reconciliation</caption>
                  <thead>
                    <tr>
                      <th scope="col">Status</th>
                      <th scope="col">Orders</th>
                      <th scope="col">Matched (±0.01)</th>
                      <th scope="col">Payments higher</th>
                      <th scope="col">Payments lower</th>
                      <th scope="col">Payments only</th>
                    </tr>
                  </thead>
                  <tbody>
                    {o.payment_reconciliation_all_time.map((r) => (
                      <tr key={String(r.order_status)}>
                        <td>{String(r.order_status)}</td>
                        <td>{formatInt(Number(r.orders))}</td>
                        <td>{formatInt(Number(r.matched_orders))}</td>
                        <td>{formatInt(Number(r.payments_higher_orders))}</td>
                        <td>{formatInt(Number(r.payments_lower_orders))}</td>
                        <td>{formatInt(Number(r.payments_only_orders))}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </>
        )}
      </AsyncSection>
    </div>
  );
}
