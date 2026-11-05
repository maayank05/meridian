// Presentation formatting only (no business calculations).
// One locale everywhere (matches the HTML report): R$ with English separators, e.g. R$13,181,027.13.
const brl = new Intl.NumberFormat("en-US", { style: "currency", currency: "BRL", minimumFractionDigits: 2, maximumFractionDigits: 2 });
const brlCompact = new Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 });
const int = new Intl.NumberFormat("en");

export function formatValue(value: number | null | undefined, unit: string): string {
  if (value === null || value === undefined) return "n/a";
  if (unit === "BRL") return brl.format(value);
  if (unit === "%") return `${(value * 100).toFixed(2)}%`;
  return int.format(value);
}

export const formatBRL = (v: number | null | undefined) => formatValue(v, "BRL");
export const formatInt = (v: number | null | undefined) => formatValue(v, "count");
export const formatPct = (v: number | null | undefined, digits = 1) => (v === null || v === undefined ? "n/a" : `${(v * 100).toFixed(digits)}%`);
export const formatCompactBRL = (v: number) => `R$ ${brlCompact.format(v)}`;
export const formatChange = (v: number | null) => (v === null ? "—" : `${v > 0 ? "+" : ""}${(v * 100).toFixed(1)}%`);
export const monthLabel = (iso: string) => iso.slice(0, 7);
