import { createRequire } from "node:module";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";

const require = createRequire(import.meta.url);
const { chromium } = require(
  process.env.PLAYWRIGHT_MODULE ||
    "/Users/cristiansilva/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright",
);
const root = path.dirname(fileURLToPath(import.meta.url));
const out = path.join(root, "evidence");
await mkdir(out, { recursive: true });
const base = process.env.PROTOTYPE_URL || "http://127.0.0.1:64064";
assert.equal(
  new URL(base).hostname,
  "127.0.0.1",
  "QA must use the loopback-only prototype",
);
const browser = await chromium.launch({ headless: true });
const report = {
  generatedAt: new Date().toISOString(),
  base,
  fixturesOnly: true,
  views: [],
  journeys: [],
  errors: [],
  externalRequests: [],
  contrastFailures: [],
};

async function inspect(page, label) {
  const metrics = await page.evaluate(() => {
    const visible = (e) =>
      !!e.getClientRects().length &&
      getComputedStyle(e).visibility !== "hidden";
    const rgb = (value) => (value.match(/[\d.]+/g) || []).map(Number);
    const blend = (front, back) => {
      const a = front[3] ?? 1;
      return [0, 1, 2].map((i) => front[i] * a + back[i] * (1 - a));
    };
    const background = (element) => {
      const chain = [];
      for (let e = element; e; e = e.parentElement) chain.unshift(e);
      return chain.reduce(
        (color, e) => blend(rgb(getComputedStyle(e).backgroundColor), color),
        [255, 255, 255],
      );
    };
    const luminance = (c) =>
      c
        .map((v) => v / 255)
        .map((v) => (v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4))
        .reduce((n, v, i) => n + v * [0.2126, 0.7152, 0.0722][i], 0);
    const contrasts = [];
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
    );
    while (walker.nextNode()) {
      const node = walker.currentNode,
        element = node.parentElement,
        text = node.textContent.trim();
      if (
        !text ||
        !element ||
        !visible(element) ||
        ["SCRIPT", "STYLE", "OPTION"].includes(element.tagName) ||
        element.closest("[hidden],.sr-only,svg")
      )
        continue;
      const style = getComputedStyle(element),
        size = parseFloat(style.fontSize);
      if (!size || style.opacity === "0" || element.closest(":disabled"))
        continue;
      const bg = background(element),
        fg = blend(rgb(style.color), bg),
        l1 = luminance(bg),
        l2 = luminance(fg);
      const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
      const large =
        size >= 24 || (size >= 18.66 && Number(style.fontWeight) >= 700);
      contrasts.push({
        text: text.slice(0, 70),
        ratio: Number(ratio.toFixed(2)),
        minimum: large ? 3 : 4.5,
      });
    }
    return {
      width: innerWidth,
      documentWidth: document.documentElement.scrollWidth,
      overflow: [...document.querySelectorAll("main *,header *")]
        .filter(
          (e) => visible(e) && e.getBoundingClientRect().right > innerWidth + 1,
        )
        .map((e) => e.tagName + "." + e.className)
        .slice(0, 10),
      brokenImages: [...document.images]
        .filter((i) => visible(i) && (!i.complete || !i.naturalWidth))
        .map((i) => i.src),
      bodyFont: getComputedStyle(document.body).fontFamily,
      headingFont: getComputedStyle(document.querySelector("h1")).fontFamily,
      icons: document.querySelectorAll("svg.lucide").length,
      checks: document.querySelectorAll("main .checked").length,
      contrastPairs: contrasts.length,
      minimumTextContrast: Math.min(...contrasts.map((c) => c.ratio)),
      contrastFailures: contrasts.filter((c) => c.ratio < c.minimum),
      ecosystem: [...document.querySelectorAll(".svt-ecosystem-strip a")].map(
        (a) => ({ url: a.href, track: a.dataset.track }),
      ),
      inactive: document.querySelectorAll(".svt-ecosystem-strip__inactive")
        .length,
    };
  });
  report.views.push({ label, ...metrics });
  assert.equal(
    metrics.documentWidth,
    metrics.width,
    `${label}: horizontal overflow`,
  );
  assert.deepEqual(metrics.overflow, [], `${label}: child overflow`);
  assert.deepEqual(metrics.brokenImages, [], `${label}: broken media`);
  assert.ok(metrics.icons > 10, `${label}: Lucide rendered`);
  assert.ok(metrics.checks > 0, `${label}: Checked region exists`);
  assert.equal(metrics.inactive, 2);
  assert.equal(metrics.ecosystem.length, 7);
  for (const link of metrics.ecosystem) {
    const url = new URL(link.url);
    assert.equal(url.searchParams.get("utm_source"), "linkyoh");
    assert.equal(url.searchParams.get("utm_medium"), "ecosystem");
    assert.equal(url.searchParams.get("utm_campaign"), "strip");
    assert.match(link.track, /_clickout$/);
  }
  report.contrastFailures.push(
    ...metrics.contrastFailures.map((f) => ({ label, ...f })),
  );
  return metrics;
}
try {
  for (const lang of ["en", "es"])
    for (const width of [390, 1440]) {
      const context = await browser.newContext({
        viewport: { width, height: width === 390 ? 844 : 1000 },
        deviceScaleFactor: 1,
        locale: lang,
      });
      await context.route("**/*", (route) => {
        const url = new URL(route.request().url());
        if (
          url.origin !== base &&
          !["data:", "about:"].includes(url.protocol)
        ) {
          report.externalRequests.push(url.href);
          return route.abort();
        }
        return route.continue();
      });
      const page = await context.newPage();
      page.on("pageerror", (e) => report.errors.push(String(e)));
      page.on("console", (msg) => {
        if (msg.type() === "error") report.errors.push(msg.text());
      });
      const loc = lang === "es" ? "/es" : "",
        q = lang === "es" ? "plomero en Cayo" : "plumber in Cayo";
      for (const [kind, url] of [
        ["home", `${loc}/index.html`],
        ["results", `${loc}/results.html?q=${encodeURIComponent(q)}`],
        ["provider", `${loc}/provider.html`],
      ]) {
        await page.goto(base + url, { waitUntil: "networkidle" });
        await page.evaluate(() => document.fonts.ready);
        const label = `${kind}-${lang}-${width}`;
        await inspect(page, label);
        await page.screenshot({
          path: path.join(out, `${label}.png`),
          fullPage: true,
        });
        await page.screenshot({
          path: path.join(out, `${label}-viewport.png`),
        });
      }
      await page.locator(".contact-panel:visible [data-open=quote]").click();
      await page
        .locator("#quote-form [name=need]")
        .fill("Fixture: repair kitchen tap");
      await page.locator("#quote-form [name=contact]").fill("0000000000");
      await page.locator("#quote-form button[type=submit]").click();
      assert.equal(
        await page.locator("#quote-review").isVisible(),
        false,
        "No review without consent",
      );
      await page.locator("#quote-form [name=consent]").check();
      await page.locator("#quote-form button[type=submit]").click();
      assert.equal(await page.locator("#quote-review").isVisible(), true);
      await page.screenshot({
        path: path.join(out, `quote-review-${lang}-${width}.png`),
      });
      await inspect(page, `quote-review-${lang}-${width}`);
      await page.locator("#edit-quote").click();
      assert.equal(
        await page.locator("#quote-form [name=need]").inputValue(),
        "Fixture: repair kitchen tap",
      );
      await page.locator("#quote-form button[type=submit]").click();
      await page.locator("#preview-lead").click();
      assert.equal(await page.locator("#quote-preview").isVisible(), true);
      await page.keyboard.press("Tab");
      assert.equal(await page.evaluate(() => document.activeElement.closest("dialog")?.id), "quote");
      await page.keyboard.press("Escape");
      await page.waitForFunction(
        () => document.querySelector("#quote-form [name=contact]").value === "",
      );
      assert.equal(
        await page.locator("#quote-form [name=contact]").inputValue(),
        "",
      );
      assert.equal(
        await page.locator("#quote-form [name=consent]").isChecked(),
        false,
      );
      report.journeys.push(
        `${lang}/${width}: quote consent, review/edit, unsent state, clear on close`,
      );
      await page.locator(".contact-panel:visible .secondary").hover();
      await inspect(page, `button-hover-${lang}-${width}`);
      await page.locator(".claim-block [data-open=pros]").click();
      await page.locator("[data-stage=claim]").click();
      await page.locator("#preview-claim").click();
      assert.equal(await page.locator("#claim-pending").isVisible(), true);
      await page.screenshot({
        path: path.join(out, `pros-claim-${lang}-${width}.png`),
      });
      await page.locator("[data-stage=verify]").click();
      await inspect(page, `pros-verify-${lang}-${width}`);
      await page.locator("[data-stage=verify]").press("ArrowRight");
      assert.equal(await page.locator("#stage-manage").isVisible(), true);
      await page.locator("#profile-preview button").click();
      assert.equal(await page.locator("#profile-saved").isVisible(), true);
      await page.locator("[data-manage=inbox]").click();
      await page.locator("#lead-toggle").click();
      assert.equal(await page.locator("#lead-detail").isVisible(), true);
      await inspect(page, `pros-inbox-${lang}-${width}`);
      await page.screenshot({
        path: path.join(out, `pros-inbox-${lang}-${width}.png`),
      });
      await page.keyboard.press("Escape");
      report.journeys.push(
        `${lang}/${width}: Pros claim/verify/manage/profile/inbox and keyboard tabs`,
      );
      if (width === 390) {
        await page.locator("#menu-toggle").click();
        assert.equal(await page.locator("#mobile-menu").isVisible(), true);
        await page.locator("#menu-toggle").click();
      assert.equal(await page.locator("#mobile-menu").isVisible(), false);
        report.journeys.push(`${lang}: mobile menu expands/collapses`);
      }
      await page.goto(
        `${base}${loc}/results.html?q=${encodeURIComponent(lang === "es" ? "carpintero en Belmopán" : "carpenter in Belmopan")}`,
        { waitUntil: "networkidle" },
      );
      assert.equal(await page.locator("#result-count").textContent(), "1");
      await page.locator(".language-switch a:not([aria-current])").click();
      await page.waitForLoadState("networkidle");
      assert.equal(await page.locator("#result-count").textContent(), "1");
      await page.goBack({ waitUntil: "networkidle" });
      assert.equal(await page.locator("#result-count").textContent(), "1");
      await page.goto(`${base}${loc}/results.html?q=unknown-service`, {
        waitUntil: "networkidle",
      });
      assert.equal(await page.locator("#empty-state").isVisible(), true);
      await page.screenshot({
        path: path.join(out, `empty-${lang}-${width}.png`),
      });
      await page.goto(
        `${base}${loc}/results.html?q=${encodeURIComponent(q + " tonight")}`,
        { waitUntil: "networkidle" },
      );
      assert.equal(await page.locator("#urgency").isVisible(), true);
      await page.locator(".filters summary").click();
      if (!(await page.locator("[name=district]").isVisible()))
        await page.locator(".filters summary").click();
      await page.locator("[name=district]").selectOption("Belize");
      assert.deepEqual(
        await page.locator("[name=town] option").allTextContents(),
        [
          lang === "es" ? "Todas las localidades" : "All towns",
          "Belize City",
          "Ladyville",
        ],
      );
      await page.locator("[name=town]").selectOption("Ladyville");
      await page.locator(".filter-apply").click();
      await page.waitForLoadState("networkidle");
      assert.equal(await page.locator("#result-count").textContent(), "0");
      assert.equal(new URL(page.url()).searchParams.get("town"), "Ladyville");
      await page.goto(`${base}${loc}/provider-pine.html`);
      await page.locator(".provider-photo").click();
      await page.locator('[data-photo="1"]').click();
      assert.equal(await page.locator("#photo-count").textContent(), "2 / 2");
      await page.keyboard.press("Escape");
      report.journeys.push(
        `${lang}/${width}: parsed search, language/back, no-match, urgency, dependent town filters, gallery`,
      );
      await page.locator(".claim-block [data-open=pros]").click();
      await page.locator("#preview-claim").click();
      assert.match(await page.locator("#claim-pending").textContent(), lang === "es" ? /pendiente de revisión/ : /pending review/);
      await inspect(page, `unclaimed-pros-${lang}-${width}`);
      await page.screenshot({ path: path.join(out, `pros-claim-${lang}-${width}.png`) });
      report.journeys.push(`${lang}/${width}: unclaimed maker retains pending claim review, unlike claimed provider`);
      await page.keyboard.press("Escape");
      assert.equal(await page.evaluate(() => localStorage.length), 0);
      await context.close();
    }
  for (const width of [320, 768, 944]) {
    const context = await browser.newContext({
      viewport: { width, height: 900 },
    });
    const page = await context.newPage();
    for (const route of [
      "/es/index.html",
      "/es/results.html",
      "/es/provider.html",
    ]) {
      await page.goto(base + route, { waitUntil: "networkidle" });
      await inspect(page, `extra-${width}-${route}`);
    }
    await context.close();
  }
  const nojs = await browser.newContext({
    javaScriptEnabled: false,
    viewport: { width: 390, height: 844 },
  });
  const page = await nojs.newPage();
  await page.goto(base + "/es/index.html");
  assert.match(await page.locator("h1").textContent(), /Qué necesitas/);
  await page.locator(".card-body h3 a").first().click();
  assert.equal(await page.locator("h1").textContent(), "Riverbend Plumbing");
  report.journeys.push(
    "No-JS static content and provider navigation; dynamic parsing explicitly not claimed",
  );
  await nojs.close();
  assert.deepEqual(report.errors, []);
  assert.deepEqual(report.externalRequests, []);
  assert.deepEqual(
    report.contrastFailures,
    [],
    "WCAG AA visible text contrast",
  );
  report.status = "PASS";
} catch (e) {
  report.status = "FAIL";
  report.failure = e.stack;
  process.exitCode = 1;
} finally {
  await browser.close();
  await writeFile(
    path.join(out, "qa-report.json"),
    JSON.stringify(report, null, 2) + "\n",
  );
  console.log(
    JSON.stringify(
      {
        status: report.status,
        views: report.views.length,
        journeys: report.journeys.length,
        errors: report.errors,
        externalRequests: report.externalRequests,
        contrastFailures: report.contrastFailures,
        failure: report.failure,
      },
      null,
      2,
    ),
  );
}
