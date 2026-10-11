// The controls on each reference site, and how to check that each one works.
// Each exercise() returns a list of lines; a line starting with FAIL fails the test.

// Every collapsible table opens and closes from the keyboard.
async function detailsToggle(page) {
  const out = [];
  const count = await page.locator("details > summary").count();
  for (let i = 0; i < count; i++) {
    const summary = page.locator("details > summary").nth(i);
    const before = await summary.evaluate((s) => s.parentElement.open);
    await summary.focus();
    await page.keyboard.press("Enter");
    const after = await summary.evaluate((s) => s.parentElement.open);
    await page.keyboard.press("Enter");
    out.push((after !== before ? "ok" : "FAIL") + ": table toggle " + (i + 1));
  }
  return out;
}

// Chart marks take keyboard focus and show a tooltip.
async function chartTooltips(page) {
  const out = [];
  await page.mouse.move(0, 0);  // a resting pointer over a chart would fire its own hover events
  const marks = page.locator("svg .hit");
  const count = await marks.count();
  if (!count) return ["FAIL: no focusable chart marks"];
  for (const i of [0, Math.floor(count / 2), count - 1]) {
    await marks.nth(i).focus();
    const shown = await page.evaluate(() => { const t = document.querySelector(".tip"); return !!t && !t.hidden && t.textContent.length > 0; });
    out.push((shown ? "ok" : "FAIL") + ": tooltip on chart mark " + i);
  }
  await page.keyboard.press("Tab");
  return out;
}

const fs = require("fs");
const path = require("path");

const text = (page, id) => page.locator("#" + id).innerText();

// V1: every option in the picker changes the headline numbers, and a bar in the
// new-homes chart picks its area from the keyboard.
async function v1Controls(page) {
  const out = [];
  const options = await page.locator("#area option").evaluateAll((os) => os.map((o) => o.value));
  const seen = new Set();
  for (const value of options) {
    await page.selectOption("#area", value);
    const stats = [await text(page, "s1-d"), await text(page, "s2-d"), await text(page, "s3-d")].join(" | ");
    const ok = !stats.includes("...") && !seen.has(stats);
    seen.add(stats);
    out.push((ok ? "ok" : "FAIL") + ": picker " + value);
  }
  const bar = page.locator("#c3 .pickable").nth(2);
  const label = (await bar.getAttribute("aria-label")).split(":")[0];
  await bar.focus();
  await page.keyboard.press("Enter");
  const chosen = await page.locator("#area").inputValue();
  out.push((chosen === label ? "ok" : "FAIL") + ": bar picks " + label + " (picker shows " + chosen + ")");
  await page.selectOption("#area", options[0]);
  return out;
}

// V3: the campus, budget and distance controls change the headline numbers. The values
// shown at several settings are saved, so check_numbers.py can compare them with Python.
const V3_SETTINGS = [
  { campus: "Illinois", budget: 400000, dist: 3 },
  { campus: "Penn State", budget: 300000, dist: 1 },
  { campus: "UC Davis", budget: 900000, dist: 5 },
  { campus: "Virginia", budget: 550000, dist: 10 },
  { campus: "Michigan", budget: 150000, dist: 1 },
];
async function v3Controls(page, texts) {
  const out = [], shown = [];
  for (const s of V3_SETTINGS) {
    const value = await page.locator("#campus option", { hasText: s.campus }).first().getAttribute("value");
    await page.selectOption("#campus", value);
    await page.locator("#budget").evaluate((el, v) => { el.value = String(v); el.dispatchEvent(new Event("input", { bubbles: true })); }, s.budget);
    await page.locator('label[for="d' + s.dist + '"]').click();
    const row = { ...s, share: await text(page, "s1-v"), counts: await text(page, "s1-d"), sqft: await text(page, "s2-v"), dom: await text(page, "s3-v"),
      budgetShown: await text(page, "budget-out") };
    shown.push(row);
    out.push((row.share !== "..." ? "ok" : "FAIL") + ": settings " + s.campus + " " + s.budget + " " + s.dist);
  }
  const bar = page.locator("#bars .pickable").nth(0);
  const label = (await bar.getAttribute("aria-label")).split(":")[0];
  await bar.focus();
  await page.keyboard.press("Enter");
  const picked = await page.locator("#campus option:checked").innerText();
  out.push((picked.startsWith(label) ? "ok" : "FAIL") + ": bar picks " + label);
  if (texts) fs.writeFileSync(path.join(texts, "v3-settings.json"), JSON.stringify(shown, null, 1));
  return out;
}

module.exports = [
  {
    folder: "v1-old-homes-close-in",
    afterShot: true,
    reset: (page) => page.selectOption("#area", "All campus areas"),
    exercise: async (page) => [...(await v1Controls(page)), ...(await chartTooltips(page))],
  },
  {
    folder: "v2-six-questions",
    exercise: async (page) => [...(await detailsToggle(page)), ...(await chartTooltips(page))],
  },
  {
    folder: "v3-close-to-campus",
    afterShot: true,
    exercise: async (page, texts) => [...(await v3Controls(page, texts)), ...(await chartTooltips(page))],
  },
];
