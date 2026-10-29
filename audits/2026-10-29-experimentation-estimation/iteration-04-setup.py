from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,urllib.request,hashlib,zipfile,time
ROOT=Path("C:/Dev/FLOW-Etude-Economique")
HERE=ROOT/"tmp/iteration04-runtime"
HERE.mkdir(parents=True,exist_ok=True)
items=[
 {"id":"jdk","url":"https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.12.1%2B1/OpenJDK21U-jdk_x64_windows_hotspot_21.0.12.1_1.zip","expected_sha256":"f9d6e191ab098c0d416e7d588a24420a8621cd2f4720dab2459b8b7b2d2d8b4e"},
 {"id":"postgresql","url":"https://get.enterprisedb.com/postgresql/postgresql-17.11-1-windows-x64-binaries.zip","expected_sha256":None}]
def get(item):
 start=time.monotonic(); archive=HERE/(item["id"]+".zip")
 if not archive.exists():
  req=urllib.request.Request(item["url"],headers={"User-Agent":"Mozilla/5.0"})
  with urllib.request.urlopen(req,timeout=120) as src,archive.open("wb") as dst:
   while chunk:=src.read(1024*1024): dst.write(chunk)
 h=hashlib.file_digest(archive.open("rb"),"sha256").hexdigest()
 if item["expected_sha256"] and h!=item["expected_sha256"]:raise ValueError("Checksum mismatch")
 target=(HERE/item["id"]).resolve();target.mkdir(exist_ok=True)
 with zipfile.ZipFile(archive) as z:
  for name in z.namelist():
   if item["id"]=="postgresql" and not name.startswith(("pgsql/bin/","pgsql/lib/","pgsql/share/")):continue
   dest=(target/name).resolve()
   if not dest.is_relative_to(target):raise ValueError("Zip target escapes runtime")
   z.extract(name,target)
 out={**item,"sha256":h,"archive_bytes":archive.stat().st_size,"directory":str(target),"download_extract_seconds":round(time.monotonic()-start,1)}
 print(json.dumps({"ready":out}),flush=True);return out
with ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(get,items))
runtime={"id":"iteration-04-runtime","artifacts":records,"java_home":str(next((HERE/"jdk").glob("jdk-*"))),"pg_bin":str(HERE/"postgresql/pgsql/bin"),"maven_home":"C:/Users/laure/.m2/wrapper/dists/apache-maven-3.9.16/0daed3be3ebd1c706f0e69e8b07c6b73f5cc4ea3dfce72a8d0ec2e849ca2ddb0","note":"Portable test runtimes only. JDK checksum checked against Adoptium metadata; PostgreSQL archive hash recorded, no publisher checksum comparison available."}
(ROOT/"audits/2026-10-29-experimentation-estimation/iteration-04-runtime.json").write_text(json.dumps(runtime,indent=2)+"\n",encoding="utf-8")
