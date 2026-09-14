import {createRequire} from 'node:module';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const require=createRequire(import.meta.url);
const {chromium}=require('/Users/cristiansilva/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.dirname(fileURLToPath(import.meta.url)),out=path.join(root,'evidence');
const repo=path.resolve(root,'../../..'),base='https://linkyoh.com';
await mkdir(out,{recursive:true});
const report={utc:new Date().toISOString(),base,views:[],errors:[],journeys:[],https:[],assets:[],legacy:[],blocked:[]};
const urls=['https://linkyoh.com/','https://www.linkyoh.com/','https://wop.silvatech.bz/health/','https://n8n.silvatech.bz/','https://payments.silvatech.bz/','https://nationalperspectivebz.com/','https://analytics.silvatech.bz/api/health','https://marketday.silvatech.bz/','https://yardsale.marketday.silvatech.bz/','https://chillbout.com/'];
for(const url of urls){const r=await fetch(url,{signal:AbortSignal.timeout(30000)});report.https.push({url,status:r.status,finalUrl:r.url});await r.arrayBuffer();}
if(process.argv.includes('--before')){await writeFile(path.join(out,'https-before.json'),JSON.stringify(report.https,null,2));process.exit(report.https.some(r=>r.status!==200)?1:0);}
const routes={home:'/',results:'/search/?q=plumber+in+Cayo',provider:'/belize/providers/linkyoh-ai-admin-218/',gig:'/belize/services/belize/belize-city/gracekennedy-belize-ltd-110/',category:'/belize/services/services-5/',subcategory:'/belize/services/services/wholesale-importer-476/',login:'/login/',register:'/register/',help:'/help/search/',about:'/about-us/'};
const browser=await chromium.launch({headless:true});
function assert(value,message){if(!value)throw new Error(message);}
async function ctx(width,lang,nojs=false){
  const context=await browser.newContext({viewport:{width,height:width<700?844:1000},locale:lang,javaScriptEnabled:!nojs});
  await context.route('**/*',r=>{
    const u=new URL(r.request().url());
    if(!['GET','HEAD'].includes(r.request().method())){report.blocked.push('write:'+u.origin+u.pathname);return r.abort();}
    if(u.hostname==='analytics.silvatech.bz')return r.fulfill({contentType:'text/javascript',body:'/* release QA: analytics suppressed */'});
    if(['linkyoh.com','www.linkyoh.com','linkyoh-prd-assets-944327601374-us-east-1.s3.amazonaws.com','api.qrserver.com'].includes(u.hostname))return r.continue();
    report.blocked.push(u.origin+u.pathname);return r.abort();
  });
  return context;
}
async function inspect(page){return page.evaluate(()=>{
  const visible=e=>{for(let p=e;p;p=p.parentElement){const s=getComputedStyle(p);if(s.display==='none'||s.visibility==='hidden'||+s.opacity===0)return false;}return !!e.getClientRects().length;};
  const rgb=v=>(v.match(/[\d.]+/g)||[]).map(Number),blend=(f,b)=>[0,1,2].map(i=>f[i]*(f[3]??1)+b[i]*(1-(f[3]??1)));
  const bg=e=>{const c=[];for(let p=e;p;p=p.parentElement)c.unshift(p);return c.reduce((a,p)=>blend(rgb(getComputedStyle(p).backgroundColor),a),[255,255,255]);};
  const lum=c=>c.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0);
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT),contrastFailures=[];let textSamples=0;
  while(walker.nextNode()){
    const n=walker.currentNode,e=n.parentElement,t=n.textContent.trim();
    if(!t||!e||!visible(e)||['SCRIPT','STYLE','OPTION'].includes(e.tagName)||e.closest('svg,.visually-hidden,.sr-only,[disabled]'))continue;
    const s=getComputedStyle(e),size=parseFloat(s.fontSize),back=bg(e),a=lum(back),b=lum(blend(rgb(s.color),back));
    const ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05),minimum=size>=24||(size>=18.66&&+s.fontWeight>=700)?3:4.5;textSamples++;
    if(ratio<minimum)contrastFailures.push({text:t.slice(0,90),ratio:+ratio.toFixed(2),minimum});
  }
  return {width:innerWidth,documentWidth:document.documentElement.scrollWidth,lang:document.documentElement.lang,
    overflow:[...document.querySelectorAll('main *, .site-header *')].filter(e=>visible(e)&&!e.closest('.brand-art')&&(e.getBoundingClientRect().right>innerWidth+1||e.getBoundingClientRect().left< -1)).map(e=>e.tagName+'.'+e.className).slice(0,20),
    brokenImages:[...document.images].filter(i=>visible(i)&&i.getBoundingClientRect().top<innerHeight&&(!i.complete||!i.naturalWidth)).map(i=>i.src),
    textSamples,contrastFailures,checked:document.querySelectorAll('[data-checked]').length,
    canonical:document.querySelector('link[rel=canonical]')?.href,ogImage:document.querySelector('meta[property="og:image"]')?.content,
    schema:[...document.querySelectorAll('script[type="application/ld+json"]')].map(e=>JSON.parse(e.textContent)),
    finderModes:[...document.querySelectorAll('[data-finder-mode]')].map(e=>e.dataset.finderMode),
    wordmark:!!document.querySelector('img[src*="linkyoh-stitch-wordmark"]'),
    stripVersion:document.querySelector('.svt-ecosystem-strip')?.dataset.stripVersion,
    stripLinks:[...document.querySelectorAll('.svt-ecosystem-strip a')].map(a=>({name:a.textContent.trim(),href:a.href,track:a.dataset.track,rel:a.rel,height:a.getBoundingClientRect().height}))};
});}
try{
  for(const lang of ['en','es'])for(const width of [320,390,768,944,1440]){
    const context=await ctx(width,lang),page=await context.newPage();
    page.on('pageerror',e=>report.errors.push({url:page.url(),message:e.message}));
    const names=width===390?Object.keys(routes):['home','results','provider','gig'];
    for(const name of names){
      const route=routes[name],label=`${name}-${lang}-${width}`;
      const response=await page.goto(base+route+(route.includes('?')?'&':'?')+'lang='+lang,{waitUntil:'networkidle',timeout:45000});
      await page.evaluate(()=>document.fonts.ready);
      const metrics=await inspect(page);
      report.views.push({label,status:response.status(),...metrics});
      await page.screenshot({path:path.join(out,label+'.png')});
      console.log(label,response.status(),'overflow',metrics.overflow.length,'broken',metrics.brokenImages.length,'contrast',metrics.contrastFailures.length);
      assert(response.status()===200&&metrics.wordmark,label+' not on candidate UI');
      assert(metrics.stripVersion==='v2'&&metrics.stripLinks.length===10,label+' missing strip v2');
      assert(metrics.stripLinks.map(x=>x.name).join('|')==='Silvatech|Visit Belize|Chillbout|Linkyoh|MarketDay|WOP|Payments|Consulta|Belize Logistics|Games',label+' strip order');
      for(const link of metrics.stripLinks){const u=new URL(link.href);assert(u.searchParams.get('utm_source')==='linkyoh'&&u.searchParams.get('utm_medium')==='ecosystem'&&u.searchParams.get('utm_campaign')==='strip'&&link.rel==='noreferrer'&&link.height>=44,label+' strip attribution/privacy/target');}
      assert(metrics.stripLinks[9].track==='games_clickout',label+' Games event');
      const organizations=metrics.schema.flatMap(s=>s['@graph']||[s]).filter(s=>s['@type']==='Organization');
      assert(organizations.some(s=>(s.sameAs||[]).filter(u=>u==='https://games.silvatech.bz').length===1),label+' Games identity');
      await page.locator('.svt-ecosystem-strip').screenshot({path:path.join(out,label+'-strip.png')});
      assert(metrics.canonical===base+route.split('?')[0]||name==='results',label+' canonical drift');
      assert(metrics.lang===lang,label+' locale');
      assert(!metrics.finderModes.includes('conversation'),'WOP must stay off');
      await page.waitForTimeout(1100);
    }
    await context.close();
  }
  for(const lang of ['en','es'])for(const nojs of [true,false]){
    const context=await ctx(390,lang,nojs),page=await context.newPage();
    await page.goto(base+'/?lang='+lang,{waitUntil:'networkidle'});
    await page.keyboard.press('Tab');assert(await page.locator('.skip-link').evaluate(e=>e===document.activeElement),'skip link focus');
    await page.keyboard.press('Enter');assert(new URL(page.url()).hash==='#body','skip target');
    const summary=page.locator('.mobile-navigation>summary');
    await summary.focus();await page.keyboard.press('Enter');assert(await page.locator('.mobile-navigation').getAttribute('open')!==null,'menu opens');
    await summary.focus();await page.keyboard.press('Enter');assert(await page.locator('.mobile-navigation').getAttribute('open')===null,'menu closes');
    await page.locator('#need').fill(lang==='es'?'plomero en Cayo':'plumber in Cayo');
    await Promise.all([page.waitForURL(u=>u.pathname==='/search/'),page.locator('#need').press('Enter')]);
    assert(new URL(page.url()).searchParams.has('q'),'GET shareable query');
    const district=await page.locator('#district option:checked').textContent();assert(district==='Cayo','real district parsing');
    await page.locator('#need').fill('zzzz-no-service-release-qa');
    await Promise.all([page.waitForURL(u=>u.searchParams.get('q')==='zzzz-no-service-release-qa'),page.locator('#need').press('Enter')]);
    assert(await page.locator('.card-grid .empty').count()===1,'honest empty state');
    await page.screenshot({path:path.join(out,`empty-${lang}-${nojs?'nojs':'keyboard'}.png`)});
    report.journeys.push({lang,nojs,skip:true,menu:true,smartGet:true,district,empty:true});
    await context.close();
  }
  for(const [route,expected]of [['/gigs/110/',routes.gig],['/profile/218/',routes.provider],['/category/5/',routes.category]]){
    const r=await fetch(base+route,{redirect:'manual'});report.legacy.push({route,status:r.status,location:r.headers.get('location')});assert(r.status===301&&r.headers.get('location')===expected,'legacy redirect');
  }
  for(const asset of ['static/lab/assets/silvatech-ui.css','static/css/ecosystem-strip.css','static/lab/sitewide.css','static/lab/discovery.css','static/lab/assets/linkyoh-stitch-wordmark.png','static/lab/assets/linkyoh-belize-banner.png','static/brand/kev/kev-plumbing-master.png']){
    const r=await fetch(base+'/'+asset),data=Buffer.from(await r.arrayBuffer()),expected=await readFile(path.join(repo,asset));
    const match=data.equals(expected);report.assets.push({asset,status:r.status,match,sha256:createHash('sha256').update(data).digest('hex')});assert(r.status===200&&match,'asset mismatch '+asset);
  }
  for(const route of ['/robots.txt','/llms.txt','/sitemap.xml']){const r=await fetch(base+route),body=await r.text();report.https.push({url:base+route,status:r.status,bytes:body.length});assert(r.status===200&&body.length>100,'crawl surface');if(route==='/llms.txt')assert(body.includes('https://games.silvatech.bz?')&&body.includes('not open for bookings')&&!body.includes('inactive/reserved'),'related product contract');}
  for(const image of new Set(report.views.map(v=>v.ogImage).filter(Boolean))){const r=await fetch(image);report.assets.push({asset:image,status:r.status,bytes:(await r.arrayBuffer()).byteLength});assert(r.status===200,'OG image failure');}
}catch(error){report.errors.push({message:error.message});console.error(error);process.exitCode=1;}
finally{
  report.blocked=[...new Set(report.blocked)];
  report.passed=!report.errors.length&&report.https.every(r=>r.status===200)&&report.views.every(v=>v.status===200&&v.width===v.documentWidth&&!v.overflow.length&&!v.brokenImages.length&&!v.contrastFailures.length);
  if(!report.passed)process.exitCode=1;
  await writeFile(path.join(out,'public-qa.json'),JSON.stringify(report,null,2)+'\n');await browser.close();
}
