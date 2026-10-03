import {createRequire} from 'node:module';
import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {execFileSync} from 'node:child_process';

const require = createRequire(import.meta.url);
const {chromium} = require('/Users/cristiansilva/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const here = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(here, '../../..');
const arg = (name, fallback) => process.argv.includes(name) ? process.argv[process.argv.indexOf(name) + 1] : fallback;
const candidate = process.argv.includes('--candidate');
const out = path.resolve(arg('--output', here));
if (candidate && out === here) throw new Error('Candidate evidence must not overwrite the baseline');
const base = arg('--base', 'https://linkyoh.com');
const local = new URL(base).hostname === '127.0.0.1';
const routes = {home: '/', provider: arg('--provider', '/belize/providers/linkyoh-ai-admin-218/')};
const localeHosts = ['visitbelize.silvatech.bz', 'linkyoh.com', 'wop.silvatech.bz', 'consulta.silvatech.bz', 'belizelogistics.com'];
const expected = [
  ['Silvatech', 'silvatech.bz', 'hub_clickout'],
  ['Visit Belize', 'visitbelize.silvatech.bz', 'visitbelize_clickout'],
  ['Chillbout', 'chillbout.com', 'chillbout_clickout'],
  ['Linkyoh', 'linkyoh.com', 'linkyoh_clickout'],
  ['MarketDay', 'marketday.silvatech.bz', 'marketday_clickout'],
  ['WOP', 'wop.silvatech.bz', 'wop_clickout'],
  ['Payments', 'payments.silvatech.bz', 'payments_clickout'],
  ['Consulta', 'consulta.silvatech.bz', 'consulta_clickout'],
  ['Belize Logistics', 'belizelogistics.com', 'logistics_clickout'],
  ['Games', 'games.silvatech.bz', 'games_clickout'],
];
const report = {started: new Date().toISOString(), source: candidate ? 'candidate' : '60d5af7', repoHead: execFileSync(process.env.GIT_BINARY || '/usr/bin/git', ['rev-parse', 'HEAD'], {cwd: repo}).toString().trim(), base, candidate,
  references: [], destinations: [], views: [], keyboard: [], nojs: [], localeRouting: [],
  errors: [], blockedWrites: [], realAnalyticsSent: false, productionMutation: false};
const check = (condition, message) => {if (!condition) throw new Error(message);};
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const get = async url => {
  const response = await fetch(url, {signal: AbortSignal.timeout(30000)});
  const body = Buffer.from(await response.arrayBuffer());
  return {url, finalUrl: response.url, status: response.status, body, sha256: hash(body)};
};
await mkdir(out, {recursive: true});
const browser = await chromium.launch({headless: true});
async function context(width, nojs = false) {
  const ctx = await browser.newContext({viewport: {width, height: 900}, javaScriptEnabled: !nojs});
  await ctx.route('**/*', route => {
    const request = route.request(), url = new URL(request.url());
    if (!['GET', 'HEAD'].includes(request.method())) {
      report.blockedWrites.push(url.origin + url.pathname);
      return route.abort();
    }
    if (url.hostname === 'analytics.silvatech.bz') {
      return route.fulfill({contentType: 'text/javascript', body: '/* QA: analytics suppressed */'});
    }
    if ([new URL(base).hostname, 'linkyoh.com', 'www.linkyoh.com', 'linkyoh-prd-assets-944327601374-us-east-1.s3.amazonaws.com', 'api.qrserver.com'].includes(url.hostname)) return route.continue();
    return route.abort();
  });
  return ctx;
}
function validateLinks(links, source, lang = 'en', localized = candidate) {
  check(links.length === expected.length, 'Expected ten links');
  links.forEach((link, i) => {
    const url = new URL(link.href), [name, host, track] = expected[i];
    const pathname = localized && host === 'silvatech.bz' && lang === 'es' ? '/es/' : '/';
    check(link.name === name && url.hostname === host && url.protocol === 'https:' && url.pathname === pathname, 'Destination/order mismatch: ' + name);
    check(link.track === track, 'Event mismatch: ' + name);
    check(url.searchParams.get('utm_source') === source && url.searchParams.get('utm_medium') === 'ecosystem' && url.searchParams.get('utm_campaign') === 'strip', 'Attribution mismatch: ' + name);
    if (localized) check(url.searchParams.get('lang') === (localeHosts.includes(host) ? lang : null), 'Locale mismatch: ' + name);
  });
}
try {
  const reference = await get('https://silvatech.bz/brand/ecosystem-strip.html');
  check(reference.status === 200, 'Hub reference unavailable');
  const parser = await browser.newPage();
  const links = await parser.evaluate(html => {
    const doc = new DOMParser().parseFromString(html, 'text/html');
    return [...doc.querySelectorAll('.svt-ecosystem-strip a')].map(a => ({name: a.textContent.trim(), href: a.href, track: a.dataset.track}));
  }, reference.body.toString());
  validateLinks(links, 'hub', 'en', false);
  await parser.close();
  report.references.push({url: reference.url, status: reference.status, sha256: reference.sha256, navMatches: true});
  for (const [url, file] of [
    ['https://silvatech.bz/brand/silvatech-ui.css', 'static/lab/assets/silvatech-ui.css'],
    [base + '/static/lab/assets/silvatech-ui.css', 'static/lab/assets/silvatech-ui.css'],
    [base + '/static/css/ecosystem-strip.css', 'static/css/ecosystem-strip.css'],
    [base + '/static/js/ecosystem-tracking.js', 'static/js/ecosystem-tracking.js'],
  ]) {
    const result = await get(url), matches = result.body.equals(await readFile(path.join(repo, file)));
    report.references.push({url, status: result.status, sha256: result.sha256, matches});
    check(result.status === 200 && matches, 'Source bytes differ: ' + url);
  }
  for (const [, host] of expected) {
    for (const attributed of [false, true]) {
      const url = `https://${host}/` + (attributed ? '?utm_source=linkyoh&utm_medium=ecosystem&utm_campaign=strip' : '');
      const result = await get(url);
      report.destinations.push({url, status: result.status, finalUrl: result.finalUrl});
      check(result.status === 200 && new URL(result.finalUrl).hostname === host, 'Destination failed: ' + url);
    }
  }
  for (const lang of ['en', 'es']) for (const width of candidate ? [320, 390, 768, 944, 1440] : [320, 390, 1440]) {
    const ctx = await context(width), page = await ctx.newPage();
    page.on('pageerror', error => report.errors.push(error.message));
    for (const [name, route] of Object.entries(routes)) {
      const response = await page.goto(base + route + '?lang=' + lang, {waitUntil: 'networkidle'});
      await page.evaluate(() => document.fonts.ready);
      const metrics = await page.evaluate(() => {
        const nav = document.querySelector('.svt-ecosystem-strip');
        const forward = document.querySelector('.forward');
        const link = forward?.querySelector('a');
        return {lang: document.documentElement.lang, width: innerWidth, documentWidth: document.documentElement.scrollWidth,
          version: nav?.dataset.stripVersion, stripWidth: nav?.getBoundingClientRect().width,
          links: [...nav.querySelectorAll('a')].map(a => ({name: a.textContent.trim(), href: a.href, track: a.dataset.track,
            rel: a.rel, height: a.getBoundingClientRect().height})),
          forward: {text: forward?.textContent.trim().replace(/\s+/g, ' '), href: link?.href, track: link?.dataset.track, rel: link?.rel},
          canonical: document.querySelector('link[rel=canonical]')?.href};
      });
      const label = `${name}-${lang}-${width}`;
      report.views.push({label, status: response.status(), ...metrics});
      check(response.status() === 200 && metrics.lang === lang, label + ': status/locale');
      check(metrics.width === metrics.documentWidth && metrics.stripWidth <= width, label + ': overflow');
      check(metrics.version === 'v2', label + ': version');
      validateLinks(metrics.links, 'linkyoh', lang);
      check(metrics.links.every(link => link.rel.includes('noreferrer') && link.height >= 44), label + ': target/referrer');
      const forward = new URL(metrics.forward.href);
      check(forward.hostname === 'marketday.silvatech.bz' && forward.searchParams.get('utm_source') === 'linkyoh' && forward.searchParams.get('utm_medium') === 'ecosystem' && forward.searchParams.get('utm_campaign') === 'forward' && metrics.forward.track === 'marketday_clickout', label + ': forward contract');
      check(metrics.forward.text === (lang === 'en' ? 'Sell what you make. Open your own store on MarketDay' : 'Vende lo que creas. Abre tu propia tienda en MarketDay'), label + ': banner copy');
      check(metrics.canonical === 'https://linkyoh.com' + route, label + ': canonical');
      await page.screenshot({path: path.join(out, label + '.png')});
      await page.locator('.svt-ecosystem-strip').screenshot({path: path.join(out, label + '-strip.png')});
      await page.locator('.forward').screenshot({path: path.join(out, label + '-forward.png')});
      console.log(label, 'PASS');
    }
    await ctx.close();
  }
  // Navigation is intercepted after the real keyboard click; dispatch stays on the live source page.
  for (const lang of ['en', 'es']) {
    const ctx = await context(390), page = await ctx.newPage(), events = [];
    await page.exposeBinding('qaEvent', (_, event, properties) => events.push({event, properties}));
    await page.addInitScript(() => {window.rybbit = {event: (event, properties) => window.qaEvent(event, properties)};});
    for (const [name, route] of Object.entries(routes)) {
      const selectors = name === 'home' ? expected.map((_, i) => `.svt-ecosystem-strip a >> nth=${i}`) : [];
      selectors.push('.forward a');
      if (candidate) selectors.push('.legal a[data-track="hub_clickout"]');
      for (const selector of selectors) {
        await page.goto(base + route + '?lang=' + lang, {waitUntil: 'networkidle'});
        events.length = 0;
        const anchor = page.locator(selector), href = new URL(await anchor.getAttribute('href')).href, event = await anchor.getAttribute('data-track');
        let navigation;
        const handler = async intercepted => {
          navigation = {url: intercepted.request().url(), method: intercepted.request().method(), referer: intercepted.request().headers().referer || null};
          await intercepted.fulfill({contentType: 'text/html', body: '<!doctype html><title>Navigation receipt only</title>'});
        };
        await page.route(href, handler);
        await anchor.focus();
        const focus = await anchor.evaluate(a => ({focused: a === document.activeElement, outline: getComputedStyle(a).outlineWidth}));
        await page.keyboard.press('Enter');
        await page.waitForURL(href);
        await page.waitForTimeout(100);
        await page.unroute(href, handler);
        const placement = new URL(href).searchParams.get('utm_campaign');
        check(focus.focused && parseFloat(focus.outline) > 0, 'Missing keyboard focus');
        check(navigation?.method === 'GET' && !navigation.referer, 'Navigation/referrer failed');
        check(events.length === 1 && events[0].event === event && JSON.stringify(events[0].properties) === JSON.stringify({source: 'linkyoh', placement}), 'Not exactly one bounded dispatch');
        report.keyboard.push({lang, page: name, selector, href, focus, navigation, events: [...events]});
      }
    }
    await ctx.close();
  }
  for (const lang of ['en', 'es']) {
    const ctx = await context(390, true), page = await ctx.newPage();
    await page.goto(base + '/?lang=' + lang, {waitUntil: 'networkidle'});
    const links = await page.locator('.svt-ecosystem-strip a').count();
    await page.locator('.mobile-navigation > summary').focus();
    await page.keyboard.press('Enter');
    check(await page.locator('.mobile-navigation').getAttribute('open') !== null, 'No-JS menu failed to open');
    await page.keyboard.press('Enter');
    check(await page.locator('.mobile-navigation').getAttribute('open') === null, 'No-JS menu failed to close');
    const self = page.locator('.svt-ecosystem-strip a[data-track="linkyoh_clickout"]');
    if (local) {
      const target = new URL(await self.getAttribute('href'));
      await page.route(target.href, async route => {
        const response = await fetch(base + target.pathname + target.search);
        await route.fulfill({contentType: 'text/html', body: await response.text()});
      });
    }
    await self.focus();
    await page.keyboard.press('Enter');
    await page.waitForURL(url => url.searchParams.get('utm_campaign') === 'strip');
    const finalLang = await page.locator('html').getAttribute('lang');
    if (candidate) check(finalLang === lang, 'Self-link lost locale');
    report.nojs.push({lang, links, menu: 'opens and closes', nativeNavigation: page.url(), finalLang});
    if (lang !== finalLang) report.localeRouting.push({sourceLang: lang, target: 'Linkyoh self-link', finalLang, url: page.url()});
    await ctx.close();
  }
  const hub = await get('https://silvatech.bz/' + (candidate ? 'es/' : '') + '?utm_source=linkyoh&utm_medium=ecosystem&utm_campaign=strip');
  const spanishHub = await get('https://silvatech.bz/es/');
  const documentLang = body => body.toString().match(/<html[^>]*\blang=["']([^"']+)/i)?.[1];
  if (documentLang(hub.body) !== 'es' && documentLang(spanishHub.body) === 'es') report.localeRouting.push({sourceLang: 'es', target: 'Silvatech root', finalLang: documentLang(hub.body), url: hub.finalUrl, spanishAlternative: spanishHub.finalUrl});
  if (candidate) {
    const ctx = await browser.newContext();
    await ctx.route('**/*', route => {
      const request = route.request(), url = new URL(request.url());
      if (!['GET', 'HEAD'].includes(request.method()) || /analytics\.silvatech|google-analytics|facebook\.com|doubleclick/.test(url.hostname)) return route.abort();
      return route.continue();
    });
    const page = await ctx.newPage();
    report.actualDestinations = [];
    for (const lang of ['en', 'es']) {
      const view = report.views.find(view => view.label === `home-${lang}-390`);
      for (const link of view.links) {
        const requested = new URL(link.href), response = await page.goto(requested.href, {waitUntil: 'networkidle', timeout: 45000});
        const metrics = await page.evaluate(() => ({lang: document.documentElement.lang, title: document.title,
          headings: [...document.querySelectorAll('h1')].map(e => e.innerText.trim()), visibleTextLength: document.body.innerText.trim().length,
          hubLinks: [...document.querySelectorAll('a[href]')].filter(a => new URL(a.href).hostname === 'silvatech.bz').map(a => a.href)}));
        const final = new URL(page.url());
        check(response.status() === 200 && final.hostname === requested.hostname, 'Actual destination failed: ' + link.name);
        for (const [key, value] of requested.searchParams) check(final.searchParams.get(key) === value, 'Destination lost query: ' + key);
        check(metrics.visibleTextLength > 100 && metrics.headings.some(value => value.length > 3) && !/^(404|page not found|not found)/i.test(metrics.title), 'Soft 404/empty destination: ' + link.name);
        check(metrics.hubLinks.length > 0, 'Missing return-to-hub route: ' + link.name);
        if (lang === 'es' && (localeHosts.includes(final.hostname) || final.hostname === 'silvatech.bz')) {
          if (final.hostname === 'wop.silvatech.bz') check(metrics.headings.some(value => /Convierte WhatsApp/.test(value)), 'WOP Spanish content missing');
          else check(metrics.lang === 'es', 'Destination failed Spanish rendering: ' + link.name);
        }
        report.actualDestinations.push({requested: requested.href, final: final.href, status: response.status(), sourceLang: lang, ...metrics});
      }
    }
    await ctx.close();
  }
  check(report.errors.length === 0 && report.blockedWrites.length === 0, 'Unexpected error/write request');
  report.passed = true;
} catch (error) {
  report.errors.push(error.message);
  report.passed = false;
  process.exitCode = 1;
  console.error(error);
} finally {
  report.finished = new Date().toISOString();
  await writeFile(path.join(out, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  await browser.close();
  console.log(JSON.stringify({passed: report.passed, views: report.views.length, keyboard: report.keyboard.length, nojs: report.nojs.length, localeRouting: report.localeRouting, errors: report.errors}));
}
