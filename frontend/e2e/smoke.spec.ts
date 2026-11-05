import { expect, test } from "@playwright/test";

const SHOTS = "../docs/screenshots";

test("overview shows real KPIs, honest comparison and forecast verdict", async ({ page }) => {
  await page.goto("/overview");
  await expect(page.getByRole("heading", { name: "Executive overview" })).toBeVisible();
  const k01 = page.getByLabel("Delivered Merchandise Value (Revenue Proxy)", { exact: true });
  await expect(k01).toContainText("R$");
  await expect(k01).not.toContainText("n/a");
  await expect(page.getByText("No comparable prior period").first()).toBeVisible();
  await expect(page.getByText(/did not beat the naive baseline/)).toBeVisible();
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: `${SHOTS}/overview.png`, fullPage: true });
});

test("comparable single month shows a computed change", async ({ page }) => {
  await page.goto("/overview?start=2018-03&end=2018-03");
  await expect(page.getByLabel("Delivered Merchandise Value (Revenue Proxy)", { exact: true })).toContainText(/[▲▼]/);
});

test("customers page shows repeat rate and cohorts", async ({ page }) => {
  await page.goto("/customers");
  await expect(page.getByText("People with 2+ delivered orders")).toBeVisible();
  await expect(page.locator("table.cohort tbody tr")).toHaveCount(20);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: `${SHOTS}/customers.png`, fullPage: true });
});

test("products and operations render categories and delivery", async ({ page }) => {
  await page.goto("/products-operations");
  await expect(page.getByText("Top 12 categories by Delivered Merchandise Value")).toBeVisible();
  await expect(page.getByText("On time (on or before estimate)")).toBeVisible();
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: `${SHOTS}/products-operations.png`, fullPage: true });
});

test("simulator compares scenarios and labels them", async ({ page }) => {
  await page.goto("/simulator");
  await page.getByRole("button", { name: "Compare scenarios" }).click();
  await expect(page.getByText(/Hypothetical estimate based on your assumptions/)).toBeVisible();
  await expect(page.getByRole("table", { name: "" }).first()).toBeVisible();
  await expect(page.getByRole("cell", { name: "downside" })).toBeVisible();
  await page.getByRole("button", { name: "Evaluate campaign" }).click();
  await expect(page.getByText("Incremental ROAS", { exact: true })).toBeVisible();
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: `${SHOTS}/simulator.png`, fullPage: true });
});

test("data quality lists the 9 source files and checks", async ({ page }) => {
  await page.goto("/data-quality");
  await expect(page.getByRole("heading", { name: /Latest load: run/ })).toBeVisible();
  await expect(page.getByRole("cell", { name: "olist_orders_dataset.csv" })).toBeVisible();
  await expect(page.getByText("Blocking checks must be 0")).toBeVisible();
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: `${SHOTS}/data-quality.png`, fullPage: true });
});

test("invalid period is refused and the report endpoint serves HTML", async ({ page }) => {
  await page.goto("/overview?start=2018-05&end=2017-01");
  await expect(page.getByText("Start month must not be after end month.")).toBeVisible();
  const report = await page.request.get("/api/v1/reports/executive?start_month=2017-01&end_month=2018-08");
  expect(report.status()).toBe(200);
  expect(await report.text()).toContain("not accounting revenue, not profit");
});
