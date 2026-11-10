// Central API client. In development Vite proxies /api to the FastAPI server; in production set VITE_API_BASE_URL.
// `vite build --mode static` builds the hosted demo, which reads a pre-exported snapshot instead of the API (D-024).
import type { ApiErrorBody, Manifest, PresetId } from "../types/api";

const BASE = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
export const STATIC_SNAPSHOT = import.meta.env.MODE === "static";
const SNAPSHOT = `${import.meta.env.BASE_URL}snapshot`;

export class ApiError extends Error {
  readonly status: number;
  readonly requestId: string | null;
  readonly details: { field: string; message: string }[];

  constructor(status: number, message: string, requestId: string | null = null, details: { field: string; message: string }[] = []) {
    super(message);
    this.status = status;
    this.requestId = requestId;
    this.details = details;
  }
}

/** Snapshot file for a GET path; the stem matches scripts/export_static_snapshot.py (snapshot_name). */
export function staticPath(path: string): string {
  const [route, query = ""] = path.split("?");
  const params = new URLSearchParams(query);
  const start = params.get("start_month");
  const end = params.get("end_month");
  return start && end ? `${SNAPSHOT}${route}/${start}_${end}.json` : `${SNAPSHOT}${route}.json`;
}

async function readSnapshot<T>(file: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(file);
  } catch {
    throw new ApiError(0, "The demo data could not be loaded. Check your connection and try again.");
  }
  if (!response.ok) throw new ApiError(response.status, "This view is not part of the demo snapshot.");
  const body = (await response.json()) as T | ApiErrorBody;
  if (body && typeof body === "object" && "error" in body && Object.keys(body).length === 1) {
    const err = (body as ApiErrorBody).error;
    throw new ApiError(422, err.message, err.request_id ?? null, err.details ?? []);
  }
  return body as T;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  if (STATIC_SNAPSHOT) return readSnapshot<T>(staticPath(path));
  let response: Response;
  try {
    response = await fetch(`${BASE}/api/v1${path}`, { ...init, headers: { "Content-Type": "application/json", ...init?.headers } });
  } catch {
    throw new ApiError(0, "The API could not be reached. Is the backend running?");
  }
  if (!response.ok) {
    let body: ApiErrorBody | null = null;
    try {
      body = (await response.json()) as ApiErrorBody;
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(response.status, body?.error.message ?? `Request failed (${response.status})`, body?.error.request_id ?? null, body?.error.details ?? []);
  }
  return (await response.json()) as T;
}

export interface Period {
  start: string; // YYYY-MM
  end: string; // YYYY-MM
}

const q = (p: Period) => `?start_month=${encodeURIComponent(p.start)}&end_month=${encodeURIComponent(p.end)}`;

export const api = {
  metadata: () => request<import("../types/api").Metadata>("/metadata"),
  overview: (p: Period) => request<import("../types/api").Overview>(`/overview${q(p)}`),
  customers: (p: Period) => request<import("../types/api").Customers>(`/customers${q(p)}`),
  products: (p: Period) => request<import("../types/api").Products>(`/products${q(p)}`),
  operations: (p: Period) => request<import("../types/api").Operations>(`/operations${q(p)}`),
  quality: () => request<import("../types/api").Quality>("/quality"),
  forecast: () => request<import("../types/api").Forecast>("/forecast"),
  simulate: (body: Record<string, string | number>) =>
    request<import("../types/api").Simulation>("/simulator/compare", { method: "POST", body: JSON.stringify(body) }),
  campaign: (body: Record<string, string | number>) =>
    request<import("../types/api").Campaign>("/simulator/campaign", { method: "POST", body: JSON.stringify(body) }),
  reportUrl: (p: Period) =>
    STATIC_SNAPSHOT ? `${SNAPSHOT}/reports/${p.start}_${p.end}.html` : `${BASE}/api/v1/reports/executive${q(p)}`,
  // Static demo only: pre-computed results for the named synthetic presets (meridian.analytics.presets).
  manifest: () => readSnapshot<Manifest>(`${SNAPSHOT}/manifest.json`),
  simulatePreset: (preset: PresetId, p: Period) =>
    readSnapshot<import("../types/api").Simulation>(`${SNAPSHOT}/simulator/${preset}/${p.start}_${p.end}.json`),
  campaignPreset: (preset: PresetId) => readSnapshot<import("../types/api").Campaign>(`${SNAPSHOT}/campaign/${preset}.json`),
};
