import assert from 'node:assert/strict';
import {test} from 'node:test';
import {createStaticTransport,siteAssetUrl} from '../src/runtime/staticTransport.ts';

function fixture(){
 const root='https://example.github.io/FLOW-Etude-Economique/';
 const manifest={format:1,id:'flow-study',model_version:'model-1',simulation_contract:'contract-1',server_revision:'delivery-1',base:'/FLOW-Etude-Economique/',bootstrap:'data/delivery-1/bootstrap.json',routes:{'/api/ui':'data/delivery-1/ui.json','/api/market-build':'data/delivery-1/market.json','/api/capability':'data/delivery-1/capabilities.json'},documents:{'sources/offre.pdf':{url:'documents/hash/offre.pdf',sha256:'hash'}},python:{archive:'data/delivery-1/engine.zip',archive_sha256:'hash',model:'data/delivery-1/model.json.gz',model_sha256:'hash',pyodide:'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/'}};
 const bootstrap={model_version:'model-1',simulation_contract:'contract-1',server_revision:'delivery-1',baseline:{value:123}};
 const files=new Map([[root+'site-manifest.json',manifest],[root+manifest.bootstrap,bootstrap],[root+manifest.routes['/api/ui'],{title:'Study'}],[root+manifest.routes['/api/market-build'],{items:[1,2]}],[root+manifest.routes['/api/capability'],{BC01:{title:'Capability',text:'Scope',source:'source/map.yaml'}}]]);
 const fetched=[],workers=[];
 const client=createStaticTransport({manifestUrl:root+'site-manifest.json',fetch:async(url,options)=>{fetched.push({url,options});return new Response(JSON.stringify(files.get(url)),{status:files.has(url)?200:404});},createWorker:()=>{const worker={messages:[],onmessage:null,onerror:null,terminated:false,postMessage(message){this.messages.push(message);},terminate(){this.terminated=true;}};workers.push(worker);return worker;}});
 return {root,manifest,bootstrap,files,fetched,workers,client};
}

test('static bootstrap uses the project subpath and cached data stays isolated',async()=>{
 const f=fixture();
 const first=await f.client.request('/api/bootstrap?view=essential');first.baseline.value=999;
 assert.equal((await f.client.request('/api/bootstrap?view=essential')).baseline.value,123);
 assert.equal(f.fetched.length,2);assert.equal(f.workers.length,0);
 assert.ok(f.fetched.every(({url})=>url.startsWith(f.root)));
 assert.equal(f.client.fileHref('sources/offre.pdf#page=3'),f.root+'documents/hash/offre.pdf#page=3');
 assert.equal(f.client.fileHref('sources/private.pdf'),undefined);
});

test('documentary routes enforce the loaded model version and declared identities',async()=>{
 const f=fixture();
 await assert.rejects(f.client.request('/api/market-build?model_version=old'),{code:'version'});
 assert.equal(f.fetched.length,1);
 assert.deepEqual(await f.client.request('/api/market-build?model_version=model-1'),{items:[1,2]});
 assert.equal((await f.client.request('/api/capability?id=BC01&model_version=model-1')).title,'Capability');
 await assert.rejects(f.client.request('/api/capability?id=absent&model_version=model-1'),{code:'missing_document'});
 await assert.rejects(f.client.request('/api/unknown'),{code:'missing_document'});
 assert.equal(f.workers.length,0);
});

test('a new delivery is announced without replacing the loaded reference',async()=>{
 const f=fixture();await f.client.request('/api/bootstrap?view=essential');
 f.files.set(f.root+'site-manifest.json',{...f.manifest,server_revision:'delivery-2',model_version:'model-2'});
 const health=await f.client.request('/api/health');
 assert.equal(health.server_revision,'delivery-2');
 assert.equal(f.fetched.at(-1).options.cache,'no-store');
 assert.equal((await f.client.request('/api/bootstrap?view=essential')).model_version,'model-1');
 assert.deepEqual(await f.client.request('/api/market-build?model_version=model-1'),{items:[1,2]});
});

test('mismatched deployed bootstrap is rejected before it can replace a session',async()=>{
 const f=fixture();f.files.set(f.root+f.manifest.bootstrap,{...f.bootstrap,simulation_contract:'another-contract'});
 await assert.rejects(f.client.request('/api/bootstrap?view=essential'),{code:'version'});
});

test('simulations and documentary fragments are delegated unchanged to one lazy worker',async()=>{
 const f=fixture(),body={parameters:{common:{rate:17},options:{java:{build:1234}}},model_version:'model-1'};
 const simulation=f.client.request('/api/simulate',body);
 await new Promise(resolve=>setImmediate(resolve));
 assert.equal(f.workers.length,1);
 const worker=f.workers[0],job=worker.messages[0];
 assert.equal(job.path,'/api/simulate');assert.deepEqual(JSON.parse(job.body),body);
 worker.onmessage({data:{id:job.id,reply:{status:200,data:{total:9876}}}});
 assert.deepEqual(await simulation,{total:9876});
 const document=f.client.request('/api/document?path=source/map.yaml%23scope');
 await new Promise(resolve=>setImmediate(resolve));
 const docJob=worker.messages[1];assert.equal(docJob.body,'');
 worker.onmessage({data:{id:docJob.id,reply:{status:404,data:{error:'missing_document'}}}});
 await assert.rejects(document,{code:'missing_document'});
 assert.equal(f.workers.length,1);
});

test('runtime errors keep validation fields, and worker failure rejects every pending request',async()=>{
 const f=fixture();
 const invalid=f.client.request('/api/simulate',{model_version:'model-1'});
 await new Promise(resolve=>setImmediate(resolve));
 const worker=f.workers[0];
 worker.onmessage({data:{id:worker.messages[0].id,reply:{status:422,data:{error:'invalid_number',field:'common.rate'}}}});
 await assert.rejects(invalid,{code:'invalid_number',field:'common.rate'});
 const first=f.client.request('/api/simulate',{}),second=f.client.request('/api/document?path=source/a.yaml');
 const failures=Promise.all([assert.rejects(first,{code:'network'}),assert.rejects(second,{code:'network'})]);
 await new Promise(resolve=>setImmediate(resolve));worker.onerror({});await failures;
 assert.equal(worker.terminated,true);
});

test('manifest data cannot address another origin or escape the project prefix',()=>{
 const base='https://example.github.io/FLOW-Etude-Economique/site-manifest.json';
 for(const path of ['../secret.json','/other/data.json','https://unrelated.example/model.json'])assert.throws(()=>siteAssetUrl(path,base),{code:'missing_document'});
});
