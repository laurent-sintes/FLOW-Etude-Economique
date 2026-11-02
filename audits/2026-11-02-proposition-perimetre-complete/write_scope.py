from pathlib import Path
import json
OUT=Path(__file__).resolve().parent

def save(name,basis,cases,reason,rows):
    processes=[]
    for line in rows.strip().splitlines():
        id,label,bc,E,R,W,X=line.split('|')
        processes.append(dict(id=id,label=label,capabilities=['BC-'+f'{int(c):03}' for c in bc.split()],scenario_refs=cases.split(),trigger=label+' sur commande explicite ou résultat corrélé.',E=E.split() if E!='-' else [],R=R.split() if R!='-' else [],W=W.split() if W!='-' else [],X=X.split() if X!='-' else [],scope_reason=reason))
    (OUT/('scope-'+basis+'.json')).write_text(json.dumps(dict(id=name,basis=basis,assessment=reason,processes=processes),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
