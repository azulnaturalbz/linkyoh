import {createRequire} from 'node:module';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || '/Users/cristiansilva/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.dirname(fileURLToPath(import.meta.url)), out=path.join(root,'evidence');
const base='http://127.0.0.1:8098';
const routes=JSON.parse(await readFile(path.join(out,'routes.json'),'utf8'));
const authenticated=new Set(['profile-edit','edit-gig','claim','my_gigs','create_gig','password_change','password_change_done','messaging_unified','notification_list','conversation','conversation-detail','message-draft']);
const selected=process.env.QA_PAGES?.split(',');
const previous=selected?JSON.parse(await readFile(path.join(out,'qa-report.json'),'utf8')):null;
const report={generatedAt:new Date().toISOString(),base,productionWrites:false,syntheticAccounts:true,views:previous?previous.views.filter(v=>!selected.some(n=>v.label.startsWith(n+'-'))):[],errors:[],blockedExternal:[]};
const browser=await chromium.launch({headless:true});
await mkdir(out,{recursive:true});
async function context(width,lang,nojs=false){
  const ctx=await browser.newContext({viewport:{width,height:width<700?844:1000},locale:lang,javaScriptEnabled:!nojs});
  await ctx.route('**/*',r=>{
    const u=new URL(r.request().url());
    if(u.origin===base)return r.continue();
    if(u.hostname==='analytics.silvatech.bz')return r.fulfill({contentType:'text/javascript',body:'/* isolated QA */'});
    if(u.hostname==='api.qrserver.com')return r.fulfill({contentType:'image/png',body:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=','base64')});
    report.blockedExternal.push(u.origin+u.pathname); return r.abort();
  });
  return ctx;
}
async function login(page,lang){
  await page.goto(base+'/login/?lang='+lang);
  await page.locator('#id_username').fill('qa-provider');
  await page.locator('#id_password').fill('Local-review-only-2026');
  await Promise.all([page.waitForURL(u=>!u.pathname.startsWith('/login/')),page.locator('form[action="/login/"] button[type=submit]').click()]);
}
async function inspect(page){return page.evaluate(()=>{
  const visible=e=>{for(let p=e;p;p=p.parentElement){const s=getComputedStyle(p);if(s.display==='none'||s.visibility==='hidden'||Number(s.opacity)===0)return false;}return !!e.getClientRects().length;};
  const rgb=v=>(v.match(/[\d.]+/g)||[]).map(Number);
  const blend=(f,b)=>[0,1,2].map(i=>f[i]*(f[3]??1)+b[i]*(1-(f[3]??1)));
  const bg=e=>{const c=[];for(let p=e;p;p=p.parentElement)c.unshift(p);return c.reduce((a,p)=>blend(rgb(getComputedStyle(p).backgroundColor),a),[255,255,255]);};
  const lum=c=>c.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0);
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT),contrasts=[];
  while(walker.nextNode()){
    const n=walker.currentNode,e=n.parentElement,t=n.textContent.trim();
    if(!t||!e||!visible(e)||['SCRIPT','STYLE','OPTION'].includes(e.tagName)||e.closest('svg,.visually-hidden,.sr-only,[disabled]'))continue;
    const s=getComputedStyle(e),size=parseFloat(s.fontSize),back=bg(e),a=lum(back),b=lum(blend(rgb(s.color),back));
    const ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05),minimum=size>=24||(size>=18.66&&+s.fontWeight>=700)?3:4.5;
    if(ratio<minimum)contrasts.push({text:t.slice(0,90),ratio:+ratio.toFixed(2),minimum,element:e.tagName+'.'+e.className});
  }
  return {width:innerWidth,documentWidth:document.documentElement.scrollWidth,mainText:document.querySelector('main').innerText.trim().length,overflow:[...document.querySelectorAll('main *, .site-header *')].filter(e=>visible(e)&&!e.closest('.brand-art')&&(e.getBoundingClientRect().right>innerWidth+1||e.getBoundingClientRect().left< -1)).map(e=>e.tagName+'.'+e.className).slice(0,20),contrastFailures:contrasts,brokenImages:[...document.images].filter(i=>visible(i)&&(!i.complete||!i.naturalWidth)).map(i=>i.getAttribute('src')),lang:document.documentElement.lang,icons:document.querySelectorAll('svg.lucide').length};
});}
try {
  const widths=(process.env.QA_WIDTHS||'320,390,768,944,1440').split(',').map(Number);
  for(const lang of ['en','es'])for(const width of widths){
    const ctx=await context(width,lang),page=await ctx.newPage();let loggedIn=false;
    page.on('pageerror',e=>report.errors.push({url:page.url(),message:e.message}));
    for(const [name,route]of Object.entries(routes).sort((a,b)=>Number(authenticated.has(a[0]))-Number(authenticated.has(b[0])))){
      if(selected&&!selected.includes(name))continue;
      if(authenticated.has(name)&&!loggedIn){await login(page,lang);loggedIn=true;}
      const label=`${name}-${lang}-${width}`;
      const response=await page.goto(base+route+(route.includes('?')?'&':'?')+'lang='+lang);
      await page.evaluate(()=>document.fonts.ready);
      await page.waitForTimeout(150);
      const metrics=await inspect(page);
      report.views.push({label,status:response.status(),...metrics});
      await page.screenshot({path:path.join(out,label+'.png')});
      if(width===390)await page.screenshot({path:path.join(out,label+'-full.png'),fullPage:true});
      console.log(label,response.status(),metrics.documentWidth,metrics.overflow.length,metrics.contrastFailures.length,metrics.brokenImages.length);
    }
    await ctx.close();
  }
} finally {
  report.blockedExternal=[...new Set(report.blockedExternal)];
  if(report.errors.length||report.views.some(v=>v.status!==200||v.width!==v.documentWidth||v.overflow.length||v.contrastFailures.length||v.brokenImages.length))process.exitCode=1;
  await writeFile(path.join(out,'qa-report.json'),JSON.stringify(report,null,2)+'\n');
  await browser.close();
}
