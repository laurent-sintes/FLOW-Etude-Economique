"""Native business domains and conserved attribution, independent of team ownership."""
from copy import deepcopy
from decimal import Decimal
from jsonschema import Draft202012Validator
from capability_catalog import catalog, native, dependencies as native_dependencies
from validate_stacks import ROOT, read
from content_model import resolve_text_tree, validate_glossary_literals

SOURCE = 'source/classement-domaines.yaml'
SCHEMA = 'source/schema-classement-domaines.yaml'


def dependencies():
    return {SOURCE, SCHEMA, 'tools/domain_costs.py', 'source/glossaire.yaml'} | native_dependencies()


def require(value, message):
    if not value:
        raise ValueError('ERR_DOMAIN_COSTS: ' + message)


def context(document=None):
    doc = deepcopy(document) if document is not None else read(ROOT / SOURCE)
    Draft202012Validator(read(ROOT / SCHEMA)).validate(doc)
    glossary=read(ROOT/'source/glossaire.yaml')
    validate_glossary_literals(doc,glossary,path=SOURCE)
    doc=resolve_text_tree(doc,glossary,path=SOURCE)
    domains = [dict(id=n['id'], label=n['fields']['name']) for n in native()['nodes'] if n['kind']=='domain']
    domains.sort(key=lambda d:d['label'])
    ids = {d['id'] for d in domains}
    overrides = doc['overrides']
    require(len({r['work_unit_ref'] for r in overrides})==len(overrides), 'Duplicate work classification')
    for r in overrides:
        require(set(r['domain_refs']) <= ids and bool(r['domain_refs']), 'Unknown native domain')
        require((r['status']=='direct' and len(r['domain_refs'])==1) or (r['status']=='shared_pending' and len(r['domain_refs'])>1), 'Ambiguous classification')
        require(all((ROOT/p).is_file() for p in r['evidence_refs']), 'Missing classification evidence')
    return dict(domains=domains, labels=doc['labels'], overrides={r['work_unit_ref']:r for r in overrides},
                capabilities={r['capacite_id']:r['hierarchie'][0]['id'] for r in catalog()['rows']})


def classify(uid, capability_ids, ctx):
    require(set(capability_ids)<=ctx['capabilities'].keys(), 'Unknown native capability')
    refs=sorted({ctx['capabilities'][c] for c in capability_ids})
    override=ctx['overrides'].get(uid)
    if override:
        require(not capability_ids, 'Native domain attribution cannot be overwritten')
        return deepcopy(override)
    return dict(work_unit_ref=uid,domain_refs=refs,status='direct' if len(refs)==1 else 'shared_pending' if refs else 'to_classify',
                basis=ctx['labels']['native_basis'] if refs else ctx['labels']['pending_basis'], evidence_refs=['source/referentiel-capacites.yaml'] if refs else [])


def summarize(rows, ctx):
    """Every source amount enters one bucket. Missing attribution is never split by headcount."""
    buckets=[dict(id=d['id'], label=d['label'], rows=[]) for d in ctx['domains']]
    buckets.append(dict(id='unallocated',label=ctx['labels']['unallocated'],rows=[]))
    by_id={b['id']:b for b in buckets}
    require(len({r['id'] for r in rows})==len(rows), 'Duplicate source amount')
    for row in rows:
        c=row['domain_classification']
        require(c['status'] in {'direct','shared_pending','to_classify'}, 'Unknown classification status')
        require(set(c['domain_refs'])<=set(by_id)-{'unallocated'}, 'Unknown attributed domain')
        require(c['status']!='direct' or len(c['domain_refs'])==1, 'Ambiguous direct amount')
        by_id[c['domain_refs'][0] if c['status']=='direct' else 'unallocated']['rows'].append(row)
    def amounts(items):
        result={}
        for field in ('jh','cost_eur_ht'):
            known=[Decimal(str(r[field])) for r in items if r[field] is not None]
            missing=sum(r[field] is None for r in items)
            result[field]=dict(known=float(sum(known)) if known or not items else None,missing=missing,total=None if missing else float(sum(known)))
        return result
    for bucket in buckets:
        bucket['unit_refs']=[r['id'] for r in bucket.pop('rows')]
        selected=[r for r in rows if r['id'] in bucket['unit_refs']]
        bucket['measures']=amounts(selected)
    all_amounts=amounts(rows)
    for field in all_amounts:
        actual=sum((Decimal(str(b['measures'][field]['known'])) for b in buckets if b['measures'][field]['known'] is not None),Decimal(0))
        require(actual==Decimal(str(all_amounts[field]['known'] or 0)), 'Domain total not conserved')
    pending=[r['id'] for r in rows if r['domain_classification']['status']!='direct']
    for bucket in buckets:
        if bucket['id']!='unallocated':
            bucket['full_totals']={field:None if pending else measure['total'] for field,measure in bucket['measures'].items()}
    return dict(domains=deepcopy(ctx['domains']),labels=deepcopy(ctx['labels']),buckets=buckets,measures=all_amounts,
                pending_unit_refs=pending,domain_totals_complete=not pending and all(a['missing']==0 for a in all_amounts.values()))


def core_reading(units, document=None):
    ctx=context(document)
    ids={'core/'+u['id'] for u in units}
    require(set(ctx['overrides'])<=ids, 'Unknown classification work unit')
    rows=[dict(id='core/'+u['id'],jh=u['total_jh'],cost_eur_ht=u['cost_eur_ht'],
               domain_classification=classify('core/'+u['id'],[c['native_id'] for c in u['capabilities']],ctx)) for u in units]
    result=summarize(rows,ctx)
    result['classifications']={r['id']:r['domain_classification'] for r in rows}
    return result
