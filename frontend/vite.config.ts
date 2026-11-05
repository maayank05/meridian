/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev: /api is proxied to the local FastAPI server, so the browser never needs CORS for local work.
export default defineConfig({
  plugins: [react()],
  server: { port: 5173, proxy: { "/api": "http://127.0.0.1:8000" } },
  test: { environment: "jsdom", setupFiles: ["./src/test/setup.ts"], globals: false, css: false, include: ["src/**/*.test.{ts,tsx}"] },
});
