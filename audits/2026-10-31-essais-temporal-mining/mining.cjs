/* Actual pinned PM4JS algorithms; synthetic mutations supplement real Temporal histories. */
const fs=require('fs'),path=require('path'),assert=require('assert'),{performance}=require('perf_hooks');
const R=process.cwd(),A=path.join(R,'audits/2026-10-31-essais-temporal-mining'),O=path.join(A,'results');
const P=path.join(R,'tmp/targeted-runtime/pm4js/pm4js-core-3eb7378dd5db8db72d7474454d69a455855b9e25/pm4js');
for(const f of ['pm4js.js','utils/generic/business_hours.js','objects/log/log.js','statistics/log/general.js','objects/dfg/frequency/obj.js','objects/dfg/performance/obj.js','algo/discovery/dfg/algorithm.js','algo/conformance/alignments/heapq.js','algo/conformance/alignments/dfg/algorithm.js','objects/petri_net/petri_net.js','algo/conformance/alignments/petri_net/algorithm.js']) require(path.join(P,f));
const checks=[];function check(id,ok,detail){checks.push({id,passed:!!ok,detail});assert.ok(ok,id+': '+JSON.stringify(detail));}
function payloads(x){return (x?.payloads||[]).map(p=>JSON.parse(Buffer.from(p.data,'base64').toString('utf8')));}
function project(file){const h=JSON.parse(fs.readFileSync(file,'utf8'));const started=h.events.find(e=>e.workflowExecutionStartedEventAttributes);const [def,input]=payloads(started.workflowExecutionStartedEventAttributes.input);const base={organisation:input.organisation,case_id:input.caseId,version:def.version};let scheduled={},rows=[],signals=new Set();
 for(const e of h.events){let a=e.activityTaskScheduledEventAttributes;if(a)scheduled[e.eventId]=a;
 let activity=null;
 if(e.activityTaskCompletedEventAttributes){a=scheduled[e.activityTaskCompletedEventAttributes.scheduledEventId];if(a.activityType.name==='Apply')activity=payloads(a.input)[2];else if(a.activityType.name==='Compensate')activity='annuler';}
 if(e.workflowExecutionSignaledEventAttributes){const out=payloads(e.workflowExecutionSignaledEventAttributes.input)[0];if(out.organisation===base.organisation&&out.role==='gestionnaire'&&out.task==='validation'&&!signals.has(out.eventId)){activity=out.approved?'validation':'refus';signals.add(out.eventId);}}
 if(e.workflowExecutionCompletedEventAttributes){const result=payloads(e.workflowExecutionCompletedEventAttributes.result)[0];activity=result.state==='COMPLETED'?'fin':result.state.toLowerCase();}
 if(activity)rows.push({...base,source_id:input.caseId+':'+e.eventId,revision:1,activity,timestamp:e.eventTime,seen_at:e.eventTime});
 }return rows;
}
function canonical(rows,asOf=Infinity){const latest=new Map(),quarantine=[];let duplicates=0;
 for(const r of rows){const observed=Date.parse(r.seen_at),ts=Date.parse(r.timestamp);if(!Number.isFinite(ts)||!Number.isFinite(observed)){quarantine.push({reason:'timestamp',row:r});continue;}if(observed>asOf)continue;const k=r.organisation+'/'+r.source_id,prev=latest.get(k);
 if(!prev||r.revision>prev.revision)latest.set(k,r);else if(r.revision===prev.revision){if(JSON.stringify(r)===JSON.stringify(prev))duplicates++;else quarantine.push({reason:'conflicting-revision',row:r});}}
 return {rows:[...latest.values()].sort((a,b)=>Date.parse(a.timestamp)-Date.parse(b.timestamp)||a.source_id.localeCompare(b.source_id)),duplicates,quarantine};}
function log(rows){const ret=new EventLog(),traces=new Map();for(const r of rows){const k=[r.organisation,r.case_id,r.version].join('/');if(!traces.has(k)){let t=new Trace();t.attributes['concept:name']=new Attribute(k);traces.set(k,t);ret.traces.push(t);}let e=new Event();e.attributes['concept:name']=new Attribute(r.activity);e.attributes['time:timestamp']=new Attribute(new Date(r.timestamp));traces.get(k).events.push(e);}return ret;}
function fixture(acts,id='fixture',org='A'){return acts.map((activity,i)=>({organisation:org,case_id:id,version:1,source_id:id+':'+i,revision:1,activity,timestamp:new Date(Date.UTC(2026,9,31)+i*60000).toISOString(),seen_at:new Date(Date.UTC(2026,9,31)+i*60000).toISOString()}));}
const files=fs.readdirSync(path.join(O,'live')).filter(f=>f.endsWith('.json'));const raw=files.flatMap(f=>project(path.join(O,'live',f))),clean=canonical(raw);
check('real-temporal-history-projected',clean.rows.length>30,{histories:files.length,events:clean.rows.length});
const redelivered=canonical([...raw,...raw].reverse());check('redelivery-idempotent',JSON.stringify(clean.rows)===JSON.stringify(redelivered.rows),redelivered.duplicates);
const f=fixture(['admettre','validation','reserver','notifier','fin']);const correction={...f[1],revision:2,activity:'validation_corrigee',seen_at:'2026-11-02T00:00:00Z'};
check('late-correction-current-view',canonical([...f,correction]).rows.some(x=>x.activity==='validation_corrigee'));
check('late-correction-historical-view',canonical([...f,correction],Date.parse('2026-11-01T00:00:00Z')).rows.some(x=>x.activity==='validation'));
check('conflicting-revision-quarantined',canonical([...f,{...f[0],activity:'tampered'}]).quarantine.length===1);
check('invalid-timestamp-quarantined',canonical([{...f[0],timestamp:'invalid'}]).quarantine.length===1);
check('same-case-id-separated-by-organisation',log([...f,...f.map(r=>({...r,organisation:'B'}))]).traces.length===2);
const dfg=FrequencyDfgDiscovery.apply(log(f));const perf=PerformanceDfgDiscovery.apply(log(f));check('known-dfg-frequencies',Object.values(dfg.pathsFrequency).every(x=>x===1)&&Object.keys(dfg.pathsFrequency).length===4);
check('known-durations-seconds',Object.values(perf.pathsPerformance).every(x=>x===60),perf.pathsPerformance);
const other=fixture(['admettre','validation','notifier','reserver','fin'],'other');
const oneOrder=DfgAlignments.apply(log(other),dfg);check('negative-control-one-observed-order-falsely-rejects-parallel-order',oneOrder.totalCost>0,oneOrder.totalCost);
const combined=FrequencyDfgDiscovery.apply(log([...f,...other]));const duplicate=fixture(['admettre','validation','reserver','notifier','reserver','fin'],'duplicate');
const permissive=DfgAlignments.apply(log(duplicate),combined);check('negative-control-union-dfg-accepts-invalid-repeat',permissive.totalCost===0,permissive.totalCost);
function model(version=1){const n=new PetriNet('parallel-v'+version);let places={};for(const k of ['start','admitted','validated','ready','ra','nb','rd','nd','joined','end'])places[k]=n.addPlace(k);
 function link(id,label,from,to){const t=n.addTransition(id,label);for(const p of from)n.addArcFromTo(places[p],t);for(const p of to)n.addArcFromTo(t,places[p]);}
 link('admit','admettre',['start'],['admitted']);link('human','validation',['admitted'],['validated']);
 link('control',version===2?'verifier_capacite':null,['validated'],['ready']);link('split',null,['ready'],['ra','nb']);link('reserve','reserver',['ra'],['rd']);link('notify',version===2?'notifier_express':'notifier',['nb'],['nd']);link('join',null,['rd','nd'],['joined']);link('finish','fin',['joined'],['end']);
 const im=new Marking(n),fm=new Marking(n);im.setTokens(places.start,1);fm.setTokens(places.end,1);return new AcceptingPetriNet(n,im,fm);}
const pn1=model(),pn2=model(2);const both=PetriNetAlignments.apply(log([...f,...other]),pn1,'concept:name',3);
check('parallel-petri-net-accepts-both-valid-orders',both.percentageFitTraces===1,both.totalCost);
check('parallel-petri-net-detects-duplicate',PetriNetAlignments.apply(log(duplicate),pn1,'concept:name',3).totalCost>0);
check('parallel-petri-net-detects-missing-task',PetriNetAlignments.apply(log(fixture(['admettre','validation','reserver','fin'],'missing')),pn1,'concept:name',3).totalCost>0);
const p2=fixture(['admettre','validation','verifier_capacite','notifier_express','reserver','fin'],'v2');p2.forEach(r=>r.version=2);
check('version-2-against-version-1-is-false-anomaly',PetriNetAlignments.apply(log(p2),pn1,'concept:name',3).totalCost>0);
check('version-2-against-correct-model-fits',PetriNetAlignments.apply(log(p2),pn2,'concept:name',3).totalCost===0);
const completed=log(clean.rows).traces.filter(t=>t.events.at(-1).attributes['concept:name'].value==='fin');const realAlign=[];
for(const t of completed){const v=Number(t.attributes['concept:name'].value.split('/').at(-1)),l=new EventLog();l.traces.push(t);let a=PetriNetAlignments.apply(l,v===2?pn2:pn1,'concept:name',3);realAlign.push({trace:t.attributes['concept:name'].value,cost:a.totalCost});}
check('real-completed-instances-fit-versioned-models',realAlign.length>=4&&realAlign.every(x=>x.cost===0),realAlign);
const benchmark=[];for(const n of [10000,20000]){const rows=[];for(let i=0;i<n;i++)rows.push(...fixture(['admettre','validation',...(i%2?['reserver','notifier']:['notifier','reserver']),'fin'],'load'+i));const t=performance.now(),l=log(rows),start=performance.now(),d=FrequencyDfgDiscovery.apply(l),p=PerformanceDfgDiscovery.apply(l);benchmark.push({traces:n,events:rows.length,log_build_ms:start-t,frequency_and_performance_ms:performance.now()-start,arcs:Object.keys(d.pathsFrequency).length});}
const actualDfg=FrequencyDfgDiscovery.apply(log(clean.rows)),actualPerf=PerformanceDfgDiscovery.apply(log(clean.rows));
fs.writeFileSync(path.join(O,'mining-events.json'),JSON.stringify(clean.rows,null,2));
const metrics=[];for(const org of [...new Set(clean.rows.map(r=>r.organisation))]){for(const v of [...new Set(clean.rows.filter(r=>r.organisation===org).map(r=>r.version))]){const l=log(clean.rows.filter(r=>r.organisation===org&&r.version===v)),d=FrequencyDfgDiscovery.apply(l),p=PerformanceDfgDiscovery.apply(l);for(const [arc,count] of Object.entries(d.pathsFrequency)){const [source,target]=arc.split(',');metrics.push({organisation:org,version:v,source,target,count,mean_seconds:p.pathsPerformance[arc]});}}}
fs.writeFileSync(path.join(O,'mining-metrics.json'),JSON.stringify(metrics,null,2));
const result={status:'passed',date:'2026-10-31',library:{name:'PM4JS',commit:'3eb7378dd5db8db72d7474454d69a455855b9e25'},checks,actual:{histories:files.length,events:clean.rows.length,traces:log(clean.rows).traces.length,reporting_metrics:metrics.length,frequency:actualDfg.pathsFrequency,mean_seconds:actualPerf.pathsPerformance},benchmark,limits:['Synthetic business actions and synthetic load; no production SLA demonstrated.','DFG measures observed succession; parallel conformance requires the versioned Petri net.','Projection, correction policies and organisation scoping are Flow code, not supplied by the algorithms.','Single-case projection does not demonstrate object-centric multi-order/mining semantics.']};
fs.writeFileSync(path.join(O,'mining.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({status:result.status,checks:checks.length,actual:result.actual,benchmark}));
