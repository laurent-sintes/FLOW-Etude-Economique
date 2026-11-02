"""Read-only scope crosswalk. It neither estimates new effort nor adopts budgets."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
import yaml
from estimation_components import unpack_archives
CARTO=Path('C:/Dev/Beaumanoir Cartographie/modeles/backlog/model.yaml')

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):
    raw=path.read_text(encoding='utf-8')
    return json.loads(raw) if path.suffix=='.json' else yaml.safe_load(raw)
def save(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def collect():
    paths=['source/analyse-perimetre-core.yaml','source/estimations-core-retenues.yaml',
      'source/fonctions-produit-core.yaml','source/comparaison-solutions.yaml',
      'sources/cartographie-scm-2026-10-24.yaml',
      'audits/2026-10-30-core-adoption-09/archives.json',
      'audits/2026-11-01-proposition-references-oss/results.json',
      'audits/2026-10-30-stock-adoption-10/inputs.json',
      'audits/2026-10-30-stock-dimensionnement-05/inputs.json',
      'audits/2026-11-02-audit-politiques-allocation/results.json',
      str((OUT/'findings.json').relative_to(ROOT)).replace('\\','/')]
    inputs={p:digest(ROOT/p) for p in paths}
    carto_hash=digest(CARTO);m=read(CARTO)
    blocks=read(ROOT/paths[0])['blocs'];units=read(ROOT/paths[1])['units']
    frozen=read(ROOT/'sources/cartographie-scm-2026-10-24.yaml')
    old={n['id']:n for n in frozen['nodes']};nodes={n['id']:n for n in m['nodes']}
    native={b['capacite_id']:b['id'] for b in blocks}
    children={};parent={}
    for r in m['relations']:
        if r['type'] in ('contains','presents'):children.setdefault(r['source_id'],[]).append(r['target_id'])
        if r['type']=='contains':parent[r['target_id']]=r['source_id']
    visited=set();queue=['supply-chain-orchestration']
    while queue:
        id=queue.pop()
        if id in visited:continue
        visited.add(id);queue+=children.get(id,[])
    native_caps={id for id in visited if nodes[id]['kind']=='capability'}
    assert native_caps==set(native),'Scope capabilities differ from the estimation catalogue'
    scenarios=m['scenario_catalog']['scenarios'];scenario_ids={s['id'] for s in scenarios}
    paths=m['scenario_catalog']['paths'];path_index={p['id']:p for p in paths}
    refs=[];by_bc={b['id']:[] for b in blocks}
    for path in paths:
        assert path['scenario_id'] in scenario_ids
        for step in path['steps']:
            for c in step.get('contributions',[]):
                id=c['node_id'];assert id in nodes
                origin=id;seen=set()
                while id not in native and id in parent and id not in seen:
                    seen.add(id);id=parent[id]
                ref=dict(scenario_id=path['scenario_id'],path_id=path['id'],step_id=step['id'],node_id=origin,
                         node_kind=nodes[origin]['kind'],role=c['role'],bc_ref=native.get(id))
                refs.append(ref)
                if ref['bc_ref']:by_bc[ref['bc_ref']].append(ref)
    findings=read(OUT/'findings.json')['findings']
    for f in findings:
        assert set(f['capabilities'])<=set(by_bc)
        # Some catalogue variants are paths of a parent scenario, not new scenarios.
        f['path_refs']=[id for id in f['scenarios'] if id in path_index]
        f['scenarios']=sorted({path_index[id]['scenario_id'] if id in path_index else id for id in f['scenarios']})
        assert set(f['scenarios'])<=scenario_ids,(f['id'],f['scenarios'])
    families=unpack_archives(read(ROOT/'audits/2026-10-30-core-adoption-09/archives.json'))['proposal_inputs']['families']
    revision=read(ROOT/'audits/2026-11-01-proposition-references-oss/results.json')
    unit_for={c['id']:u for u in units for c in u.get('capabilities',[])}
    rows=[]
    for b in blocks:
        id=b['capacite_id'];node=nodes[id];u=unit_for[b['id']]
        behavior_ids=[x for x in children.get(id,[]) if nodes[x]['kind']=='behavior']
        semantic=['name','definition','scope','examples','pedagogical_description']
        rows.append(dict(bc_ref=b['id'],native_id=id,name=node['fields']['name'],
          native_fields=node['fields'],source_refs=node.get('source_refs',[]),review=node.get('review'),
          semantic_changes_since_capture=[k for k in semantic if node['fields'].get(k)!=old[id]['fields'].get(k)],
          behaviors=[nodes[x] for x in behavior_ids],functions=b['fonctions'],boundary=b.get('frontiere'),
          unit_id=u['id'],unit_jh=u['total_jh'],
          family_refs=[f['slug'] for f in families if b['id'] in f['capabilities']],
          scenario_refs=sorted({r['scenario_id'] for r in by_bc[b['id']]}),scenario_contributions=by_bc[b['id']],
          finding_refs=[f['id'] for f in findings if b['id'] in f['capabilities']],
          assessment='perimetre_a_eprouver' if any(b['id'] in f['capabilities'] for f in findings) else 'aucun_ecart_identifie_dans_cette_passe'))
    assert len(rows)==88 and len(set(r['native_id'] for r in rows))==88
    assert len(units)==11 and sum(u['total_jh'] for u in units)==5950
    assert sum(len(r['behaviors']) for r in rows)==74
    result=dict(id='scope-scenarios-audit-2026-11-02',date='2026-11-02',status='scope_audit_not_budget_adoption',
      source=dict(path=str(CARTO),sha256=carto_hash,space=m['space'],version=m['version'],as_of=m['as_of'],
                  warning='Backlog courant lu pour audit. Les états de revue sont conservés. Ce n’est pas une nouvelle publication Atlas.'),
      inputs_sha256=inputs,script_sha256=digest(Path(__file__)),
      counts=dict(capabilities=len(rows),behaviors=74,units=len(units),scenarios=len(scenarios),paths=len(paths),
          contributions=len(refs),capabilities_with_scenarios=sum(bool(r['scenario_refs']) for r in rows),
          unchanged_capability_semantics=sum(not r['semantic_changes_since_capture'] for r in rows)),
      adopted_jh=sum(u['total_jh'] for u in units),net_extra_jh=None,
      method='Lecture des définitions, périmètres, 74 comportements, exemples et 50 parcours. Rapprochement explicite avec fonctions, schémas, hypothèses et analogues des preuves existantes. Pas de qualification exhaustive nouvelle des logiciels OSS ni de nouveau comptage COSMIC.',
      scenarios=scenarios,paths=paths,contributions=refs,
      references=[nodes[x] for x in sorted(visited) if nodes[x]['kind']=='reference'],
      external_contributors=[nodes[x] for x in sorted({r['node_id'] for r in refs if r['node_id'] not in visited})],
      families=[{k:f[k] for k in ('id','slug','scope','capabilities','functions','schemas','module_names','quantity','extension_fraction') if k in f} for f in families],
      adopted_analogue_details=[dict(id=u['id'],details=u.get('calculation_details',{})) for u in revision['units']],
      professional_functions=read(ROOT/'source/fonctions-produit-core.yaml')['functions'],
      units=[dict(id=u['id'],label=u['label'],jh=u['total_jh'],capability_refs=[c['id'] for c in u.get('capabilities',[])],
                   scope=u.get('includes',[]),assumptions=u.get('assumptions',[]),exclusions=u.get('exclusions',[]),
                   finding_refs=sorted({f['id'] for f in findings if set(f['capabilities'])&{c['id'] for c in u.get('capabilities',[])}})) for u in units],
      findings=findings,capabilities=rows,
      checks=dict(all_capabilities_in_exactly_one_active_unit=len(unit_for)==len(rows),all_scenario_targets_exist=True,
                  all_cases_resolve=True,all_behavior_parents_known=True,no_budget_modified=True))
    # These product lots have their own scope, outside the native capability catalogue.
    for u in result['units']:
        if u['id']=='supply-workbenches-java-spring':u['finding_refs']=['R12']
        if u['id']=='professional-it-java-spring':u['finding_refs']=['R11','R14']
    assert result['checks']['all_capabilities_in_exactly_one_active_unit']
    for p,h in inputs.items():assert digest(ROOT/p)==h,('Input changed during scan',p)
    assert digest(CARTO)==carto_hash,'Cartography changed during scan'
    return result

def render(r):
    lines=['# Revue du périmètre estimé à partir des scénarios FLOW','',
      '**Les 88 capacités sont présentes dans les neuf lots métier. Le risque principal est leur profondeur fonctionnelle, pas l’oubli d’un intitulé.** Les deux lots supplémentaires portent les ateliers visuels et les fonctions IT du produit. Le total adopté reste à **5 950 JH**. Aucun supplément global n’est calculé par cet audit.','',
      'La lecture porte sur les **88 capacités, 74 comportements, 43 scénarios et 50 parcours** du backlog courant Beaumanoir Cartographie. Les noms, définitions, périmètres, exemples et descriptions pédagogiques des capacités ne diffèrent pas de la capture du 24 octobre utilisée pour l’étude. Les scénarios ne figuraient pas dans cette capture. Ils servent ici à éprouver les fonctions et hypothèses de taille. Leurs statuts de revue sont conservés dans la preuve.','',
      '## Ce qui doit être repris en priorité','',
      'Le correctif des politiques est une omission déjà établie. Six sujets demandent en priorité un examen de leur profondeur : consommation des enveloppes de groupe, arbitrage collectif du carnet, promesse à capacité finie, optimisation multi-échelon, chargements/tournées et engagements entre sociétés. Les migrations de parcours et les ateliers visuels demandent aussi une justification détaillée. Une fonction décrite dans un schéma est prévue, mais sa présence ne démontre ni l’adéquation de l’analogue ni la suffisance de la charge.','',
      '**Le correctif à 430 JH du lot politiques n’épuise pas la question.** Il conserve le comptage éligibilité/disposition et laisse à vérifier le financement de l’application des droits collectifs aux consommations. Il ne doit pas devenir le financement implicite de tous les sujets voisins.','',
      '## Lecture des onze lots','',
      '| Lot | JH adoptés | Points à examiner |','| --- | ---: | --- |']
    for u in r['units']:lines.append('| '+u['label']+' | '+str(u['jh'])+' | '+', '.join(u['finding_refs'])+' |')
    lines+=['','Les JH indiqués sont ceux des lots entiers. Les allocations de 63 JH au carnet, 39 JH à la promesse, 228 JH à l’optimisation et 85 JH à la planification de services ne sont pas des estimations indépendantes. Les recalculer exige de reprendre le lot cohérent de décisions et ses réutilisations.','',
      '## Écarts et contrôles par sujet','']
    scenario_names={s['id']:s['title'] for s in r['scenarios']}
    for f in r['findings']:
        lines+=['### '+f['id']+' '+f['title'],'',
          '**'+f['status'].replace('_',' ')+' — priorité '+str(f['priority'])+'.** '+f['observation'],'',
          '**Périmètre à vérifier.** '+f['gap'],'',
          '**Financement à préserver.** '+f['existing_funding'],'',
          '**Travail demandé.** '+f['next_action'],'',
          '**Cas d’acceptation.** '+f['acceptance'],'',
          'Capacités : '+', '.join(f['capabilities'])+'. Scénarios : '+', '.join(scenario_names[x]+' (`'+x+'`)' for x in f['scenarios'])+'.','']
    lines+=['## Ce qui ne constitue pas un nouveau manque','',
      '- Consommation de prévision, plan de demande, plan d’approvisionnement et rapprochement sont explicitement prévus dans Master Plan. Les scénarios doivent éprouver leurs règles et leur taille.',
      '- Avoir, remboursement partiel, remplacement et retours fournisseur ont des fonctions et schémas prévus. Leur suivi et leurs résultats doivent être réconciliés entre commandes, prestations et dossiers.',
      '- Les douze contrats de prestation ne sont pas douze moteurs WMS ou ateliers de production. Le Core porte les demandes, engagements, faits et résultats. L’exécutant conserve ses opérations.',
      '- Références produit, variantes et assortiments sont prévues. La conception produit, la décision d’assortiment commercial et la fixation des prix restent dans leurs domaines sources.',
      '- L’Office FLOW finance l’équipe transverse. Il ne remplace pas les fonctions du produit et ne doit pas être ajouté au titre de ces écarts logiciels.','',
      '## Contrôle de chaque capacité','',
      'Le tableau établit le rattachement, les cas explicitement reliés et les sujets de revue. Une absence de scénario explicite ne signifie ni absence de besoin ni charge nulle. Une contribution à un référentiel est conservée comme telle et n’est pas transformée artificiellement en contribution d’une capacité. Les liens de dépendance ne prouvent pas un financement.','',
      '| Capacité | Lot | Scénarios explicites | Points de revue |','| --- | --- | ---: | --- |']
    for c in r['capabilities']:lines.append('| '+c['bc_ref']+' '+c['name']+' | '+c['unit_id'].replace('-java-spring','')+' | '+str(len(c['scenario_refs']))+' | '+(', '.join(c['finding_refs']) or 'Aucun écart identifié dans cette passe')+' |')
    lines+=['','## Suite du chiffrage','',
      'Pour chaque sujet prioritaire, construire la liste des résultats et transactions métier nécessaires, désigner leur lot de financement et vérifier ce qui y est déjà compté. Déplier les processus COSMIC concernés avec leurs échanges de données, puis choisir ou mesurer des analogues couvrant réellement ces mêmes responsabilités. Réévaluer les unités cohérentes après déduction des mécanismes partagés. Cette passe n’applique ni majoration générale ni forfait par scénario.','',
      'Les interfaces et règles propres aux SI et aux sociétés Beaumanoir relèvent de l’intégration. Les services génériques, contrôles métier et outils de configuration du produit relèvent de sa construction. Un coût de produit Buy dépend de son inclusion contractuelle et ne se déduit pas de la charge Make.','',
      '## Preuves et reproduction','',
      '- [Matrice complète, périmètres, comportements et parcours](results.json).',
      '- [Constats et critères de contrôle](findings.json).',
      '- [Script de rapprochement et contrôles](scan.py).',
      '- [Audit et proposition sur les politiques](../2026-11-02-audit-politiques-allocation/audit.md).','',
      'Rejouer avec le Python du projet et les dépendances YAML : `python audits/2026-11-02-revue-perimetre-scenarios/scan.py`. Le script lit le projet Cartographie sans le modifier et vérifie que les entrées économiques restent identiques. `--verify` contrôle la preuve enregistrée et ses empreintes sans écrire.','',
      'Le rapprochement automatique contrôle les identifiants, rattachements et totaux. Les constats de pertinence sont une analyse de périmètre, pas une certification de couverture ni une nouvelle mesure de productivité. Les quatre OSS ne sont pas rescannés intégralement dans cette passe : leurs preuves de calcul déjà archivées sont confrontées aux scénarios métier.','']
    (OUT/'audit.md').write_text('\n'.join(lines),encoding='utf-8')

if __name__=='__main__':
    if '--verify' in sys.argv:
        r=read(OUT/'results.json')
        assert digest(CARTO)==r['source']['sha256']
        for p,h in r['inputs_sha256'].items():assert digest(ROOT/p)==h,p
        assert digest(Path(__file__))==r['script_sha256']
        assert len(r['capabilities'])==88 and len({c['bc_ref'] for c in r['capabilities']})==88
        assert all(r['checks'].values()) and r['adopted_jh']==5950
        assert len(r['scenarios'])==43 and len(r['paths'])==50
        print(json.dumps(dict(verified=True,**r['counts']),ensure_ascii=False))
    else:
        r=collect();save('results.json',r);render(r)
        print(json.dumps(r['counts'],ensure_ascii=False))
