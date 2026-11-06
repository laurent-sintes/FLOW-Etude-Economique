"""Current workload reading, with one accounting source and explicit mappings."""
from jsonschema import Draft202012Validator
from copy import deepcopy
from decimal import Decimal

from validate_stacks import ROOT, read
from content_model import resolve_text_tree
from capability_catalog import catalog as capability_catalog, native

LABELS = 'config/evaluation-charges.yaml'
JUSTIFICATIONS = 'source/justifications-charges.yaml'
JUSTIFICATION_SCHEMA = 'source/schema-justifications-charges.yaml'

def dependencies():
    return {JUSTIFICATIONS, JUSTIFICATION_SCHEMA, 'source/fonctions-produit-core.yaml', 'source/calculs-estimation-core.yaml'}



def compact_scope(capabilities, snapshot):
    nodes = {n['id']: n for n in snapshot['nodes']}
    children = {}
    for relation in snapshot['relations']:
        if relation['type'] in ('contains', 'presents'):
            children.setdefault(relation['source_id'], set()).add(relation['target_id'])
    def descendants(parent, kind):
        return {i for i in children.get(parent, ()) if nodes[i]['kind']==kind}
    selected = {c['id'] for c in capabilities}
    result = []
    for domain in snapshot['nodes']:
        if domain['kind']!='domain':
            continue
        subs = [n for n in snapshot['nodes'] if n['id'] in descendants(domain['id'], 'area')]
        areas = {sub['id']: descendants(sub['id'], 'business_area') for sub in subs}
        all_areas = set().union(*areas.values()) if areas else set()
        covered = {a for a in all_areas if descendants(a, 'capability') & selected}
        # Empty or partially covered Business Areas cannot prove full coverage.
        full = {a for a in covered if descendants(a, 'capability') <= selected}
        def item(kind, node, parent='', excluded=''):
            return dict(kind=kind,ref=node['id'],label=node['fields']['name'],parent=parent,excluded=excluded)
        if all_areas and all_areas <= full:
            result.append(item('domain', domain))
            continue
        for sub in subs:
            scope=areas[sub['id']]
            present=scope & covered
            if not present:
                continue
            if scope <= full:
                result.append(item('subdomain',sub,domain['fields']['name']))
            elif len(scope-full)==1 and present==scope & full and len(present)>1:
                missing=nodes[next(iter(scope-full))]
                result.append(item('except',sub,domain['fields']['name'],missing['fields']['name']))
            else:
                for area in snapshot['nodes']:
                    if area['id'] in present:
                        result.append(item('area',area,domain['fields']['name']+' › '+sub['fields']['name']))
    return result


def build_dossier(organisation, gross):
    justifications=read(ROOT/JUSTIFICATIONS)
    Draft202012Validator(read(ROOT/JUSTIFICATION_SCHEMA)).validate(justifications)
    justifications=justifications['units']
    product_functions=read(ROOT/'source/fonctions-produit-core.yaml')['functions']
    mechanisms={m['id']:m['funding_owner'] for m in read(ROOT/'source/calculs-estimation-core.yaml')['mechanisms']}
    catalog = organisation['work_catalog']
    current={u['id'].removeprefix('core/') for u in catalog['units'] if u['nature']=='core_build'}
    if set(justifications)!=current:raise ValueError('Charge justification coverage mismatch')
    snapshot = native()
    hierarchy = {r['capacite_id']: [dict(id=n['id'],label=n['nom'],kind=n['kind']) for n in r['hierarchie']]
                 for r in capability_catalog()['rows']}
    def scope_paths(capabilities):
        paths = {tuple(n['id'] for n in hierarchy[c['id']]): hierarchy[c['id']] for c in capabilities}
        return list(paths.values())
    labels = resolve_text_tree(read(ROOT / LABELS), read(ROOT / 'source/glossaire.yaml'))
    office = read(ROOT / 'source/modele-composable.yaml')['equipe_transformation']
    annual_governance = sum(r['etp']*office['jours_par_an'] for r in office['roles'])
    years = labels['governance_years']
    if len(set(years))!=len(years) or any(type(y) is not int or y<=0 for y in years):
        raise ValueError('Invalid governance horizons')
    governance = dict(annual_jh=annual_governance,horizons=[dict(years=y,jh=annual_governance*y) for y in years])
    core = gross['acquisition']['options']['java-spring']['core']
    allocation_rules = {r['id']: r['basis'] for r in catalog['abaque']['overrides']}
    core_rows = {'core/' + row['id']: row for row in core['rows']}
    capability_shares = {(l['work_unit_ref'], l['capability_ref']): l['share_pct'] for l in catalog['capability_links']}
    phases = []
    team_names = {team['id']: team['label'] for team in organisation['teams']}
    team_names.update(governance=organisation['governance']['label'])
    for phase in organisation['phases']:
        rows = []
        for unit in catalog['units']:
            if unit['phase_ref'] != phase['id'] or phase['id'] == 'integration':
                continue
            # Financial-only records are valued in the economic dossier.
            if unit['totals']['jh'] is None:
                continue
            estimate = unit['estimation']
            source = core_rows.get(unit['id'])
            charge = unit['totals']['jh']
            annual_role = next((r for r in office['roles'] if r['id']==unit['id'].split('/')[-1]),None) if unit['nature']=='governance' else None
            if annual_role:
                charge = annual_role['etp']*office['jours_par_an']
            contributions = []
            for item in unit['contributions']:
                days = charge if annual_role else item['jh']
                if days is None:
                    continue
                share = None if days is None or not charge else float(Decimal(str(days)) * 100 / Decimal(str(charge)))
                contributions.append(dict(team_ref=item['team_ref'], label=team_names.get(item['team_ref'], labels['unallocated']),
                                          jh=days, share_pct=share, rule_refs=item['rule_refs'],
                                          basis=' · '.join(allocation_rules[r] for r in item['rule_refs'] if r in allocation_rules)))
            if abs(sum(item['jh'] or 0 for item in contributions) - charge) > 1e-7:
                raise ValueError('ERR_CHARGE_DOSSIER_CONSERVATION:' + unit['id'])
            capabilities = [dict(cap, share_pct=capability_shares[(unit['id'], cap['id'])])
                            for cap in unit['capabilities']]
            methods = [{key: method[key] for key in ('id','label','method','jh')} for method in source['comparisons']] if source else []
            if unit['id'] == 'core/master-data-java-spring':
                methods = [dict(id=p['id'], label=p['label'], method='COCOMO II', jh=p['jh'])
                           for p in organisation['mdm_oss_assessment']['products']]
            packages = deepcopy(source['detail']['work_packages']) if source else []
            rationale = source['detail']['analysis']['decision'] if source else ' · '.join(t['basis'] for t in estimate['terms'] if t.get('basis')) or estimate['scope']['deliverable'] or unit['label']
            terms = deepcopy(estimate['terms'])
            if unit['nature'] == 'governance':
                office = read(ROOT / 'source/modele-composable.yaml')['equipe_transformation']
                role = next(r for r in office['roles'] if r['id']==unit['id'].split('/')[-1])
                rationale = role['mission']
                terms = [dict(id='capacity',quantity=role['etp'],
                              unit=labels['annual_unit'],unit_jh=office['jours_par_an'],basis=labels['annual_capacity'])]
            summary = rationale.split('. ')[0].rstrip('.') + '.' if source and not packages else ''
            exclusions, bridge = [], None
            if unit['id']=='core/master-data-java-spring':
                assessment = organisation['mdm_oss_assessment']
                rationale, summary = labels['mdm_decision'], labels['mdm_summary']
                exclusions = deepcopy(assessment['unidata_review']['exclusions'])
                engineering = assessment['engineering']
                bridge = dict(reference_jh=next(p['jh'] for p in assessment['products'] if p['id']=='unidata'),
                    flow_jh=charge,parts=[dict(label=g['label'],jh=g['jh']) for g in engineering['groups']]+[
                        dict(label=labels['mdm_families'],jh=engineering['family_jh']),
                        dict(label=labels['mdm_qualification'],jh=engineering['qualification_jh'])])
            proofs = [source['detail']['proof']['path']] if source else estimate['source_refs']
            if unit['id'] == 'core/master-data-java-spring':
                assessment = organisation['mdm_oss_assessment']
                proofs += [assessment['report_ref'], assessment['engineering']['report_ref'],assessment['unidata_review']['report_ref']]
            justification=deepcopy(justifications.get(unit['id'].removeprefix('core/')))
            functions=[dict(id=f['id'],label=f['label'],nature=f['nature'],boundary=f['boundary']) for f in product_functions
                       if unit['id'].removeprefix('core/') in {mechanisms[ref] for ref in f['existing_funding_refs']}]
            cosmic=None
            if justification:
                summary=justification['summary']
                rationale=justification['choice']
            if unit['id']=='core/master-data-java-spring':
                cosmic=organisation['mdm_oss_assessment']['cosmic']
                methods.append(dict(id='cosmic-isbsg',label='COSMIC × ISBSG',method='COSMIC × ISBSG',jh=cosmic['jh']))
                proofs+=cosmic['proof_refs']
            for method in methods:
                method['scope_note'] = source['detail']['analysis']['cosmic' if method['id']=='cosmic-isbsg' else 'oss'] if source else ''
                if cosmic:method['scope_note'] = cosmic['activity_scope'] if method['id']=='cosmic-isbsg' else labels['mdm_comparison_scope']
            rows.append(dict(justification=justification,natures=justification['natures'] if justification else [],product_functions=functions,cosmic=cosmic,id=unit['id'],label=unit['label'].removesuffix(' Java/Spring'),kind=unit['nature'],jh=charge,
                             methods=methods,contributions=contributions,capabilities=capabilities,scope_paths=scope_paths(capabilities),scope_summary=compact_scope(capabilities,snapshot),
                             rationale=rationale,summary=summary,exclusions=exclusions,bridge=bridge,unit='JH/an' if annual_role or phase['id']=='fonctionnement' else 'JH',packages=packages,terms=terms,
                             roles=[dict(id=r['id'],label=r['label'],jh=charge if annual_role else r.get('net_jh')) for r in estimate['reference']['roles']],
                             scope=estimate['scope']['deliverable'],proofs=proofs))
        phases.append(dict(id=phase['id'],label=phase['label'],unit='JH/an' if phase['id']=='fonctionnement' else 'JH',
                           pending=phase['id']=='integration',rows=rows,
                           total_jh=None if phase['id']=='integration' else sum(row['jh'] for row in rows if row['kind']!='governance'),
                           product_jh=sum(row['jh'] for row in rows if row['kind']=='core_build'),
                           governance_annual_jh=sum(row['jh'] for row in rows if row['kind']=='governance')))
    governance['rows'] = [row for p in phases for row in p['rows'] if row['kind']=='governance']
    for p in phases:
        p['rows'] = [row for row in p['rows'] if row['kind']!='governance']
        del p['governance_annual_jh']
    teams = []
    for team in organisation['teams']:
        totals = {}
        links = []
        for phase in phases:
            allocations = [c for row in phase['rows'] for c in row['contributions'] if c['team_ref']==team['id']]
            totals[phase['id']] = None if phase['pending'] or not allocations else sum(c['jh'] or 0 for c in allocations)
            for row in phase['rows']:
                contribution = next((c for c in row['contributions'] if c['team_ref']==team['id']), None)
                if contribution:
                    links.append(dict(function_ref=row['id'],label=row['label'],phase_ref=phase['id'],
                                      share_pct=contribution['share_pct'],jh=contribution['jh'],capabilities=row['capabilities'],scope_paths=row['scope_paths']))
        phase_scopes = {p['id']: compact_scope([c for row in links if row['phase_ref']==p['id'] for c in row['capabilities']],snapshot) for p in phases}
        teams.append(dict(scope_summaries=phase_scopes,id=team['id'],label=team['label'],type=team['type'],totals=totals,functions=links,capability_scope=next(s['capabilities'] for s in catalog['team_scopes'] if s['team_ref']==team['id'])))
    option_summaries = {}
    for option in ('microsoft', 'sap'):
        option_summaries[option] = []
        for phase in phases:
            rows = gross[phase['id']]['options'][option]['groups']
            values = [r['value'] for group in rows for r in group['rows'] if r['unit'].startswith('JH') and r['value'] is not None]
            option_summaries[option].append(dict(id=phase['id'],label=labels['buy_phase_labels'][phase['id']],
                unit=phase['unit'],jh=None if phase['pending'] or not values else sum(values)))
    acquisition_summaries = {}
    for option in ('java-spring', 'microsoft', 'sap'):
        product = phases[0]['total_jh'] if option=='java-spring' else next(p['jh'] for p in option_summaries[option] if p['id']=='acquisition')
        acquisition_summaries[option] = dict(product_jh=product, horizons=[
            dict(years=h['years'], jh=None if product is None else product+h['jh']) for h in governance['horizons']])
    return dict(acquisition_summaries=acquisition_summaries,governance=governance,labels=labels,phases=phases,teams=teams,option_summaries=option_summaries,methods=[{key:m[key] for key in ('id','label','method')} for m in core['rows'][0]['comparisons']])
