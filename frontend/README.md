# MERIDIAN frontend

React + TypeScript (Vite) dashboard for the MERIDIAN API. It shows real API data only; there is no mock data in the app.

```powershell
npm ci                # exact versions from package-lock.json
npm run dev           # http://localhost:5173, proxies /api to the FastAPI server on :8000
npm run lint; npm run typecheck; npm run test; npm run build
npm run e2e           # Playwright smoke: starts the API (read-only account) and the dev server on :5180
```

Production builds call `${VITE_API_BASE_URL}/api/v1` (empty = same origin).
