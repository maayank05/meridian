// Central API client. In development Vite proxies /api to the FastAPI server; in production set VITE_API_BASE_URL.
import type { ApiErrorBody } from "../types/api";

const BASE = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

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

async function request<T>(path: string, init?: RequestInit): Promise<T> {
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
  reportUrl: (p: Period) => `${BASE}/api/v1/reports/executive${q(p)}`,
};
