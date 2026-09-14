import {createRequire} from 'node:module';
import {readFile,writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || '/Users/cristiansilva/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const base='http://127.0.0.1:8098',out=new URL('./evidence/',import.meta.url);
const routes=JSON.parse(await readFile(new URL('routes.json',out),'utf8'));
const results=[];
const browser=await chromium.launch({headless:true});
try {
  for(const language of ['en','es'])for(const javascript of [true,false]){
    const context=await browser.newContext({viewport:{width:390,height:844},javaScriptEnabled:javascript,locale:language});
    await context.route('**/*',route=>new URL(route.request().url()).origin===base?route.continue():route.abort());
    const page=await context.newPage(),errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    await page.goto(base+'/?lang='+language);
    await page.keyboard.press('Tab');
    assert.equal(await page.locator(':focus').getAttribute('href'),'#body');
    await page.keyboard.press('Enter');
    assert.equal(await page.locator(':focus').getAttribute('id'),'body');
    const menu=page.locator('.mobile-navigation > summary');
    await menu.focus();await page.keyboard.press('Enter');
    assert.ok(await page.locator('.mobile-navigation').evaluate(e=>e.open));
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('.mobile-navigation').evaluate(e=>e.open),false);
    await page.locator('#need').fill(language==='es'?'Plomero en San Ignacio':'Plumber in San Ignacio');
    await Promise.all([page.waitForURL('**/search/**'),page.locator('.search-input button').click()]);
    assert.ok((await page.locator('.provider-card').count())>0);
    assert.match(await page.locator('select#location option:checked').textContent(),/San Ignacio/);
    const shareURL=page.url();await page.goto(shareURL);
    assert.ok((await page.locator('.provider-card').count())>0);
    await page.goto(base+'/search/?q=NoSuchServiceXYZ&lang='+language);
    assert.equal(await page.locator('.provider-card').count(),0);
    assert.ok(await page.locator('.empty').isVisible());
    await page.goto(base+'/login/?lang='+language);
    await page.locator('#id_username').fill('qa-provider');
    await page.locator('#id_password').fill('Local-review-only-2026');
    await Promise.all([page.waitForURL(u=>!u.pathname.startsWith('/login/')),page.locator('form[action="/login/"] button').click()]);
    await page.goto(base+'/create-gig/?lang='+language);
    assert.equal(await page.locator('#id_category option').count(),6);
    assert.equal(await page.locator('#id_district option').count(),7);
    assert.equal(await page.locator('#id_subcategory option').count(),440);
    assert.equal(await page.locator('#id_location option').count(),245);
    await page.locator('#id_category').selectOption({label:language==='es'?'Vivienda y construcción':'Housing & Construction'});
    if(javascript)await page.waitForFunction(()=>document.querySelector('#id_subcategory').options.length<440);
    assert.ok(await page.locator('#id_subcategory option[value="431"]').count());
    await page.locator('#id_district').selectOption({label:'Cayo'});
    if(javascript)await page.waitForFunction(()=>document.querySelector('#id_location').options.length<245);
    if(javascript){
      for(let i=0;i<3;i++)await page.locator('#next-tab').click();
      assert.ok(await page.locator('#submit-btn').isVisible());
    }else{
      assert.ok(await page.locator('#images').isVisible());
      assert.ok(await page.locator('#locations').isVisible());
    }
    assert.equal(await page.locator('#submit-btn').evaluate(e=>e.form?.id),'gigForm');
    await page.screenshot({path:new URL(`form-${language}-${javascript?'js':'nojs'}.png`,out).pathname,fullPage:true});
    await page.goto(base+routes['profile-edit']+'&lang='+language);
    assert.ok(await page.locator('form.profile-form').isVisible());
    await page.goto(base+'/help/faq/?lang='+language);
    if(javascript){const accordion=page.locator('.accordion-button.collapsed').first();const target=await accordion.getAttribute('aria-controls');await accordion.click();assert.equal(await page.locator(`[aria-controls="${target}"]`).getAttribute('aria-expanded'),'true');}
    else assert.ok(await page.locator('.accordion-collapse').last().isVisible());
    await page.locator('.mobile-navigation > summary').click();
    await page.locator('.mobile-navigation nav a').first().click();
    assert.equal(new URL(page.url()).pathname,'/search/');
    assert.deepEqual(errors,[]);
    results.push({language,javascript,keyboard:'pass',smartGET:'pass',referenceDropdowns:'pass',listingForm:'pass',profileEditor:'pass',helpNavigation:'pass'});
    await context.close();
  }
} finally {await browser.close();await writeFile(new URL('journeys.json',out),JSON.stringify(results,null,2)+'\n');}
