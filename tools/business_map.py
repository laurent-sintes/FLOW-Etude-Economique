"""A derived, versioned business reading: no economic formulas or editable hierarchy."""
from copy import deepcopy
import hashlib
from urllib.parse import urlencode
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read

PATH = 'source/lecture-metier.yaml'


def validate(spec=None, scope=None):
    spec = spec if spec is not None else read(ROOT / PATH)
    Draft202012Validator(read(ROOT / 'source/schema-lecture-metier.yaml')).validate(spec)
    snapshot = read(ROOT / spec['cartographie'])
    assert hashlib.sha256((ROOT / spec['cartographie']).read_bytes()).hexdigest() == spec['empreinte']
    assert snapshot['domaine_id'] == spec['domaine']
    nodes = {n['id']: n for n in snapshot['nodes']}
    caps = {i for i, n in nodes.items() if n['kind'] == 'capability'}
    neighbors = read(ROOT / spec['frontieres_source'])
    assert neighbors['provenance']['sha256'] == snapshot['provenance']['sha256']
    assert hashlib.sha256((ROOT / spec['frontieres_source']).read_bytes()).hexdigest() == spec['frontieres_empreinte']
    external = {n['id']: n for n in neighbors['nodes']}
    assert len(external) == len(neighbors['nodes']) and not external.keys() & nodes.keys()
    scope = scope if scope is not None else read(ROOT / 'source/explications-modele.yaml')['perimetre_compare']
    assert len({r['id'] for r in scope}) == len(scope)
    assert {t['id'] for t in spec['sujets']} == {r['id'] for r in scope}
    assert len(spec['sujets']) == len(scope)
    for theme in spec['sujets']:
        assert set(theme['capacites']) <= caps
        assert set(theme['ancrages']) <= {i for i,n in nodes.items() if n['kind'] in ('domain','area','business_area')}
        assert set(theme['voisins']) <= external.keys()
        assert theme['capacites'] or theme['ancrages'] or theme['voisins'] or theme['nature'] == 'technique'
    return spec, snapshot, external


def build(complexity, business, buy, integration, scope):
    spec, snapshot, external = validate(scope=scope)
    names = {r['id']: r for r in scope}
    nodes = {n['id']: n for n in snapshot['nodes']}
    rows = deepcopy(complexity['rows'])
    assert {r['capacite_id'] for r in rows} == {i for i,n in nodes.items() if n['kind']=='capability'}
    work = {r['id']: r for r in business['rows']}
    reviews = {(r['capacite'],r['stack']): r for r in buy['revues']}
    exceptions = {e['id']: e for e in buy['exceptions']}

    def proofs(ids, registry):
        assert set(ids) <= registry.keys(), ('Missing evidence', set(ids)-registry.keys())
        return [dict(id=i, **registry[i]) for i in ids]

    themes = []
    for t in spec['sujets']:
        selected = set(t['capacites']) | {r['capacite_id'] for r in rows if set(r['chemin']) & set(t['ancrages'])}
        themes.append(dict(id=t['id'], title=names[t['id']]['fonction'], kind=t['nature'],
            capabilities=[r['capacite_id'] for r in rows if r['capacite_id'] in selected], anchors=t['ancrages'],
            neighbors=[dict(id=i,nom=external[i]['fields']['name'],kind=external[i]['kind']) for i in t['voisins']],
            content=names[t['id']], rationale=t['justification'], source=t['source'], status=t['statut']))

    funding = []
    for w in business['rows']:
        for slug, a in w['stacks'].items():
            a['proofs'] = proofs(a['coverage']['sources'], business['sources'])
            # The instance is (work owner, option); a reusable estimate template is not a funding identity.
            a['funding_id'] = w['id'] + ':' + slug
            funding.append(dict(id=a['funding_id'], owner=w['capacite_id'], block=w['id'], stack=slug,
                template=a['travaux_ref'], valuation=a['valuation'],
                beneficiaries=[r['capacite_id'] for r in business['rows'] if any(x['proprietaire']==w['id'] for x in r['reuse'])]))
    assert len({f['id'] for f in funding}) == len(funding)
    for r in rows:
        cid = r['capacite_id']
        r['work'] = work[r['id']]
        r['buy'] = {}
        for slug in ('microsoft','sap'):
            review = deepcopy(reviews[cid,slug])
            review['proofs'] = proofs(review['coverage']['sources'], buy['coverage_sources'])
            review['exceptions'] = [dict(**exceptions[e],proofs=proofs(exceptions[e]['sources'],buy['sources'])) for e in review['exceptions']]
            r['buy'][slug] = review
        r['themes'] = [t['id'] for t in themes if cid in t['capabilities']]
        r['scenarios'] = [dict(id=s['scenario'],title=s['source']['title'],
            route='#estimations?'+urlencode(dict(section='integration',focus='scenario-'+s['scenario'])))
            for s in integration['scenarios'] if cid in s['capacites']]
    return dict(source=dict(path=spec['cartographie'],date=snapshot['date_capture'],
        version=snapshot['provenance']['version'],revision=snapshot['provenance']['sha256'],
        domain=dict(id=spec['domaine'],nom=nodes[spec['domaine']]['fields']['name'])),
        rows=rows,themes=themes,transverse=work['TRANSVERSE'],funding=funding)
