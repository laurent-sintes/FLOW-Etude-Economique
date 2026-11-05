"""Prepare an atomic adoption of the reviewed Master Data and SCM reference scope."""
from copy import deepcopy
from collections import Counter
from pathlib import Path
from validate_stacks import ROOT,read
from adoption_transaction import require,encode,digest
from estimation_inputs import digest as object_digest,historical_dependencies
from estimation_preparation import prepare
from estimation_calculation import formula,rounded
from core_product_estimate import apportioned

MD='master-data-java-spring'
OR='operational-references-java-spring'


def project_scope(proposal,study,registry,documents,note):
    from adopt_core import SOURCES,yaml_bytes,describe
    require(set(proposal)=={'format','method','date','revision_ref'} and proposal['format']==1 and proposal['method']=='native_scope_adoption','Invalid scope adoption request')
    require(proposal['revision_ref']=='source/revision-master-data.yaml' and note.strip(),'Unknown scope adoption or missing instruction')
    revision=read(ROOT/proposal['revision_ref']);require(revision['status']=='proposal','Scope revision already adopted')
    R=study.content['delivery_organisation']['scope_revision'];before=describe(study)
    require(R['proposed']['jh']==3070 and R['reference']['jh']==1600 and R['scope']['total_capabilities']==116,'Scope decision changed')
    source={p:read(ROOT/p) for p in SOURCES};retained=source[SOURCES[0]];previous=deepcopy(retained['units']);old=next(u for u in previous if u['id']==MD)
    valued=next(o['core_units'] for o in study.economic['options'] if o['stack']=='java-spring');reference=next(u for u in valued if u['id']==MD)
    folder='audits/'+proposal['date']+'-adoption-master-data-scm';require(not (ROOT/folder).exists(),'Immutable scope adoption folder already exists')
    paths={k:folder+'/'+k+'.json' for k in ('basis','scope','decision')}
    basis=dict(id='native-scope-adoption-basis',registry=deepcopy(registry),source_documents={p:read(ROOT/p) for p in ('source/analyse-perimetre-core.yaml','source/qualification-buy.yaml','source/comparaison-solutions.yaml','source/lecture-metier.yaml')},units=previous,reference_unit=deepcopy(reference),previous_core_units=deepcopy(valued),input_hashes={p:v['sha256'] for p,v in registry['proofs'].items()})
    changes={};basis_raw=encode(basis);changes[paths['basis']]=basis_raw
    raw_native=read(ROOT/revision['capture']['path']);nodes={n['id']:n for n in raw_native['nodes']};children={}
    for r in raw_native['relations']:
        if r['type'] in ('presents','contains'):children.setdefault(r['source_id'],[]).append(r['target_id'])
    selected={'system-business-operations'}
    def collect(id):
        if id in selected:return
        selected.add(id)
        for c in children.get(id,[]):collect(c)
    for id in ('domain-master-data','supply-chain-orchestration'):collect(id)
    capture=dict(id='flow-core-system-native-input',date_capture=proposal['date'],domaine_id='system-business-operations',provenance=dict(fichier=revision['capture']['origin'],sha256=revision['capture']['sha256'],version=raw_native['version']),nodes=[n for n in raw_native['nodes'] if n['id'] in selected],relations=[r for r in raw_native['relations'] if r['source_id'] in selected and r['target_id'] in selected])
    capture_path='sources/cartographie-core-system-'+proposal['date']+'.yaml';capture_raw=yaml_bytes(capture);changes[capture_path]=capture_raw
    native_source=dict(version=1,source=capture_path,sha256=digest(capture_raw),domain_id='system-business-operations');changes['source/referentiel-capacites.yaml']=yaml_bytes(native_source)
    analysis=read(ROOT/'source/analyse-perimetre-core.yaml');capids={id for id in selected if nodes[id]['kind']=='capability'}
    retired={b['capacite_id'] for b in analysis['blocs']}-capids;retired_bc={b['id'] for b in analysis['blocs'] if b['capacite_id'] in retired}
    analysis['blocs']=[b for b in analysis['blocs'] if b['capacite_id'] in capids]
    paths_by_id={r['target_id']:r['source_id'] for r in capture['relations'] if r['type'] in ('contains','presents')}
    known={b['capacite_id'] for b in analysis['blocs']};new_blocks=[]
    for n in capture['nodes']:
        if n['kind']!='capability' or n['id'] in known:continue
        id=n['id'];chain=[id]
        while nodes[chain[0]]['kind']!='domain':chain.insert(0,paths_by_id[chain[0]])
        bc='BC-'+str(89+len(new_blocks)).zfill(3)
        new_blocks.append(dict(id=bc,capacite_id=id,chemin=chain,fonctions=[dict(id=bc+'.01',resultat=n['fields']['definition'])],variantes_source=[],frontiere='Périmètre métier générique de la capacité. Les adaptations des SI, autorités Beaumanoir, volumes et exploitation restent à dimensionner.'))
    analysis['blocs']+=new_blocks
    ingestion=next(b for b in analysis['blocs'] if b['capacite_id']=='master-data-ingestion')
    ingestion['fonctions']=[dict(id='BC-002.01',resultat='Recevoir les versions de référence publiées par le MDM et contrôler leur provenance et leur validité'),dict(id='BC-002.02',resultat='Actualiser les vues opérationnelles et signaler les versions manquantes ou incompatibles'),dict(id='BC-002.03',resultat='Accuser la réception, tracer les rejets et reprendre une version corrigée sans modifier la donnée maître')]
    ingestion['frontiere']='Vues locales de consultation alimentées par Master Data. La consolidation, la qualité et la correction du référentiel maître appartiennent au domaine producteur.'
    changes['source/analyse-perimetre-core.yaml']=yaml_bytes(analysis)
    md_caps=[dict(id=b['id'],native_id=b['capacite_id']) for b in new_blocks];or_caps=[dict(id=ingestion['id'],native_id=ingestion['capacite_id'])]
    base_contract=next(c for c in registry['calculations'] if c['unit_id']==MD);prepared=prepare(documents,base_contract,registry,formula,use_cache=True)
    cc=prepared['cocomo'];E=formula('cocomo_exponent',B=cc['B'],SF_sum=cc['SF_sum']);F=formula('schedule_exponent',D=cc['D'],E=E,B=cc['B'])
    current_contract=deepcopy(base_contract);new_contract=deepcopy(base_contract);new_contract.update(id=OR+'-v1',unit_id=OR)
    new_mechanism=dict(id='scm-operational-reference-views',label='Vues opérationnelles et réception des références publiées',stack='java-spring',funding_owner=OR,basis=dict(kind='component_domain',scope='scm-operational-reference-views'),note='Conception, vues, réception, validité, reprises et qualification locales. Les moteurs MDM restent financés par le producteur.')
    registry['mechanisms'].append(new_mechanism)
    new_contract['funding_claims']=[dict(mechanism=new_mechanism['id'],mode='funded')]+[dict(mechanism=m['mechanism'],mode='consumed') for m in base_contract['funding_claims']]
    units_by_lot={};proof_units=[]
    for lot_ref,uid,caps,level,native_id,contract in [('master-data',MD,md_caps,'domain','domain-master-data',current_contract),('operational-references',OR,or_caps,'area','business-references',new_contract)]:
        lot=next(l for l in R['lots'] if l['id']==lot_ref);groups=[g for g in R['groups'] if g['id'] in lot['group_refs']]
        roles={r['id']:sum(x['net_jh'] for g in groups for x in g['roles'] if x['id']==r['id']) for r in old['roles']}
        u=deepcopy(old);u.update(id=uid,label='Master Data Java/Spring' if uid==MD else 'Operational References SCM Java/Spring',capabilities=caps,total_jh=lot['jh'],decision_date=proposal['date'],includes=[p['deliverable'] for p in revision['packages'] if p['group'] in lot['group_refs']],method='Estimation détaillée par livrable',calculation=dict(id=contract['id']))
        u['role_assumption']='Ventilation des ensembles de travaux validés. Réutilisation des proportions antérieures et des tarifs courants, sans gain forfaitaire supplémentaire.'
        u['assumptions']=[dict(id='scope',hypothesis='Le domaine Master Data couvre les services producteurs et les familles de données.' if uid==MD else 'Operational References comprend les vues locales et leur alimentation par les versions publiées du MDM, avec conception, contrôles et reprises.',trigger='Modification des fonctions, familles, volumes ou niveaux de service.',effect='Réexaminer les livrables concernés. Les adaptations Beaumanoir et le fonctionnement supplémentaires restent à dimensionner.'),dict(id='method',hypothesis='Somme des livrables adoptés, avec réutilisation des socles déjà financés. Les références COCOMO et COSMIC sont historiques.',trigger='Premières réalisations et mesures de productivité comparables.',effect='Confronter les hypothèses aux travaux observés sans transformer les contrôles historiques en mesures du nouveau périmètre.')]
        for r in u['roles']:r['jh']=roles[r['id']]
        months=formula('cocomo_schedule',C=cc['C'],JH=u['total_jh'],effort_phase_factor=cc['effort_phase_factor'],day_hours=cc['day_hours'],month_hours=cc['month_hours'],SCED=cc['SCED'],F=F,schedule_phase_factor=cc['schedule_phase_factor'])
        u['months']=rounded(months,prepared['allocation'].get('schedule_rounding_months',1));u['schedule']['unrounded_months']=months;u['schedule']['explanation']='Projection indicative depuis les JH adoptés et les paramètres calendaires historiques. Le calendrier global et la capacité des équipes restent à confirmer.'
        u['crosscheck']['explanation']='Contrôle COSMIC historique du lot antérieur, conservé comme preuve. Aucun comptage comparable du nouveau périmètre n’est établi.'
        selected_blocks=[b for b in analysis['blocs'] if b['id'] in {c['id'] for c in caps}]
        contract.update(recipe='native_scope_adoption_v1',scope=dict(level=level,native_id=native_id,capabilities=caps,native_source=native_source,analysis_sha256=object_digest(selected_blocks),decision_scope_sha256=object_digest({k:u[k] for k in ('capabilities','includes','excludes')})),inputs=dict(revision_basis=paths['basis'],revision_proposal=paths['scope'],revision_hypotheses=paths['decision']))
        contract['comparison']['service_note']='Les charges retenues proviennent des livrables adoptés. Les références COCOMO et COSMIC sont historiques et ne mesurent pas le nouveau périmètre.'
        units_by_lot[uid]=u
        proof_units.append(dict(id=uid,lot_ref=lot_ref,total_jh=u['total_jh'],roles=roles,scope=deepcopy(contract['scope']),funding_claims=deepcopy(contract['funding_claims']),package_refs=[p['id'] for p in revision['packages'] if p['group'] in lot['group_refs']],funded_work_ref=new_mechanism['id'] if uid==OR else 'master-data-common-domain'))
    retained['units']=[v for u in previous for v in ([units_by_lot[MD],units_by_lot[OR]] if u['id']==MD else [u])]
    registry['calculations']=[current_contract if c['unit_id']==MD else c for c in registry['calculations']]+[new_contract]
    scope=dict(id='adopted-native-scope',revision=deepcopy(revision),native_source=native_source,native_capture=capture,analysis=analysis,analysis_digest=object_digest(analysis['blocs']),units=proof_units,input_hashes={paths['basis']:digest(basis_raw)})
    scope_raw=encode(scope);changes[paths['scope']]=scope_raw
    decision=deepcopy(read(ROOT/source['source/proposition-produit-core.yaml']['adoption']['revision']['path']))
    decision.update(id='native-scope-master-data-scm-adoption',date=proposal['date'],status='adopted',decision_status='adopted',user_decision=note,scope_revision_id=revision['id'],adopted_jh=before['total_jh'],proposal_jh=R['core_proposed']['jh'],delta_jh=R['delta']['jh'],delta_pct=100*R['delta']['jh']/before['total_jh'],previous_cost_eur_ht=before['cost_eur_ht'],construction_cost_eur_ht=R['core_proposed']['cost_eur_ht'],scope_change='Master Data et Supply Chain Management. Remplacement du lot historique par deux financements distincts, sans modifier les autres décisions.',inputs_sha256={paths['basis']:digest(basis_raw),paths['scope']:digest(scope_raw)})
    previous_decisions={u['id']:u for u in decision['units']};decision['units']=[]
    for u in retained['units']:
        row=deepcopy(previous_decisions.get(u['id'],previous_decisions[MD]));old_jh=next((v['total_jh'] for v in previous if v['id']==u['id']),0)
        row.update(id=u['id'],label=u['label'],capabilities=deepcopy(u['capabilities']),adopted_jh=old_jh,proposal_jh=u['total_jh'],delta_jh=u['total_jh']-old_jh);decision['units'].append(row)
    for s in decision['sensitivity']:
        s['total_jh']=sum(rounded(formula('cosmic_effort',CFP=next(v for v in valued if v['id']==u['id'])['trace']['CFP'],hours_per_CFP=s['value'],factor=1,day_hours=7),10) if u['method']=='COSMIC × ISBSG' else u['total_jh'] for u in retained['units'])
    decision_raw=encode(decision);changes[paths['decision']]=decision_raw;decision_ref=dict(path=paths['decision'],sha256=digest(decision_raw));baseline_ref=dict(path=paths['basis'],sha256=digest(basis_raw))
    for u in retained['units']:
        if u['id'] in units_by_lot:u['provenance']=dict(**decision_ref,explanation='Adoption de deux lots distincts sur le nouveau périmètre. Conception des vues Operational References incluse. Les preuves historiques restent inchangées.')
    for name,raw in list(changes.items()):
        if not name.endswith('.json'):continue
        doc=__import__('json').loads(raw);deps=historical_dependencies(name,doc);registry['proofs'][name]=dict(sha256=digest(raw),kind='calculation_evidence',dependencies=[dict(path=p,sha256=h) for p,h in deps.items()])
    source[SOURCES[0]]=retained;source[SOURCES[1]]=registry
    f=source['source/fonctions-produit-core.yaml'];allocation=next(a for a in f['allocations'] if a['unit_id']==MD)
    for uid in (MD,OR):
        a=allocation if uid==MD else deepcopy(allocation);a['unit_id']=uid;a['evidence_refs'].append(paths['decision']);roles={r['id']:r['jh'] for r in units_by_lot[uid]['roles']};support=apportioned(90 if uid==MD else 0,roles)
        a['basis']='La traçabilité et la protection génériques MDM13 représentent 90 JH Support. Les autres livrables métier, et les vues opérationnelles consommatrices, relèvent du Core Domain. La finalité ne dépend pas des rôles.'
        for share in a['shares']:share['jh_by_role']={r:support[r] if share['purpose_id']=='support' else v-support[r] for r,v in roles.items()}
        if uid==OR:f['allocations'].append(a)
    for fn in f['functions']:fn['capability_refs']=[id for id in fn['capability_refs'] if id not in retired_bc]
    product=source['source/proposition-produit-core.yaml'];product['adoption']['revision']=decision_ref;product['adoption']['unit_ids'].insert(product['adoption']['unit_ids'].index(MD)+1,OR);product['adoption']['decision_date']=proposal['date']
    source['source/evaluation-charges-brutes.yaml']['proposal']=dict(**decision_ref,status='adopted')
    source['source/evaluation-charges-brutes.yaml']['unit_arbitrations'][OR]='Estimation détaillée des vues opérationnelles adoptée. La conception est incluse. Les comparaisons du lot antérieur restent historiques.'
    gross=source['source/evaluation-charges-brutes.yaml']
    for uid in (MD,OR):
        gross['unit_analyses'][uid]=dict(finding='**Les livrables du domaine Master Data sont intégrés au chiffrage courant.**' if uid==MD else '**La conception et la réalisation des vues opérationnelles sont intégrées au chiffrage courant.**',oss='Les références logicielles historiques éclairent les mécanismes réutilisés. Aucun nouveau volume de code représentatif de ce périmètre n’a été mesuré.',cosmic='Le comptage COSMIC du lot antérieur reste une preuve historique. Il ne mesure pas le nouveau domaine ni le seul consommateur Operational References.',decision='La somme des livrables validés est retenue. Les deux lots sont financés séparément, sans refacturer les services communs du producteur.',remaining='Préciser les volumes et objectifs de service. Les connecteurs, migrations et travaux spécifiques Beaumanoir ainsi que les compléments de fonctionnement restent à dimensionner.')
        gross['unit_scope'][uid]=dict(includes=[],excludes=[len(units_by_lot[uid]['excludes'])-1],assumption='scope')
    gross['analysis_order'].insert(gross['analysis_order'].index(MD)+1,OR)

    revision['status']='adopted';revision['adoption']=dict(decision_ref=decision_ref,baseline_ref=baseline_ref);revision['baseline']['path']=paths['basis'];changes[proposal['revision_ref']]=yaml_bytes(revision)
    # Work records and responsibilities stay conserved, with a distinct consumer lot.
    work=__import__('json').loads(__import__('json').dumps(read(ROOT/'source/unites-travail.yaml')));unit=next(u for u in work['units'] if u['id']=='core/'+MD);other=deepcopy(unit);other.update(id='core/'+OR,label=units_by_lot[OR]['label'],record_refs=['core/'+OR],core_scope_refs=[OR]);work['units'].insert(work['units'].index(unit)+1,other)
    for uid in (MD,OR):
        u=next(x for x in work['units'] if x['id']=='core/'+uid);lot=next(x for x in proof_units if x['id']==uid);packages=[p for p in revision['packages'] if p['id'] in lot['package_refs']];u['estimation_contract']['scope']=dict(deliverable=' · '.join(p['deliverable'] for p in packages),acceptance=[p['acceptance'] for p in packages],boundary='Produit générique. Les adaptations Beaumanoir, le MCO et l’exploitation supplémentaires restent à dimensionner.')
    for t in work['team_scopes']:
        if MD in t['core_scope_refs'] and OR not in t['core_scope_refs']:t['core_scope_refs'].insert(t['core_scope_refs'].index(MD)+1,OR)
    changes['source/unites-travail.yaml']=yaml_bytes(work)
    org=read(ROOT/'source/organisation-delivery.yaml');owner=deepcopy(next(o for o in org['work_owners'] if o['kind']=='core_unit' and o['ref']==MD));owner['ref']=OR;owner['basis']='Continuité de la propriété des services de référence. L’équipe Master Data porte le producteur et ses vues opérationnelles consommatrices. Les contributions des autres équipes restent à préciser.';org['work_owners'].append(owner);changes['source/organisation-delivery.yaml']=yaml_bytes(org)
    scenario=read(ROOT/'source/scenarios-chiffrage.yaml');selection=deepcopy(next(s for s in scenario['selections'] if s['work_unit_ref']=='core/'+MD));selection['work_unit_ref']='core/'+OR;scenario['selections'].append(selection);changes['source/scenarios-chiffrage.yaml']=yaml_bytes(scenario)
    self_contained_readings(changes,capture,capture_path,native_source,capids,retired,retired_bc,new_blocks,revision)
    for name,doc in source.items():
        if name!='source/version-modele.yaml':changes[name]=yaml_bytes(doc)
    from model_revision import next_revision
    changes['source/version-modele.yaml']=yaml_bytes(next_revision(read(ROOT/'source/version-modele.yaml'),proposal['date']))
    publication=source['config/publication.yaml']
    for name in changes:
        if name not in publication['documents']:publication['documents'].append(name)
    publication['documents'].append('tools/scope_adoption.py') if 'tools/scope_adoption.py' not in publication['documents'] else None
    changes['config/publication.yaml']=yaml_bytes(publication)
    return changes,dict(status='prepared',scope_adoption=True,total_jh=decision['proposal_jh'],cost_eur_ht=decision['construction_cost_eur_ht'],delta_jh=decision['delta_jh'],delta_cost_eur_ht=R['delta']['cost_eur_ht'],decision=decision_ref,proof_directory=folder,changed_units=[MD,OR],calendar='unchanged')


def self_contained_readings(changes,capture,capture_path,native_source,capids,retired,retired_bc,new_blocks,revision):
    from adopt_core import yaml_bytes
    fundamentals=read(ROOT/'source/fondamentaux.yaml')
    fundamentals['business_map']['scope']='La {{notion.flow_core_system}} couvre Master Data et {{notion.supply_chain_management}}. Sourcing and Procurement et Commerce restent des domaines voisins. Les autres systèmes situent le contexte des échanges.'
    fundamentals['business_map']['scope_summary']='**Le périmètre de la {{notion.flow_core_system}} réunit Master Data et {{notion.supply_chain_management}}.** La cartographie métier fournit les capacités communes à examiner dans les trois options.'
    changes['source/fondamentaux.yaml']=yaml_bytes(fundamentals)
    glossary=read(ROOT/'source/glossaire.yaml');glossary['notions']['flow_core_system']['dans_etude']='Java / Spring est la voie Make du parcours courant. Master Data produit les références maîtres. Supply Chain Management les consomme pour gérer les opérations de la chaîne logistique. Les deux domaines constituent le périmètre du produit. Les adaptations propres à Beaumanoir restent distinctes.';changes['source/glossaire.yaml']=yaml_bytes(glossary)
    # Unknown Buy coverage stays unknown for every newly introduced capability.
    coverage=read(ROOT/'source/couvertures-produits.yaml');qual=read(ROOT/'source/qualification-buy.yaml')
    qual['revues']=[r for r in qual['revues'] if r['capacite'] not in retired]
    for e in qual['exceptions']:e['blocs']=[b for b in e['blocs'] if b not in retired_bc]
    for stack in ('microsoft','sap'):
        key=stack+'_mdm_a_qualifier';base='ms_reference' if stack=='microsoft' else 'sap_reference';c=deepcopy(coverage['couvertures'][base]);c['apport']='Capacités du nouveau domaine Master Data à qualifier dans l’option et dans les contrats reçus.';c['limites']='Aucune couverture, licence, prestation ou enveloppe supplémentaire n’est présumée. Les composants cités identifient l’option comparée.';coverage['couvertures'][key]=c
        for b in new_blocks:qual['revues'].append(dict(bloc=b['id'],capacite=b['capacite_id'],stack=stack,couverture_ref=key,statut='a_qualifier',decision='Le domaine Master Data est ajouté au périmètre. La couverture fonctionnelle et les conditions commerciales restent à qualifier.',exceptions=[]))
    changes['source/couvertures-produits.yaml']=yaml_bytes(coverage);changes['source/qualification-buy.yaml']=yaml_bytes(qual)
    reading=read(ROOT/'source/lecture-metier.yaml');reading.update(cartographie=capture_path,empreinte=native_source['sha256'],domaine=native_source['domain_id'])
    for theme in reading['sujets']:
        theme['capacites']=[c for c in theme['capacites'] if c not in retired]
        if theme['id']=='operations-scm':theme['ancrages'].append('domain-master-data')
    old=read(ROOT/reading['frontieres_source']);nodes={n['id'] for n in capture['nodes']};old['nodes']=[n for n in old['nodes'] if n['id'] not in nodes];old['provenance']=deepcopy(capture['provenance']);old['date_capture']=revision['date'];border='sources/cartographie-frontieres-core-system-'+revision['date']+'.yaml';raw=yaml_bytes(old);changes[border]=raw;reading['frontieres_source']=border;reading['frontieres_empreinte']=digest(raw);changes['source/lecture-metier.yaml']=yaml_bytes(reading)
    # Documentary comparison retains its evidence, while new BA cells start unqualified.
    spec=read(ROOT/'source/comparaison-solutions.yaml');bas=[n['id'] for n in capture['nodes'] if n['kind']=='business_area'];known={r['business_area_ref'] for r in spec['business_areas']}
    template=spec['business_areas'][0]
    for id in bas:
        if id in known:continue
        row=deepcopy(template);row['business_area_ref']=id
        for assessment in row['assessments']:
            assessment.update(reading_status='non_etabli',evidence_refs=[],summary='Périmètre Master Data ajouté. Couverture à qualifier.',commercial_status='non_etabli',complete_ba_coverage=None,review=None)
        spec['business_areas'].append(row)
    spec['rfi_crosswalk']=[x for x in spec['rfi_crosswalk'] if x['capability_ref'] not in retired]
    populated={r['target_id'] for r in capture['relations'] if r['type']=='contains' and r['target_id'] in capids}
    cap_parents={r['source_id'] for r in capture['relations'] if r['type']=='contains' and r['target_id'] in capids}
    for row in spec['business_areas']:
        if row['business_area_ref'] not in cap_parents:
            for a in row['assessments']:a.update(reading_status='hors_perimetre',evidence_refs=[],summary='Famille documentaire, sans capacité autonome dans le périmètre comparatif.',complete_ba_coverage=None,review=None)
    instruction=read(ROOT/'source/instruction-marche.yaml');instruction['qualifications']=[q for q in instruction['qualifications'] if q['capability_ref'] not in retired|{'master-data-ingestion'}];changes['source/instruction-marche.yaml']=yaml_bytes(instruction)
    market=read(ROOT/'source/references-couts-integration.yaml');per=market['reperes_build_core']['etude_oss']['perimetre'];per['bc_total']=len(capids);per['bc_exclus']=[bc for bc in per['bc_exclus'] if bc not in retired_bc]
    for axis in market['reperes_build_core']['cadre_comparaison']['axes']:axis['bc_refs']=[bc for bc in axis['bc_refs'] if bc not in retired_bc]
    changes['source/references-couts-integration.yaml']=yaml_bytes(market)
    supplements=read(ROOT/'source/complements-budgetaires.yaml')
    families={'BC-003':['cap-mdm-customer','cap-mdm-supplier','cap-mdm-agreement'],'BC-004':['cap-mdm-product','cap-mdm-variant','cap-mdm-trade-item','cap-mdm-assortment','cap-mdm-catalog','cap-mdm-product-pricing'],'BC-005':['cap-mdm-packaging-material','cap-mdm-packaging-specification'],'BC-006':['cap-mdm-internal-supplies'],'BC-007':['cap-mdm-location-network','cap-mdm-service-catalog','cap-mdm-service-pricing']}
    def migrate_need_refs(value):
        if isinstance(value,dict):
            for key,item in value.items():
                if key=='need_refs' and isinstance(item,list):
                    target=[]
                    for need in item:
                        old=need.split('.')[0]
                        target.extend([f['id'] for b in new_blocks if b['capacite_id'] in families[old] for f in b['fonctions']] if old in families else [need])
                    value[key]=list(dict.fromkeys(target))
                else:migrate_need_refs(item)
        elif isinstance(value,list):
            for item in value:migrate_need_refs(item)
    migrate_need_refs(supplements);changes['source/complements-budgetaires.yaml']=yaml_bytes(supplements)

    integration=read(ROOT/'source/parcours-integration.yaml');catalog=read(ROOT/integration['capture'])['scenario_catalog'];paths={p['id']:p for p in catalog['paths']}
    for scenario in integration['scenarios']:
        found={c['node_id'] for pid in scenario['parcours'] for step in paths[pid]['steps'] for c in step['contributions'] if c['node_id'] in capids}
        scenario['capacites']=sorted(found)
    changes['source/parcours-integration.yaml']=yaml_bytes(integration)
    changes['source/comparaison-solutions.yaml']=yaml_bytes(spec)
