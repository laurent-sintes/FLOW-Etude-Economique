"""Reproducible local Java solver experiment. No active economic source is written."""
from pathlib import Path
import subprocess,os,json,datetime,hashlib,platform
ROOT=Path(__file__).resolve().parents[2]
A=Path(__file__).resolve().parent
P=A/'iteration-15-prototype'
cfg=json.loads((A/'iteration-04-runtime.json').read_text(encoding='utf-8'))
env=os.environ.copy()
env['JAVA_HOME']=cfg['java_home']
env['PATH']=str(Path(cfg['java_home'])/'bin')+os.pathsep+env['PATH']
mvn=[str(Path(cfg['maven_home'])/'bin/mvn.cmd'),'-B','-ntp','-f',str(P/'pom.xml'),'-Dmaven.repo.local='+str(ROOT/'tmp/iteration04-runtime/m2')]
def run(args,log,timeout):
 with (A/log).open('w',encoding='utf-8') as out:
  p=subprocess.run(args,cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT,timeout=timeout,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 if p.returncode: raise RuntimeError(log+' failed: '+str(p.returncode))
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
run(mvn+['compile','dependency:build-classpath','-Dmdep.outputFile='+str(P/'target/classpath.txt')],'iteration-15-build.log',420)
cp=str(P/'target/classes')+os.pathsep+(P/'target/classpath.txt').read_text().strip()
java=str(Path(cfg['java_home'])/'bin/java.exe')
run([java,'-Xms128m','-Xmx1g','-Dorg.slf4j.simpleLogger.defaultLogLevel=warn','-cp',cp,'flow.audit15.Compare',str(A/'iteration-15-cases.json'),str(A/'iteration-15-raw.json')],'iteration-15-execution.log',480)
jars=[]
for path in cp.split(os.pathsep):
 f=Path(path)
 if f.is_file(): jars.append({'name':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size})
meta={'started_utc':started,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'java':subprocess.check_output([java,'-version'],stderr=subprocess.STDOUT,text=True).strip(),'os':platform.platform(),'logical_cpus':os.cpu_count(),'heap_limit':'1 GiB','isolated_process':True,'spring':'context wiring only; no HTTP, PostgreSQL, concurrency or deployment benchmark','versions':{'timefold':'1.26.0','ortools':'9.14.6206','spring_boot_dependency_management':'3.5.7'},'artifacts':jars,'sources':{str(f.relative_to(A)).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest() for f in P.rglob('*.java')}}
(A/'iteration-15-runtime.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Java experiments completed; raw results and binary provenance saved.')
