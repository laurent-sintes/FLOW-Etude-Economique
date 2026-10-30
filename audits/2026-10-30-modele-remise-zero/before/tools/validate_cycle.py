"""Validate common integration/maintenance catalogs, annual scenario, roles and purchase inclusions."""
import argparse
import hashlib
import json
from collections import Counter
import yaml
from jsonschema import Draft202012Validator
from validate_stacks import ROOT, read
from model_context import model_memo

ROLES = ('developpement', 'integration', 'support_n3', 'support_n1')
STACKS = ('java-spring', 'dotnet', 'rust', 'microsoft', 'sap')


def fingerprint(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def scenario_fingerprint(value):
    content = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(content.encode()).hexdigest()


def check_inclusions(nodes):
    visited = set()
    def visit(node, ancestors):
        assert node not in ancestors, f'Circular inclusion: {node}'
        assert node in nodes, f'Unknown financing reference: {node}'
        if node in visited:
            return
        for target in nodes[node]['inclus_dans']:
            visit(target, ancestors | {node})
        visited.add(node)
    for node in nodes:
        visit(node, set())


def prix_annuel_documente(poste, annee, taux_pct=None):
    """Prix d'un poste seulement, jamais total FLOW. None = inconnu ou financé ailleurs.

    Année relative à la séquence de prix du poste : ne pas aligner automatiquement
    Build/Run, montée en charge et exploitation stabilisée.
    """
    assert isinstance(annee, int) and annee >= 1
    if poste['methode'] == 'sans_redevance':
        return 0
    prices = {p['annee']: p['montant'] for p in poste['montants_documentes_eur_ht']}
    if annee in prices:
        return prices[annee]  # Pas d'inflation sur une donnée documentée.
    projection = poste['projection']
    if projection['methode'] != 'indexation' or not prices:
        return None
    last = max(prices)
    if annee < projection['a_partir_annee']:
        return None
    assert taux_pct is not None and taux_pct > -100
    return round(prices[last] * (1 + taux_pct / 100) ** (annee - last), 2)


def check_valuation(doc, proof, inflation):
    valuation = doc['valorisation_annuelle']
    posts = {p['id']: p for p in valuation['postes']}
    assert len(posts) == len(valuation['postes']), 'Duplicate economic post'
    targets = {}
    for act in doc['activites']:
        if act['nature'] == 'travail':
            targets[act['id']] = act
        else:
            targets.update({act['id']+'/'+b['id']: b for b in act['achats']})
    allocation = [target for p in posts.values() for target in p['couvre']]
    assert Counter(allocation) == Counter({t: 1 for t in targets}), 'Missing or duplicated economic assignment'
    for key, p in posts.items():
        assert set(p['sources']) <= set(proof['sources'])
        for target in p['couvre']:
            assert targets[target]['valorisation_ref'] == key
        values = p['montants_documentes_eur_ht']
        assert [v['annee'] for v in values] == list(range(1, len(values)+1)), 'Documented years must be explicit and consecutive'
        priced = p['methode'] in ('prix_documentes', 'prix_reference_indexe')
        assert bool(values) == priced
        if priced:
            assert p['annee_prix'] is not None and p['adequation_perimetre'] == 'source_a_rapprocher'
            assert any(proof['sources'][s]['nature'] == 'estimation_fournisseur_rfi_2025' for s in p['sources'])
            assert p['projection']['methode'] in ('indexation', 'non_etablie')
        if p['methode'] == 'prix_reference_indexe':
            assert len(values) == 1 and p['projection']['methode'] == 'indexation'
        projection = p['projection']
        if projection['methode'] == 'indexation':
            assert values and projection['a_partir_annee'] == len(values)+1, 'Inflation must start after documented prices'
            ref = projection['inflation_ref']
            assert ref and ref.startswith('source/inflation.yaml#categories/') and ref.split('/')[-1] in inflation
        else:
            assert projection['a_partir_annee'] is None and projection['inflation_ref'] is None
        if p['methode'] == 'inclus':
            assert p['finance_par'] in posts and projection['methode'] == 'inclus'
            for target in p['couvre']:
                assert p['finance_par'] == targets[target]['inclus_dans'][0]
        else:
            assert p['finance_par'] is None
        if p['methode'] == 'sans_redevance':
            assert projection['methode'] == 'sans_redevance'
            assert all(targets[t].get('regime') == 'sans_redevance' for t in p['couvre'])
        if p['methode'] == 'estimation':
            assert projection['methode'] == 'a_estimer'
    check_inclusions({key: {'inclus_dans': [p['finance_par']] if p['finance_par'] else []} for key,p in posts.items()})
    for key, target in targets.items():
        if target.get('regime') == 'prix_documente':
            assert posts[target['valorisation_ref']]['methode'] in ('prix_documentes','prix_reference_indexe')
        if target.get('regime') == 'inclus' or target.get('prise_en_charge') == 'abonnement_editeur':
            assert posts[target['valorisation_ref']]['methode'] == 'inclus'


@model_memo
def validate():
    """Current catalogs and supplier inclusions; no historical scores or AGENTS registry."""
    from model_inputs import annual_scenario
    from model_context import model_session
    with model_session():
        cv=Draft202012Validator(read(ROOT/'source/schema-activites-cycle.yaml'))
        vv=Draft202012Validator(read(ROOT/'source/schema-valorisation-cycle.yaml'))
        proof=read(ROOT/'sources/integration-maintenance-2026-10-22.yaml')
        inflation=read(ROOT/'source/inflation.yaml')['categories']
        for key,evidence in proof['sources'].items():
            ref=evidence['reference']
            assert evidence['portee'] and evidence['nature'],key
            assert ref.startswith(('https://','http://')) or (ROOT/ref).is_file(),key
            if evidence.get('sha256'):assert fingerprint(ref)==evidence['sha256'],key
        annual_scenario()  # Derived volumes and scope consistency.
        for phase in ('integration','maintenance'):
            catalog=read(ROOT/f'source/{phase}.yaml');cv.validate(catalog)
            ids=[r['id'] for r in catalog['activites']]
            assert len(ids)==len(set(ids))
            for row in catalog['activites']:
                assert set(row['sources'])<=proof['sources'].keys()
                if row['nature']=='travail':
                    assert set(row['roles_pct'])==set(ROLES) and sum(row['roles_pct'].values())==100
            for slug in STACKS:
                doc=read(ROOT/f'source/{phase}/{phase}-{slug}.yaml');vv.validate(doc)
                deps=doc['dependances']
                assert deps['catalogue']==f'source/{phase}.yaml'
                for name in ('catalogue','stack','integration'):
                    if name in deps:assert fingerprint(deps[name])==deps[name+'_sha256'],(slug,name)
                assert scenario_fingerprint(read(ROOT/'source/maintenance.yaml')['scenario_annuel'])==deps['scenario_sha256']
                assert [r['id'] for r in doc['activites']]==ids
                stack=read(ROOT/deps['stack']);components={r['id'] for r in stack['elements']}
                for row in doc['activites']:
                    assert set(row['sources'])<=proof['sources'].keys()
                    assert set(row['composants'])<=components
                    if row['nature']=='travail':
                        if row['roles'] is None:
                            assert row['prise_en_charge']=='abonnement_editeur'
                            continue
                        assert set(row['roles'])==set(ROLES)
                        assert sum(r['part_pct'] for r in row['roles'].values())==100
                        assert all(0<=r['part_pct']<=100 for r in row['roles'].values())
                if phase=='maintenance':check_valuation(doc,proof,inflation)
    return True

if __name__=='__main__':
    validate()
    print('Validated current catalogs, volumes, roles and supplier prices/inclusions.')
