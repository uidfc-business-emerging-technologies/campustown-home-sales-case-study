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

module.exports = [
  {
    folder: "v2-six-questions",
    exercise: async (page) => [...(await detailsToggle(page)), ...(await chartTooltips(page))],
  },
];
