import assert from 'node:assert/strict';
import {readFile, writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const here=path.dirname(fileURLToPath(import.meta.url));
const repo=path.resolve(here,'../../..');
const phase=process.argv.includes('--before')?'before':'after';
const report={utc:new Date().toISOString(),phase,https:[],legacy:[],assets:[],errors:[],writes:false};
const urls=['https://linkyoh.com/','https://www.linkyoh.com/',
  'https://wop.silvatech.bz/health/','https://n8n.silvatech.bz/',
  'https://payments.silvatech.bz/','https://nationalperspectivebz.com/',
  'https://analytics.silvatech.bz/api/health','https://marketday.silvatech.bz/',
  'https://yardsale.marketday.silvatech.bz/','https://chillbout.com/',
  ...['robots.txt','llms.txt','sitemap.xml'].map(p=>'https://linkyoh.com/'+p)];
try {
  for(const url of urls){
    const response=await fetch(url,{signal:AbortSignal.timeout(30000)});
    const body=await response.text();
    report.https.push({url,status:response.status,finalUrl:response.url,bytes:body.length});
    assert.equal(response.status,200,url);
  }
  for(const [route,target] of [
    ['/gigs/110/','/belize/services/belize/belize-city/gracekennedy-belize-ltd-110/'],
    ['/profile/218/','/belize/providers/linkyoh-ai-admin-218/'],
    ['/category/5/','/belize/services/services-5/'],
  ]){
    const response=await fetch('https://linkyoh.com'+route,{redirect:'manual',signal:AbortSignal.timeout(30000)});
    const location=response.headers.get('location');
    report.legacy.push({route,status:response.status,location});
    assert.equal(response.status,301); assert.equal(location,target);
    const page=await fetch('https://linkyoh.com'+target,{signal:AbortSignal.timeout(30000)});
    const body=await page.text();
    const canonical=body.match(/<link\s+rel="canonical"\s+href="([^"]+)"/)?.[1];
    const og=body.match(/<meta\s+property="og:image"\s+content="([^"]+)"/)?.[1];
    assert.equal(page.status,200); assert.equal(canonical,'https://linkyoh.com'+target); assert.ok(og);
    const image=await fetch(og,{signal:AbortSignal.timeout(30000)});
    report.assets.push({url:og,status:image.status,bytes:(await image.arrayBuffer()).byteLength});
    assert.equal(image.status,200);
  }
  for(const asset of ['static/lab/assets/silvatech-ui.css','static/css/ecosystem-strip.css','static/js/ecosystem-tracking.js']){
    const response=await fetch('https://linkyoh.com/'+asset,{signal:AbortSignal.timeout(30000)});
    const bytes=Buffer.from(await response.arrayBuffer());
    assert.equal(response.status,200); assert.ok(bytes.equals(await readFile(path.join(repo,asset))));
    report.assets.push({asset,status:response.status,match:true,sha256:createHash('sha256').update(bytes).digest('hex')});
  }
}catch(error){report.errors.push(error.message);process.exitCode=1;}
report.passed=!report.errors.length;
await writeFile(path.join(here,'evidence',`public-${phase}.json`),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({passed:report.passed,https:report.https.length,legacy:report.legacy.length,assets:report.assets.length,errors:report.errors}));
