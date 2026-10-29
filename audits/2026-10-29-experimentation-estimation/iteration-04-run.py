"""Execute bounded witnesses in a disposable local PostgreSQL cluster; never use an existing database."""
from pathlib import Path
import argparse,json,os,subprocess,secrets,socket,hashlib,datetime
ROOT=Path("C:/Dev/FLOW-Etude-Economique")
AUDIT=ROOT/"audits/2026-10-29-experimentation-estimation"
RUNTIME=ROOT/"tmp/iteration04-runtime"
cfg=json.loads((AUDIT/"iteration-04-runtime.json").read_text(encoding="utf-8"))
JAVA=Path(cfg["java_home"]);PG=Path(cfg["pg_bin"]);MVN=Path(cfg["maven_home"])/"bin/mvn.cmd"
FLAGS=subprocess.CREATE_NO_WINDOW if os.name=="nt" else 0
def run(args,env=None,check=True):
 if Path(str(args[0])).name.lower()=="pg_ctl.exe":
  # PostgreSQL inherits Windows pipe handles; use a regular file so communicate
  # does not wait for a live server to close the pipe after pg_ctl has returned.
  output=RUNTIME/"pgctl-last-command.log"
  with output.open("w",encoding="utf-8") as log:
   p=subprocess.run([str(a) for a in args],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=FLAGS,timeout=60)
  p.stdout=output.read_text(encoding="utf-8",errors="replace")
 else:
  p=subprocess.run([str(a) for a in args],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8",errors="replace",creationflags=FLAGS)
 if p.stdout: print(p.stdout,flush=True)
 if check and p.returncode:raise RuntimeError("Command failed: "+str(args[0])+" "+str(p.returncode))
 return p
ap=argparse.ArgumentParser();ap.add_argument("--prepare",action="store_true");ap.add_argument("--test",default=None);ap.add_argument("--label",default="initial")
args=ap.parse_args()
env=os.environ.copy();env["JAVA_HOME"]=str(JAVA);env["PATH"]=str(JAVA/"bin")+";"+str(PG)+";"+env["PATH"]
mvn=["cmd.exe","/d","/c",MVN,"-B","-ntp","-f",AUDIT/"iteration-04-prototype/pom.xml","-Dmaven.repo.local="+str(RUNTIME/"m2")]
if args.prepare:
 p=run(mvn+["dependency:go-offline"],env,False)
 (AUDIT/"iteration-04-maven-prepare.log").write_text(p.stdout,encoding="utf-8")
 raise SystemExit(p.returncode)
cluster=(RUNTIME/"cluster").resolve()
if not cluster.is_relative_to(RUNTIME.resolve()):raise RuntimeError("Cluster path outside runtime")
pwfile=RUNTIME/"postgres-test-password.txt"
if not pwfile.exists():pwfile.write_text(secrets.token_urlsafe(32),encoding="ascii")
password=pwfile.read_text(encoding="ascii").strip()
if not (cluster/"PG_VERSION").exists():
 run([PG/"initdb.exe","-D",cluster,"-U","audit4","--pwfile="+str(pwfile),"--auth-host=scram-sha-256","--auth-local=scram-sha-256","--encoding=UTF8","--locale=C"])
if (cluster/"postmaster.pid").exists():raise RuntimeError("Cluster already running; inspect ownership before proceeding")
with socket.socket() as sock:
 sock.bind(("127.0.0.1",0));port=sock.getsockname()[1]
started=False
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
try:
 run([PG/"pg_ctl.exe","-D",cluster,"-l",RUNTIME/"postgresql.log","-o",f"-h 127.0.0.1 -p {port} -c max_connections=30","-w","start"]);started=True
 env["PGPASSWORD"]=password
 db=run([PG/"psql.exe","-h","127.0.0.1","-p",str(port),"-U","audit4","-d","postgres","-tAc","SELECT 1 FROM pg_database WHERE datname='flowaudit4'"],env)
 if db.stdout.strip()!="1":run([PG/"createdb.exe","-h","127.0.0.1","-p",str(port),"-U","audit4","flowaudit4"],env)
 env.pop("PGPASSWORD",None)
 env.update(FLOW_AUDIT_JDBC_URL=f"jdbc:postgresql://127.0.0.1:{port}/flowaudit4",FLOW_AUDIT_JDBC_USER="audit4",FLOW_AUDIT_JDBC_PASSWORD=password)
 versions={"java":run([JAVA/"bin/java.exe","-version"]).stdout.strip(),"postgresql":run([PG/"postgres.exe","--version"]).stdout.strip()}
 if args.test:mvn+=["-Dtest="+args.test]
 p=run(mvn+["test"],env,False)
 (AUDIT/f"iteration-04-run-{args.label}.log").write_text(p.stdout,encoding="utf-8")
 reports=AUDIT/"iteration-04-prototype/target/surefire-reports"
 archive=AUDIT/("iteration-04-test-results-"+args.label);archive.mkdir(exist_ok=True)
 if reports.exists():
  for f in reports.glob("TEST-*.xml"):
   if args.test and f.name != "TEST-flow.audit4."+args.test+".xml": continue
   (archive/f.name).write_bytes(f.read_bytes())
 record={"id":"iteration-04-run-"+args.label,"started_utc":start,"finished_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"exit_code":p.returncode,"versions":versions,"database":"isolated local PostgreSQL; generated test data only","runtime_ref":"iteration-04-runtime.json","test_filter":args.test,"source_sha256":{str(f.relative_to(AUDIT)):hashlib.file_digest(f.open("rb"),"sha256").hexdigest() for f in (AUDIT/"iteration-04-prototype").rglob("*.java")},"maven_pom_sha256":hashlib.file_digest((AUDIT/"iteration-04-prototype/pom.xml").open("rb"),"sha256").hexdigest(),"elapsed_is_human_effort":False}
finally:
 if started:
  stopped=run([PG/"pg_ctl.exe","-D",cluster,"-m","fast","-w","stop"],check=False)
  if "record" in locals():record["database_stopped"]=stopped.returncode==0
 if "record" in locals():(AUDIT/f"iteration-04-run-{args.label}.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
raise SystemExit(p.returncode)
