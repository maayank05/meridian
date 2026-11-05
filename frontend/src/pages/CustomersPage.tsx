import { api, type Period } from "../services/api";
import { useApi } from "../features/useApi";
import { AsyncSection, Card, EmptyState, Stat } from "../components/ui";
import { formatInt, formatPct, monthLabel } from "../lib/format";

const MAX_MONTHS = 12;

export function CustomersPage({ period }: { period: Period }) {
  const state = useApi(() => api.customers(period), `cu-${period.start}-${period.end}`);
  return (
    <div className="page">
      <h1>Customers</h1>
      <p className="lede">People are identified by <code>customer_unique_id</code>; each order has its own <code>customer_id</code> in the source.</p>
      <AsyncSection state={state}>
        {(d) => (
          <>
            <div className="grid-3">
              <Card title="Repeat purchase rate" provenance="derived">
                <Stat label="People with 2+ delivered orders" value={formatPct(d.repeat_rate.repeat_rate, 2)}
                  hint={`${formatInt(d.repeat_rate.repeat_customers)} of ${formatInt(d.repeat_rate.customers)} purchasing people`} />
              </Card>
              <Card title="Customer concentration" provenance="derived">
                <Stat label="Share of value from top 10% of people" value={formatPct(d.concentration.customer_top10_share)}
                  hint={`${formatInt(d.concentration.customers)} people`} />
              </Card>
              <Card title="Seller concentration" provenance="derived">
                <Stat label="Share of value from top 10% of sellers" value={formatPct(d.concentration.seller_top10_share)}
                  hint={`${formatInt(d.concentration.sellers)} sellers`} />
              </Card>
            </div>
            <Card title="Cohort retention (share of cohort active in month n)" provenance="derived" footer={<span className="muted">{d.note}</span>}>
              {d.cohorts.length === 0 ? (
                <EmptyState message="No acquisition cohorts start in this period." />
              ) : (
                <div className="table-scroll">
                  <table className="table cohort">
                    <caption className="sr-only">Cohort retention by months since first delivered order</caption>
                    <thead>
                      <tr>
                        <th scope="col">Cohort</th>
                        <th scope="col">Size</th>
                        {Array.from({ length: MAX_MONTHS }, (_, i) => (
                          <th scope="col" key={i}>
                            M{i + 1}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {d.cohorts.map((c) => {
                        const byMonth = new Map(c.retention.map((r) => [r.months_since_first, r.rate]));
                        return (
                          <tr key={c.cohort_month}>
                            <th scope="row">{monthLabel(c.cohort_month)}</th>
                            <td>{formatInt(c.cohort_size)}</td>
                            {Array.from({ length: MAX_MONTHS }, (_, i) => {
                              const n = i + 1;
                              const rate = byMonth.get(n);
                              if (n > c.observable_months) {
                                return (
                                  <td key={i} className="muted" title="Not observable: after the last full-coverage month">
                                    ·
                                  </td>
                                );
                              }
                              return (
                                <td key={i} style={rate ? { background: `rgba(37, 99, 235, ${Math.min(0.85, rate * 20)})` } : undefined}>
                                  {formatPct(rate ?? 0, 2)}
                                </td>
                              );
                            })}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </Card>
          </>
        )}
      </AsyncSection>
    </div>
  );
}
