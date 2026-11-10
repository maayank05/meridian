// Component/page tests. API responses are mocked HERE ONLY (tests); the production build always calls the real API.
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AsyncSection, ProvenanceBadge } from "../components/ui";
import { ApiError, api, staticPath } from "../services/api";
import { formatChange, formatPct, formatValue } from "../lib/format";
import { OverviewPage } from "../pages/OverviewPage";
import { App } from "../app/App";
import type { Overview } from "../types/api";

const OVERVIEW: Overview = {
  period: { start: "2017-01-01", end: "2018-08-31" },
  prior_period: { start: "2015-05-01", end: "2016-12-31", comparable: false, note: "Prior period is not fully covered." },
  months_flagged: [],
  kpis: [
    { id: "K01", name: "Delivered Merchandise Value (Revenue Proxy)", unit: "BRL", provenance: "derived", definition: "Item value of delivered orders.", value: 376.25, prior_value: 0, change: null },
    { id: "K12", name: "Cancellation rate", unit: "%", provenance: "derived", definition: "Canceled / placed.", value: 0.1, prior_value: null, change: null },
  ],
  monthly: [
    { month: "2017-03-01", coverage_flag: "default_window", delivered_merchandise_value: 250.5, orders_placed: 1, delivered_orders: 1, average_order_value: 250.5 },
  ],
};

afterEach(() => vi.restoreAllMocks());

describe("formatting (presentation only)", () => {
  it("formats values by unit and never invents numbers for null", () => {
    expect(formatValue(null, "BRL")).toBe("n/a");
    expect(formatValue(0.1234, "%")).toBe("12.34%");
    expect(formatValue(1234, "orders")).toBe("1,234");
    expect(formatChange(null)).toBe("—");
    expect(formatChange(0.05)).toBe("+5.0%");
    expect(formatPct(undefined)).toBe("n/a");
  });
});

describe("shared states", () => {
  it("shows loading, error with retry, and success", async () => {
    const retry = vi.fn();
    const { rerender } = render(<AsyncSection state={{ status: "loading", retry }}>{() => <p>done</p>}</AsyncSection>);
    expect(screen.getByRole("status")).toBeInTheDocument();
    rerender(<AsyncSection state={{ status: "error", error: new ApiError(503, "Database down", "abc123"), retry }}>{() => <p>done</p>}</AsyncSection>);
    expect(screen.getByRole("alert")).toHaveTextContent("Database down");
    expect(screen.getByText(/abc123/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Retry" }));
    expect(retry).toHaveBeenCalledOnce();
    rerender(<AsyncSection state={{ status: "success", data: 1, retry }}>{() => <p>done</p>}</AsyncSection>);
    expect(screen.getByText("done")).toBeInTheDocument();
  });

  it("labels provenance in words, not colour alone", () => {
    render(<ProvenanceBadge value="scenario_output" />);
    expect(screen.getByText("Scenario")).toBeInTheDocument();
  });
});

describe("api client", () => {
  it("parses the error envelope", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ error: { code: "invalid_input", message: "start must not be after end", request_id: "r1" } }), { status: 422 }),
    );
    await expect(api.overview({ start: "2018-01", end: "2017-01" })).rejects.toMatchObject({ status: 422, message: "start must not be after end", requestId: "r1" });
  });

  it("maps API paths to static snapshot files", () => {
    expect(staticPath("/overview?start_month=2017-01&end_month=2018-08")).toBe("/snapshot/overview/2017-01_2018-08.json");
    expect(staticPath("/metadata")).toBe("/snapshot/metadata.json");
  });

  it("reports an unreachable backend", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("fetch failed"));
    await expect(api.quality()).rejects.toMatchObject({ status: 0 });
  });
});

describe("overview page", () => {
  beforeEach(() => {
    vi.spyOn(api, "forecast").mockRejectedValue(new ApiError(422, "series too short"));
  });

  it("renders KPIs and does not show a change when the prior period is not comparable", async () => {
    vi.spyOn(api, "overview").mockResolvedValue(OVERVIEW);
    render(<OverviewPage period={{ start: "2017-01", end: "2018-08" }} />);
    expect(await screen.findByText("Prior period is not fully covered.")).toBeInTheDocument();
    expect(screen.getAllByText("No comparable prior period")).toHaveLength(2);
    expect(screen.getByLabelText("Delivered Merchandise Value (Revenue Proxy)")).toHaveTextContent("376.25");
    expect(await screen.findByText("series too short")).toBeInTheDocument(); // forecast error state, not a fake forecast
  });

  it("shows an empty state instead of a chart when there are no months", async () => {
    vi.spyOn(api, "overview").mockResolvedValue({ ...OVERVIEW, monthly: [] });
    render(<OverviewPage period={{ start: "2017-01", end: "2018-08" }} />);
    expect(await screen.findByText("No months in this period.")).toBeInTheDocument();
  });
});

describe("app shell", () => {
  it("refuses an invalid period without calling the analytics endpoints", async () => {
    vi.spyOn(api, "metadata").mockRejectedValue(new ApiError(0, "offline"));
    const overview = vi.spyOn(api, "overview");
    render(
      <MemoryRouter initialEntries={["/overview?start=2018-05&end=2017-01"]}>
        <App />
      </MemoryRouter>,
    );
    expect(await screen.findByText("Start month must not be after end month.")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText(/Metadata unavailable/)).toBeInTheDocument());
    expect(overview).not.toHaveBeenCalled();
  });
});
