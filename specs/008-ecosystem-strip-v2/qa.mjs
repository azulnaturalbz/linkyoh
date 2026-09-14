import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const require = createRequire(import.meta.url);
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/cristiansilva/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root = path.dirname(fileURLToPath(import.meta.url));
const out = path.join(root, 'evidence');
const base = 'http://127.0.0.1:8099';
const routes = JSON.parse(await readFile(path.join(out, 'routes.json'), 'utf8'));
const expected = ['Silvatech', 'Visit Belize', 'Chillbout', 'Linkyoh', 'MarketDay', 'WOP', 'Payments', 'Consulta', 'Belize Logistics', 'Games'];
const report = {checkedAt: new Date().toISOString(), base, productionWrites: false, views: [], keyboard: [], tracking: [], nojs: [], errors: [], blockedExternal: []};
const browser = await chromium.launch({headless: true});
await mkdir(out, {recursive: true});

async function makeContext(width, lang, nojs = false) {
  const context = await browser.newContext({viewport: {width, height: width < 700 ? 844 : 1000}, locale: lang, javaScriptEnabled: !nojs, serviceWorkers: 'block'});
  await context.route('**/*', route => {
    const url = new URL(route.request().url());
    if (url.origin === base) return route.continue();
    report.blockedExternal.push(url.origin + url.pathname);
    if (url.hostname === 'analytics.silvatech.bz') return route.fulfill({contentType: 'text/javascript', body: '/* QA: no external analytics */'});
    return route.abort();
  });
  return context;
}

async function inspect(page) {
  return page.locator('.svt-ecosystem-strip').evaluate(nav => {
    const rgb = value => (value.match(/[\d.]+/g) || []).map(Number);
    const lum = color => color.slice(0, 3).map(v => v / 255).map(v => v <= .04045 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4).reduce((n, v, i) => n + v * [.2126, .7152, .0722][i], 0);
    const bg = lum(rgb(getComputedStyle(nav).backgroundColor));
    const links = [...nav.querySelectorAll('a')].map(a => {
      const rect = a.getBoundingClientRect(), style = getComputedStyle(a);
      const fg = lum(rgb(style.color));
      const url = new URL(a.href);
      return {text: a.textContent.trim(), href: a.href, track: a.dataset.track, rel: a.rel, height: rect.height, left: rect.left, right: rect.right, contrast: (Math.max(bg, fg) + .05) / (Math.min(bg, fg) + .05), source: url.searchParams.get('utm_source'), medium: url.searchParams.get('utm_medium'), campaign: url.searchParams.get('utm_campaign')};
    });
    return {lang: document.documentElement.lang, version: nav.dataset.stripVersion, width: innerWidth, documentWidth: document.documentElement.scrollWidth, stripWidth: nav.getBoundingClientRect().width, stripScrollWidth: nav.scrollWidth, links};
  });
}

function verify(metrics, width, lang) {
  assert.equal(metrics.lang, lang);
  assert.equal(metrics.version, 'v2');
  assert.equal(metrics.documentWidth, width);
  assert.ok(metrics.stripScrollWidth <= metrics.stripWidth + 1);
  assert.deepEqual(metrics.links.map(x => x.text), expected);
  for (const link of metrics.links) {
    assert.equal(link.source, 'linkyoh');
    assert.equal(link.medium, 'ecosystem');
    assert.equal(link.campaign, 'strip');
    assert.equal(link.rel, 'noreferrer');
    assert.ok(link.height >= 44 && link.left >= 0 && link.right <= width + 1);
    assert.ok(link.contrast >= 4.5);
  }
}

try {
  for (const lang of ['en', 'es']) for (const width of [320, 390, 768, 944, 1440]) {
    const context = await makeContext(width, lang);
    const page = await context.newPage();
    page.on('pageerror', error => report.errors.push(error.message));
    for (const [name, route] of Object.entries(routes)) {
      const response = await page.goto(base + route + '?lang=' + lang);
      assert.equal(response.status(), 200);
      await page.evaluate(() => document.fonts.ready);
      const strip = page.locator('.svt-ecosystem-strip');
      await strip.scrollIntoViewIfNeeded();
      const metrics = await inspect(page);
      verify(metrics, width, lang);
      const label = `${name}-${lang}-${width}`;
      await strip.screenshot({path: path.join(out, label + '.png')});
      report.views.push({label, status: response.status(), ...metrics});
      if (name === 'home') {
        const links = strip.locator('a');
        await links.first().focus();
        for (let index = 0; index < expected.length; index++) {
          if (index) await page.keyboard.press('Tab');
          assert.equal(await page.evaluate(() => document.activeElement.textContent.trim()), expected[index]);
          const focused = await links.nth(index).evaluate(a => ({visible: a.matches(':focus-visible'), outline: getComputedStyle(a).outlineWidth}));
          assert.ok(focused.visible && parseFloat(focused.outline) >= 2);
        }
        report.keyboard.push({label, orderedLinks: expected.length, visibleFocus: true});
      }
    }
    await context.close();
  }

  for (const lang of ['en', 'es']) for (const width of [390, 1440]) {
    const context = await makeContext(width, lang, true);
    const page = await context.newPage();
    await page.goto(base + '/?lang=' + lang);
    const strip = page.locator('.svt-ecosystem-strip');
    await strip.scrollIntoViewIfNeeded();
    const metrics = await inspect(page);
    verify(metrics, width, lang);
    await strip.screenshot({path: path.join(out, `nojs-${lang}-${width}.png`)});
    let destination;
    await context.route('https://games.silvatech.bz/**', route => {
      destination = {url: route.request().url(), referer: route.request().headers().referer || null};
      return route.fulfill({contentType: 'text/html', body: '<title>Local QA destination stub</title>'});
    });
    await Promise.all([page.waitForURL('https://games.silvatech.bz/**'), strip.locator('a').last().click()]);
    assert.equal(destination.referer, null);
    assert.equal(new URL(destination.url).searchParams.get('utm_source'), 'linkyoh');
    report.nojs.push({lang, width, nativeNavigation: true, referrerOmitted: true});
    await context.close();
  }

  const context = await makeContext(390, 'en');
  const page = await context.newPage();
  await page.goto(base);
  await page.evaluate(() => {
    window.qaEvents = [];
    window.rybbit = {event: (name, data) => window.qaEvents.push({name, data})};
    document.addEventListener('click', event => {
      if (event.target.closest('.svt-ecosystem-strip a')) event.preventDefault();
    });
  });
  for (const name of ['chillbout_clickout', 'logistics_clickout', 'games_clickout']) {
    await page.locator(`.svt-ecosystem-strip [data-track="${name}"]`).click();
    const events = await page.evaluate(() => window.qaEvents.splice(0));
    assert.deepEqual(events, [{name, data: {source: 'linkyoh', placement: 'strip'}}]);
    report.tracking.push({name, dispatches: events.length, privacySafe: true});
  }
  await context.close();
  assert.deepEqual(report.errors, []);
  report.passed = true;
} catch (error) {
  report.passed = false;
  report.failure = error.stack;
  process.exitCode = 1;
} finally {
  report.blockedExternal = [...new Set(report.blockedExternal)];
  await writeFile(path.join(out, 'qa.json'), JSON.stringify(report, null, 2) + '\n');
  await browser.close();
  console.log(JSON.stringify({passed: report.passed, views: report.views.length, keyboard: report.keyboard.length, nojs: report.nojs.length, tracking: report.tracking.length, failure: report.failure}, null, 2));
}
