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
    const page=await context.newPage();
    await page.goto(base+'/login/?lang='+language);
    await page.locator('#id_username').fill('qa-provider');
    await page.locator('#id_password').fill('Local-review-only-2026');
    await Promise.all([page.waitForURL(u=>!u.pathname.startsWith('/login/')),page.locator('form[action="/login/"] button').click()]);
    for(const name of ['conversation','conversation-detail']){
      await page.goto(base+routes[name]+'?lang='+language);
      const resolvedPath=new URL(page.url()).pathname;
      const field=page.locator('textarea[name="content"]'),form=field.locator('..').locator('..');
      assert.equal(await form.getAttribute('method'),'post');
      const action=new URL(await form.getAttribute('action'),base).href;
      await field.fill('Synthetic draft, never sent');
      if(javascript){
        await field.press('Shift+Enter');
        assert.match(await field.inputValue(),/\n$/);
        await page.route(action,r=>r.fulfill({status:500,body:'Synthetic failure'}));
        await Promise.all([page.waitForResponse(action),form.locator('button[type="submit"]').click()]);
        await page.locator('.message-status:not([hidden])').waitFor();
        assert.match(await field.inputValue(),/Synthetic draft/);
        await page.screenshot({path:new URL(`message-failure-${name}-${language}.png`,out).pathname,fullPage:true});
        await page.unroute(action);
        await page.route(action,r=>r.fulfill({status:200,contentType:'text/html',body:'<p data-qa-response="true">Synthetic response, no database write</p>'}));
        await form.locator('button[type="submit"]').click();
        await page.locator('[data-qa-response]').waitFor();
        await page.waitForFunction(()=>document.querySelector('textarea[name="content"]').value==='');
        assert.ok(await page.locator('.message-status').isHidden());
      }else{
        await page.route(action,r=>r.fulfill({status:302,headers:{location:resolvedPath}}));
        await Promise.all([page.waitForURL(u=>u.pathname===resolvedPath&&!u.search),form.locator('button[type="submit"]').click()]);
      }
      await page.unroute(action);
      results.push({language,javascript,page:name,nativePOST:'pass',draftRecovery:javascript?'pass':'not applicable',productionWrites:false,messageWrites:false});
    }
    await context.close();
  }
} finally {await browser.close();await writeFile(new URL('messages.json',out),JSON.stringify(results,null,2)+'\n');}
