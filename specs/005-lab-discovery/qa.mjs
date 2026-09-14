import { createRequire } from "node:module";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "/Users/cristiansilva/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");
const root = path.dirname(fileURLToPath(import.meta.url));
const out = path.join(root, "evidence");
await mkdir(out, { recursive: true });
const base = "http://127.0.0.1:8097";
const routes = JSON.parse(await readFile(path.join(out, "routes.json"), "utf8"));
const browser = await chromium.launch({headless:true});
const report = {generatedAt:new Date().toISOString(), base, fixturesOnly:true, views:[], journeys:[], errors:[], externalRequests:[], contrastFailures:[]};
async function context(options={}) {
  const ctx=await browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:1,...options});
  await ctx.route("**/*",async route=>{
    const url=new URL(route.request().url());
    if(url.origin===base) return route.continue();
    if(url.hostname==="analytics.silvatech.bz") return route.fulfill({contentType:"text/javascript",body:"/* QA: analytics suppressed */"});
    if(url.hostname==="api.qrserver.com") return route.fulfill({contentType:"image/png",body:Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=","base64")});
    report.externalRequests.push(url.href); return route.abort();
  });
  return ctx;
}
async function ready(page,url) {
  const response=await page.goto(url);
  assert.equal(response.status(),200,url);
  await page.evaluate(()=>document.fonts.ready);
  await page.waitForLoadState("networkidle");
}
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
  if (!label.includes("nojs")) assert.ok(metrics.icons > 3, `${label}: Lucide rendered`);
  if (!label.includes("empty")) assert.ok(metrics.checks > 0, `${label}: Checked region exists`);
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
  for(const lang of ["en","es"]) for(const width of [320,390,768,944,1440]) {
    const ctx=await context({viewport:{width,height:width<700?844:1000},locale:lang});
    const page=await ctx.newPage();
    page.on("pageerror",e=>report.errors.push(String(e)));
    for(const name of ["home","results","provider","gig","category","subcategory"]) {
      const label=name+"-"+lang+"-"+width;
      await ready(page,base+routes[name]+"?lang="+lang);
      await page.screenshot({path:path.join(out,label+".png"),fullPage:true});
      await page.screenshot({path:path.join(out,label+"-viewport.png")});
      await inspect(page,label);
      assert.equal(await page.locator('html').getAttribute('lang'),lang);
      assert.equal(await page.locator('[data-wop-key]').count(),0);
      assert.equal(await page.locator('link[rel=canonical]').count(),1);
      assert.equal(await page.locator('meta[property="og:image"]').count(),1);
      const cards=await page.locator('.provider-card').count();
      assert.equal(await page.locator('.provider-card [data-checked]').count(),cards);
    }
    await ctx.close();
  }
  for(const lang of ["en","es"]) {
    for(const nojs of [false,true]) {
      const ctx=await context({javaScriptEnabled:!nojs,locale:lang});
      const page=await ctx.newPage();
      const label=(nojs?"nojs":"js")+"-"+lang;
      await ready(page,base+"/?lang="+lang);
      await page.locator("#need").fill(lang==="es"?"Necesito un plomero en Cayo esta noche":"I need a plumber in Cayo tonight");
      await page.locator('.search-input button').click();
      await page.waitForURL("**/search/**");
      assert.equal(await page.locator(".provider-card").count(),1);
      await page.getByText(lang==="es"?"¿Lo necesitas esta noche?":"Need someone tonight?",{exact:false}).waitFor();
      await inspect(page,label);
      await page.screenshot({path:path.join(out,label+".png"),fullPage:true});
      await page.locator(".provider-card h3 a").click();
      await page.waitForURL("**/belize/**");
      assert.equal(await page.locator("html").getAttribute("lang"),lang);
      await page.locator('.language-switch a[lang="'+(lang==="es"?"en":"es")+'"]').click();
      assert.equal(await page.locator("html").getAttribute("lang"),lang==="es"?"en":"es");
      report.journeys.push(label+": real GET parsing -> one result -> detail -> locale");
      await ctx.close();
    }
    const ctx=await context({locale:lang});const page=await ctx.newPage();
    await ready(page,base+"/search/?q=plumber+in+Cayo+unicorn&lang="+lang);
    assert.equal(await page.locator(".provider-card").count(),0);
    await inspect(page,"empty-"+lang);
    await page.screenshot({path:path.join(out,"empty-"+lang+".png"),fullPage:true});
    await ready(page,base+"/?lang="+lang);
    await page.keyboard.press("Tab");
    assert.equal(await page.evaluate(()=>document.activeElement.className),"skip-link");
    await page.keyboard.press("Enter");
    await page.locator(".mobile-navigation summary").focus();
    await page.keyboard.press("Enter"); assert.equal(await page.locator(".mobile-navigation").getAttribute("open"),"");
    await page.keyboard.press("Escape"); assert.equal(await page.locator(".mobile-navigation").getAttribute("open"),null);
    await page.locator(".filters > summary").focus(); await page.keyboard.press("Enter");
    assert.equal(await page.locator(".filters").getAttribute("open"),"");
    await page.keyboard.press("Enter"); assert.equal(await page.locator(".filters").getAttribute("open"),null);
    await page.locator('.mobile-dock a[href$="#categories"]').focus();
    await page.keyboard.press("Enter");
    await page.waitForURL("**#categories");
    const categoryLink=page.locator('.category-shortcuts a').first();
    await categoryLink.focus(); await page.keyboard.press("Enter");
    await page.waitForURL("**/belize/services/**");
    assert.ok(await page.locator('.provider-card [data-checked]').count()>0);
    await page.locator('.mobile-dock a').nth(1).click();
    await page.waitForURL("**/search/**");
    report.journeys.push(lang+": keyboard skip/menu open/Escape focus/filters toggle");
    report.journeys.push(lang+": keyboard category shortcut -> canonical list -> mobile dock search");
    await ctx.close();
  }
  assert.deepEqual(report.errors,[]);
  assert.deepEqual(report.externalRequests,[]);
  assert.deepEqual(report.contrastFailures,[]);
  report.status="passed";
} catch(e) {report.status="failed";report.failure=String(e);process.exitCode=1;}
finally {
  await writeFile(path.join(out,"qa-report.json"),JSON.stringify(report,null,2)+"\n");
  await browser.close();
}
console.log(JSON.stringify({status:report.status,views:report.views.length,journeys:report.journeys, failure:report.failure,contrastFailures:report.contrastFailures.slice(0,10)},null,2));
