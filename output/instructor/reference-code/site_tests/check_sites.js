// Tests each reference site in a headless browser, served from a subfolder the way
// GitHub Pages serves a project site (https://user.github.io/repo-name/).
//
// Usage, from this folder, with Playwright installed:
//   node check_sites.js <base-url> <screenshot-folder> <text-folder>
// where <base-url> points at the folder holding the three site folders.
//
// For each site, at 375 px and 1280 px wide, in light and dark: loads the page,
// waits for the data, records console errors, failed requests and sideways
// scrolling, saves a full-page screenshot, and exercises every control.
// Writes each site's visible text (after its controls run) for the number checks.
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const [base, shots, texts] = process.argv.slice(2);
const SITES = require("./site_controls");

async function run() {
  fs.mkdirSync(shots, { recursive: true });
  fs.mkdirSync(texts, { recursive: true });
  const browser = await chromium.launch();
  const results = [];
  for (const site of SITES) {
    for (const width of [375, 1280]) {
      for (const scheme of ["light", "dark"]) {
        const context = await browser.newContext({ viewport: { width, height: 900 }, colorScheme: scheme });
        const page = await context.newPage();
        const problems = [];
        page.on("console", (m) => { if (m.type() === "error" || m.type() === "warning") problems.push(m.type() + ": " + m.text()); });
        page.on("pageerror", (e) => problems.push("page error: " + e.message));
        page.on("requestfailed", (r) => problems.push("failed request: " + r.url()));
        page.on("response", (r) => { if (r.status() >= 400) problems.push("HTTP " + r.status() + ": " + r.url()); });
        const url = base.replace(/\/$/, "") + "/" + site.folder + "/";
        await page.goto(url, { waitUntil: "networkidle" });
        await page.waitForFunction(() => !document.querySelector(".loading"), null, { timeout: 15000 }).catch(() => problems.push("still loading after 15 s"));
        await page.evaluate(() => document.fonts.ready);
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
        if (overflow > 0) problems.push("scrolls sideways by " + overflow + " px");
        const name = `${site.folder}-${width}-${scheme}`;
        await page.screenshot({ path: path.join(shots, name + ".png"), fullPage: true });
        const controls = await site.exercise(page).catch((e) => ["control check failed: " + e.message]);
        problems.push(...controls.filter((c) => c.startsWith("FAIL") || c.startsWith("control check failed")));
        const after = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
        if (after > 0) problems.push("scrolls sideways by " + after + " px after using the controls");
        if (width === 1280 && scheme === "light") {
          fs.writeFileSync(path.join(texts, site.folder + ".txt"), await page.evaluate(() => document.body.innerText));
          if (site.afterShot) await page.screenshot({ path: path.join(shots, `${site.folder}-controls-used.png`), fullPage: true });
        }
        results.push({ site: site.folder, width, scheme, problems, controls: controls.length });
        await context.close();
      }
    }
  }
  await browser.close();
  for (const r of results) {
    console.log(`${r.problems.length ? "FAIL" : "pass"}  ${r.site}  ${r.width}px  ${r.scheme}  (${r.controls} control checks)`);
    r.problems.forEach((p) => console.log("      " + p));
  }
  fs.writeFileSync(path.join(texts, "results.json"), JSON.stringify(results, null, 1));
  process.exit(results.some((r) => r.problems.length) ? 1 : 0);
}

run().catch((e) => { console.error(e); process.exit(1); });
