import path from "node:path";
import { defineConfig, devices } from "@playwright/test";

// End-to-end smoke against the REAL API (read-only account, meridian_dev) and the Vite dev server.
// Run from frontend/: `npm run e2e`. The Python interpreter is the repository's .venv (Windows or POSIX layout).
const repoRoot = path.resolve(process.cwd(), "..");
const python = process.platform === "win32" ? path.join(repoRoot, ".venv", "Scripts", "python.exe") : path.join(repoRoot, ".venv", "bin", "python");
export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: { timeout: 15_000 }, // cold dev servers + real full-data API; latency is measured separately (NFR-003)
  workers: 2,
  retries: 0,
  reporter: [["list"]],
  use: { baseURL: "http://localhost:5180", viewport: { width: 1360, height: 900 }, trace: "off" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"], viewport: { width: 1360, height: 900 } } }],
  webServer: [
    {
      command: `"${python}" -m uvicorn meridian.api.main:app --host 127.0.0.1 --port 8000`,
      cwd: repoRoot,
      url: "http://127.0.0.1:8000/api/v1/ready",
      timeout: 60_000,
      reuseExistingServer: false,
    },
    { command: "npm run dev -- --port 5180 --strictPort", url: "http://localhost:5180", timeout: 60_000, reuseExistingServer: false },
  ],
});
