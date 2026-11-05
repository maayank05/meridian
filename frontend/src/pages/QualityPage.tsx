import { api } from "../services/api";
import { useApi } from "../features/useApi";
import { AsyncSection, Card, EmptyState, ProvenanceBadge } from "../components/ui";
import { formatInt } from "../lib/format";
import type { Metadata } from "../types/api";

const SEVERITY_ICON = { blocking: "⛔", warning: "⚠", info: "ℹ" } as const;

export function QualityPage({ metadata }: { metadata: Metadata | null }) {
  const state = useApi(() => api.quality(), "quality");
  return (
    <div className="page">
      <h1>Data quality &amp; methods</h1>
      <AsyncSection state={state}>
        {(q) =>
          q.latest_run === null ? (
            <EmptyState message="No successful load yet. Run: python -m meridian.ingestion" />
          ) : (
            <>
              <Card title={`Latest load: run ${q.latest_run.run_id}`} provenance="source_observed"
                footer={<span className="muted">Finished {q.latest_run.finished_at_utc.replace("T", " ").slice(0, 19)} UTC · failed runs on record: {q.failed_runs}</span>}>
                <div className="table-scroll">
                  <table className="table">
                    <caption className="sr-only">Source files</caption>
                    <thead>
                      <tr>
                        <th scope="col">File</th>
                        <th scope="col">Rows</th>
                        <th scope="col">SHA-256 (first 12)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {q.files.map((f) => (
                        <tr key={f.file_name}>
                          <td>{f.file_name}</td>
                          <td>{formatInt(f.row_count)}</td>
                          <td><code>{f.sha256.slice(0, 12)}</code></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
              <Card title="Data-quality checks" provenance="derived" footer={<span className="muted">Blocking checks must be 0 or the load is rolled back. Others are counted and handled by rule.</span>}>
                <div className="table-scroll">
                  <table className="table">
                    <caption className="sr-only">Data-quality checks</caption>
                    <thead>
                      <tr>
                        <th scope="col">Severity</th>
                        <th scope="col">Check</th>
                        <th scope="col">Affected rows</th>
                      </tr>
                    </thead>
                    <tbody>
                      {q.checks.map((c) => (
                        <tr key={c.check_id}>
                          <td>
                            <span aria-hidden="true">{SEVERITY_ICON[c.severity]}</span> {c.severity}
                          </td>
                          <td>{c.description}</td>
                          <td>{formatInt(c.affected_rows)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Card>
            </>
          )
        }
      </AsyncSection>
      <Card title="Definitions and provenance">
        <dl className="defs">
          {(metadata?.kpis ?? []).map((k) => (
            <div key={k.id}>
              <dt>
                {k.id} · {k.name} <ProvenanceBadge value={k.provenance} />
              </dt>
              <dd>{k.definition}</dd>
            </div>
          ))}
        </dl>
        <p className="muted">
          Provenance classes: Observed (source), Derived (calculated), Synthetic (assumption), Forecast (model output), Scenario (hypothetical).
          Default analysis window 2017-01 to 2018-08; earlier months have low coverage and 2018-09/10 are incomplete.
        </p>
      </Card>
    </div>
  );
}
