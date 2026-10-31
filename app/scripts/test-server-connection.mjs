import assert from 'node:assert/strict';
import {test} from 'node:test';
import {monitorServer,SERVER_CHECK_INTERVAL,SERVER_CHECK_TIMEOUT,INITIAL_SERVER_STATUS} from '../src/serverConnection.ts';

const flush=()=>new Promise(resolve=>setImmediate(resolve));
function fixture({hidden=false,read}={}){
 const host=new EventTarget(),page=new EventTarget();page.hidden=hidden;
 const intervals=new Map(),timeouts=new Map();let sequence=0;
 host.setInterval=(fn,delay)=>{intervals.set(++sequence,{fn,delay});return sequence;};
 host.clearInterval=id=>intervals.delete(id);
 host.setTimeout=(fn,delay)=>{timeouts.set(++sequence,{fn,delay});return sequence;};
 host.clearTimeout=id=>timeouts.delete(id);
 let health={id:'flow-study',server_revision:'loaded'},failure=false,calls=0,state=INITIAL_SERVER_STATUS;
 const changes=[];
 const monitor=monitorServer({revision:'loaded',appId:'flow-study',window:host,document:page,
  onChange:value=>{state=value;changes.push(value);},
  readHealth:signal=>{calls++;return read?read(signal):failure?Promise.reject(Error('network')):Promise.resolve(health);},
 });
 return {monitor,host,page,intervals,timeouts,changes,get calls(){return calls;},get state(){return state;},
  fail(value=true){failure=value;},health(value){health=value;},
  async tick(){for(const task of intervals.values())task.fn();await flush();},
 };
}

test('healthy checks stay silent and do not re-render loaded pages',async()=>{
 const f=fixture();await flush();
 assert.equal(f.calls,1);assert.deepEqual(f.changes,[]);
 assert.equal([...f.intervals.values()][0].delay,5000);
 await f.tick();assert.equal(f.calls,2);assert.deepEqual(f.changes,[]);
 f.monitor.stop();
});

test('a stopped server is reported on the next active check and recovery clears the alert',async()=>{
 const f=fixture();await flush();f.fail();await f.tick();
 assert.deepEqual(f.state,{available:false,unreachable:true,checking:false});
 f.fail(false);await f.monitor.check();
 assert.deepEqual(f.state,INITIAL_SERVER_STATUS);
 assert.ok(f.changes.some(state=>state.checking));
 f.monitor.stop();
});

test('a restart offers the new version only after connectivity returns',async()=>{
 const f=fixture();await flush();f.fail();await f.tick();
 f.health({id:'flow-study',server_revision:'restarted'});f.fail(false);await f.tick();
 assert.deepEqual(f.state,{available:true,unreachable:false,checking:false});
 f.fail();await f.tick();assert.equal(f.state.unreachable,true);assert.equal(f.state.available,true);
 f.fail(false);f.health({id:'flow-study',server_revision:'loaded'});await f.tick();
 assert.deepEqual(f.state,INITIAL_SERVER_STATUS);
 f.monitor.stop();
});

test('timeouts abort a stalled health request and a later attempt can recover',async()=>{
 let stall=true;
 const f=fixture({read:signal=>stall?new Promise((resolve,reject)=>signal.addEventListener('abort',()=>reject(signal.reason),{once:true})):Promise.resolve({id:'flow-study',server_revision:'loaded'})});
 assert.equal([...f.timeouts.values()][0].delay,3000);
 [...f.timeouts.values()][0].fn();await flush();
 assert.equal(f.state.unreachable,true);assert.equal(f.timeouts.size,0);
 stall=false;await f.tick();assert.equal(f.state.unreachable,false);assert.equal(f.calls,2);
 f.monitor.stop();
});

test('checks resume on tab visibility, focus and network events without overlapping requests',async()=>{
 let complete;
 const f=fixture({hidden:true,read:()=>new Promise(resolve=>{complete=resolve;})});
 assert.equal(f.calls,0);await f.tick();assert.equal(f.calls,0);
 f.page.hidden=false;f.page.dispatchEvent(new Event('visibilitychange'));
 assert.equal(f.calls,1);
 f.host.dispatchEvent(new Event('focus'));f.host.dispatchEvent(new Event('online'));await f.tick();
 assert.equal(f.calls,1);
 complete({id:'flow-study',server_revision:'loaded'});await flush();
 f.host.dispatchEvent(new Event('offline'));assert.equal(f.calls,2);
 complete({id:'flow-study',server_revision:'loaded'});await flush();
 f.monitor.stop();
});

test('a manual retry is available even when background polling is paused',async()=>{
 const f=fixture({hidden:true});await f.monitor.check();
 assert.equal(f.calls,1);assert.deepEqual(f.changes,[]);f.monitor.stop();
});

test('an unexpected application or malformed health response is not accepted as connected',async()=>{
 const f=fixture();await flush();
 for(const value of [{id:'other',server_revision:'new'},{id:'flow-study'},null]){
  f.health(value);await f.monitor.check();assert.equal(f.state.unreachable,true);assert.equal(f.state.available,false);
 }
 f.monitor.stop();
});

test('cleanup aborts in-flight requests, removes listeners and ignores late results',async()=>{
 let finish,signal;
 const f=fixture({read:active=>{signal=active;return new Promise(resolve=>{finish=resolve;});}});
 assert.equal(f.calls,1);f.monitor.stop();assert.equal(signal.aborted,true);assert.equal(f.intervals.size,0);
 finish({id:'flow-study',server_revision:'new'});await flush();assert.equal(f.timeouts.size,0);
 f.host.dispatchEvent(new Event('focus'));f.host.dispatchEvent(new Event('online'));f.host.dispatchEvent(new Event('offline'));
 f.page.dispatchEvent(new Event('visibilitychange'));await f.monitor.check();
 assert.equal(f.calls,1);assert.deepEqual(f.changes,[]);
});

assert.equal(SERVER_CHECK_INTERVAL,5000);assert.equal(SERVER_CHECK_TIMEOUT,3000);
