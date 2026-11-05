"""Concise HTML executive report built from the SAME dashboard payloads the API serves (FR-028).

Observations are descriptive comparisons of computed values only. No causal claims (RULE-19), no profit
(RULE-18), synthetic and forecast values labelled (RULE-16).
"""

import base64
import html
import io
from datetime import UTC, date, datetime

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from sqlalchemy import Connection  # noqa: E402

from meridian.analytics import dashboard  # noqa: E402

FLAG_LABEL = {"low_coverage": "low coverage", "incomplete_cutoff": "incomplete (extract cutoff)"}


def _fmt(v, unit: str) -> str:
    if v is None:
        return "n/a"
    if unit == "BRL":
        return f"R$ {v:,.2f}"
    if unit == "%":
        return f"{v:.2%}"
    return f"{v:,.0f}"


def _pct(v) -> str:
    return "n/a" if v is None else f"{v:+.1%}"


def _chart(monthly: list[dict]) -> str:
    fig, ax = plt.subplots(figsize=(8, 3), dpi=110)
    xs = [m["month"][:7] for m in monthly]
    ax.plot(xs, [m["delivered_merchandise_value"] for m in monthly], color="#2563eb", marker="o", linewidth=1.8)
    for i, m in enumerate(monthly):
        if m["coverage_flag"] != "default_window":
            ax.axvspan(i - 0.5, i + 0.5, color="#f59e0b", alpha=0.18, linewidth=0)
    ax.set_title("Delivered Merchandise Value (Revenue Proxy) by purchase month, BRL", fontsize=10)
    ax.set_ylabel("BRL")
    ax.tick_params(axis="x", labelrotation=60, labelsize=7)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v / 1000:,.0f}k"))
    ax.grid(axis="y", alpha=0.3)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def build_report(conn: Connection, start: date, end: date) -> tuple[str, dict]:
    """Return (html, payloads). payloads are exactly the API payloads used, for reconciliation tests."""
    meta = dashboard.metadata(conn)
    ov = dashboard.overview(conn, start, end)
    cu = dashboard.customers(conn, start, end)
    pr = dashboard.products(conn, start, end)
    op = dashboard.operations(conn, start, end)
    qu = dashboard.quality(conn)
    try:
        fc = dashboard.forecast(conn)
    except ValueError as exc:
        fc = {"unavailable": str(exc)}
    payloads = {
        "metadata": meta,
        "overview": ov,
        "customers": cu,
        "products": pr,
        "operations": op,
        "quality": qu,
        "forecast": fc,
    }
    e = html.escape
    kpi_rows = "".join(
        f"<tr><td>{e(k['name'])}</td><td>{_fmt(k['value'], k['unit'])}</td><td>{_fmt(k['prior_value'], k['unit'])}"
        f"</td><td>{_pct(k['change'])}</td><td>{e(k['provenance'])}</td></tr>"
        for k in ov["kpis"]
    )
    k01 = next(k for k in ov["kpis"] if k["id"] == "K01")
    observations = [
        f"Delivered Merchandise Value (Revenue Proxy) was {_fmt(k01['value'], 'BRL')} for {ov['period']['start']} "
        f"to {ov['period']['end']}, {_pct(k01['change'])} versus the prior period of equal length "
        f"({ov['prior_period']['start']} to {ov['prior_period']['end']})."
        if k01["change"] is not None
        else f"Delivered Merchandise Value (Revenue Proxy) was {_fmt(k01['value'], 'BRL')}. No period-over-period change "
        "is reported because the prior period of equal length is not fully covered by the data.",
        f"{cu['repeat_rate']['repeat_customers']:,} of {cu['repeat_rate']['customers']:,} purchasing people "
        f"({_fmt(cu['repeat_rate']['repeat_rate'], '%')}) placed two or more delivered orders in the period.",
        f"On-time delivery (delivered on or before the estimated date) was {_fmt(op['delivery']['on_time_rate'], '%')}"
        f"; {op['delivery']['excluded_ambiguous_time']:,} orders were excluded from lead-time averages because their "
        "local time is ambiguous (DST).",
    ]
    if pr["categories"]:
        top = pr["categories"][0]
        observations.append(
            f"The largest category by Delivered Merchandise Value was {e(top['category'])} "
            f"({_fmt(top['share'], '%')} of the total)."
        )
    cats = "".join(
        f"<tr><td>{e(c['category'])}{' *' if c['small_sample'] else ''}</td>"
        f"<td>{_fmt(c['delivered_merchandise_value'], 'BRL')}</td><td>{_fmt(c['share'], '%')}</td>"
        f"<td>{c['delivered_orders']:,}</td></tr>"
        for c in pr["categories"][:10]
    )
    dq = "".join(
        f"<li>{e(c['description'])}: <b>{c['affected_rows']:,}</b> rows ({e(c['severity'])})</li>"
        for c in qu["checks"]
        if c["affected_rows"] > 0
    )
    flagged = (
        ", ".join(
            f"{m} ({FLAG_LABEL.get(f['coverage_flag'], f['coverage_flag'])})"
            for m in ov["months_flagged"]
            for f in meta["month_coverage"]
            if f["month"] == m
        )
        or "none"
    )
    if "unavailable" in fc:
        fc_html = f"<p>Forecast not produced: {e(fc['unavailable'])}</p>"
    else:
        rows = "".join(
            f"<tr><td>{f['month']}</td><td>{_fmt(f['point'], 'BRL')}</td>"
            f"<td>{_fmt(f['lower_80'], 'BRL')} to {_fmt(f['upper_80'], 'BRL')}</td></tr>"
            for f in fc["forecast"]
        )
        verdict = (
            "the statistical model beat the best baseline"
            if fc["model_justified"]
            else f"the statistical model did NOT beat the {fc['best_baseline']} baseline, so the baseline is used"
        )
        fc_html = (
            f"<p><span class='tag'>forecast</span> Evaluated on {', '.join(fc['test_months'])}: {verdict}.</p>"
            f"<table><tr><th>Month</th><th>Point</th><th>Approx. 80% interval</th></tr>{rows}</table>"
        )
    generated = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>MERIDIAN Executive Report</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>body{{font-family:system-ui,Segoe UI,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem;color:#1f2937}}
h1{{margin-bottom:.2rem}}h2{{border-bottom:1px solid #e5e7eb;padding-bottom:.3rem;margin-top:2rem}}
table{{border-collapse:collapse;width:100%;font-size:.9rem}}td,th{{border-bottom:1px solid #e5e7eb;padding:.35rem;text-align:left}}
.note{{background:#fef3c7;padding:.6rem .8rem;border-radius:6px;font-size:.9rem}}.muted{{color:#6b7280;font-size:.85rem}}
.tag{{background:#ede9fe;color:#5b21b6;border-radius:4px;padding:0 .35rem;font-size:.75rem}}img{{max-width:100%}}</style></head>
<body><h1>MERIDIAN Executive Report</h1>
<p class="muted">Northstar Commerce (simulated) · Period {ov["period"]["start"]} to {ov["period"]["end"]} ·
Generated {generated} · Data loaded {meta["data_freshness_utc"] or "n/a"} (UTC) · Currency BRL</p>
<p class="note">Northstar is a simulated company; figures are derived from the public Olist dataset (CC BY-NC-SA 4.0).
"Revenue" here is a <b>proxy</b> (item value of delivered orders): not accounting revenue, not profit. Flagged months in
the period: {e(flagged)}.</p>
<h2>Key performance indicators</h2>
<table><tr><th>KPI</th><th>Current</th><th>Prior period</th><th>Change</th><th>Provenance</th></tr>{kpi_rows}</table>
{"" if ov["prior_period"]["comparable"] else f"<p class='muted'>{e(ov['prior_period']['note'])}</p>"}
<h2>Trend</h2><img alt="Monthly Delivered Merchandise Value; shaded months are low-coverage or incomplete"
src="data:image/png;base64,{_chart(ov["monthly"])}">
<h2>Observations (descriptive only)</h2><ul>{"".join(f"<li>{o}</li>" for o in observations)}</ul>
<p class="muted">These are measured differences, not explanations; no causal claim is made.</p>
<h2>Top categories</h2><table><tr><th>Category</th><th>Delivered Merchandise Value</th><th>Share</th>
<th>Orders</th></tr>{cats}</table><p class="muted">* fewer than 30 orders: small sample, interpret with care.</p>
<h2>Forecast</h2>{fc_html}
<h2>Data-quality warnings (latest load)</h2><ul>{dq or "<li>None</li>"}</ul>
<h2>Limitations</h2><ul><li>No cost, margin, marketing-spend or refund data exists: no profit, CAC or ROAS is reported.</li>
<li>Recent months are right-censored; 2016 months have low coverage.</li>
<li>Review scores: some orders share a review record (non-independent).</li>
<li>Timestamps are inferred São Paulo local time; ambiguous DST times are excluded from durations.</li></ul>
<h2>Suggested follow-up questions</h2><ul><li>Which categories and states drive late deliveries? (association analysis, not causation)</li>
<li>What would a measured experiment need to test a delivery-speed or pricing intervention?</li></ul>
</body></html>"""
    return doc, payloads
