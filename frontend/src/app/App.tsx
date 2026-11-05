import { NavLink, Navigate, Route, Routes, useSearchParams } from "react-router-dom";
import { api, type Period } from "../services/api";
import { useApi } from "../features/useApi";
import type { Metadata } from "../types/api";
import { OverviewPage } from "../pages/OverviewPage";
import { CustomersPage } from "../pages/CustomersPage";
import { ProductsOpsPage } from "../pages/ProductsOpsPage";
import { SimulatorPage } from "../pages/SimulatorPage";
import { QualityPage } from "../pages/QualityPage";

export const DEFAULT_PERIOD: Period = { start: "2017-01", end: "2018-08" }; // D-018 default window

const NAV = [
  { to: "/overview", label: "Overview" },
  { to: "/customers", label: "Customers" },
  { to: "/products-operations", label: "Products & Operations" },
  { to: "/simulator", label: "Decision Simulator" },
  { to: "/data-quality", label: "Data Quality & Methods" },
];

function usePeriod(): [Period, (p: Period) => void] {
  const [params, setParams] = useSearchParams();
  const period = { start: params.get("start") ?? DEFAULT_PERIOD.start, end: params.get("end") ?? DEFAULT_PERIOD.end };
  return [period, (p: Period) => setParams({ start: p.start, end: p.end })];
}

function PeriodFilter({ meta, period, onChange }: { meta: Metadata | null; period: Period; onChange: (p: Period) => void }) {
  const months = meta?.month_coverage ?? [];
  const invalid = period.start > period.end;
  const label = (m: { month: string; coverage_flag: string }) =>
    `${m.month.slice(0, 7)}${m.coverage_flag === "default_window" ? "" : m.coverage_flag === "low_coverage" ? " (low coverage)" : " (incomplete)"}`;
  return (
    <form className="period" aria-label="Analysis period" onSubmit={(e) => e.preventDefault()}>
      <label>
        From
        <select value={period.start} onChange={(e) => onChange({ ...period, start: e.target.value })} disabled={!months.length}>
          {months.map((m) => (
            <option key={m.month} value={m.month.slice(0, 7)}>
              {label(m)}
            </option>
          ))}
        </select>
      </label>
      <label>
        To
        <select value={period.end} onChange={(e) => onChange({ ...period, end: e.target.value })} disabled={!months.length}>
          {months.map((m) => (
            <option key={m.month} value={m.month.slice(0, 7)}>
              {label(m)}
            </option>
          ))}
        </select>
      </label>
      <button type="button" className="button ghost" onClick={() => onChange(DEFAULT_PERIOD)}>
        Reset
      </button>
      {invalid && (
        <span className="field-error" role="alert">
          Start month must not be after end month.
        </span>
      )}
    </form>
  );
}

export function App() {
  const [period, setPeriod] = usePeriod();
  const meta = useApi(() => api.metadata(), "metadata");
  const metadata = meta.status === "success" ? meta.data : null;
  const valid = period.start <= period.end;

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">◆</span> MERIDIAN
        </div>
        <p className="brand-sub">Northstar Commerce · simulated</p>
        <nav aria-label="Main">
          {NAV.map((n) => (
            <NavLink key={n.to} to={{ pathname: n.to, search: `?start=${period.start}&end=${period.end}` }} className="nav-link">
              {n.label}
            </NavLink>
          ))}
        </nav>
        <p className="sidebar-foot">
          Data: Olist public dataset (CC BY-NC-SA 4.0). Values in BRL.
          {metadata?.data_freshness_utc && <><br />Loaded {metadata.data_freshness_utc.slice(0, 16).replace("T", " ")} UTC</>}
        </p>
      </aside>
      <div className="main">
        <header className="topbar">
          <PeriodFilter meta={metadata} period={period} onChange={setPeriod} />
          <a className="button" href={valid ? api.reportUrl(period) : undefined} target="_blank" rel="noreferrer" aria-disabled={!valid}>
            Executive report
          </a>
        </header>
        {meta.status === "error" && (
          <div className="state state-error" role="alert">
            Metadata unavailable: {meta.error.message}
          </div>
        )}
        <main>
          {valid ? (
            <Routes>
              <Route path="/" element={<Navigate to="/overview" replace />} />
              <Route path="/overview" element={<OverviewPage period={period} />} />
              <Route path="/customers" element={<CustomersPage period={period} />} />
              <Route path="/products-operations" element={<ProductsOpsPage period={period} />} />
              <Route path="/simulator" element={<SimulatorPage period={period} />} />
              <Route path="/data-quality" element={<QualityPage metadata={metadata} />} />
              <Route path="*" element={<Navigate to="/overview" replace />} />
            </Routes>
          ) : (
            <p className="muted">Choose a valid period to see results.</p>
          )}
        </main>
      </div>
    </div>
  );
}
