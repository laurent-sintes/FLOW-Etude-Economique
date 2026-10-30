"""Derived reading metadata for parameters; no economic or simulation calculation."""
from copy import deepcopy
from urllib.parse import urlsplit

from validate_stacks import ROOT, read


ERROR = 'ERR_FRAMEWORK_PARAMETERS'
CALIBRATION = 'source/calibration-couts.yaml'
INTEGRATION = 'source/integration.yaml'
MAINTENANCE = 'source/maintenance.yaml'
INFLATION = 'source/inflation.yaml'


def _require(condition, reason):
    if not condition:
        raise ValueError(f'{ERROR}:{reason}')


def _add(target, key, value):
    """Never replace a conflicting projection silently."""
    _require(key not in target or target[key] == value, f'conflicting projection:{key}')
    target[key] = deepcopy(value)


def compile_framework_parameters(framework, stacks, calibration, ui, documents,
                                 integration, maintenance, inflation):
    """Return an isolated enrichment, retaining every existing field and value."""
    result = deepcopy(framework)
    allowed = set(documents)

    def document(path):
        _require(path.split('#', 1)[0] in allowed, f'undeclared document:{path}')
        return path

    def evidence(registry, ids):
        rows = []
        for key in ids:
            _require(key in registry, f'unknown evidence:{key}')
            source = registry[key]
            path = source.get('reference', source.get('url'))
            _require(isinstance(path, str) and bool(path.strip()), f'missing evidence path:{key}')
            parts = urlsplit(path)
            if parts.scheme:
                _require(parts.scheme in ('http', 'https') and bool(parts.netloc), f'invalid evidence URL:{key}')
            else:
                document(path)
            _require(bool(source.get('titre')), f'missing evidence title:{key}')
            rows.append(dict(id=key, title=source['titre'], path=path,
                             kind=source['nature'], locator=source.get('repere', '')))
        return rows

    specifications = ui['parameters']
    common = {row['key']: row for row in specifications['common']}
    options = {row['key']: row for row in specifications['option']}
    _require(len(common) == len(specifications['common']) and
             len(options) == len(specifications['option']), 'duplicate personal parameter')
    modes = {row['key']: row['mode'] for row in result['tariffs']}

    def personal(key=None, slugs=None, aggregate=False, shared=False):
        registry = common if shared else options
        if key not in registry:
            return dict(kind='reference')
        spec = registry[key]
        eligible = [] if shared else [slug for slug in (slugs or modes)
                                      if slug in modes and modes[slug] in spec['modes']]
        if not shared and not eligible:
            return dict(kind='reference')
        return dict(kind='aggregate' if aggregate else 'direct', key=key,
                    label=spec['label'], options=eligible, shared=shared)

    _require(integration['roles'] == maintenance['roles'], 'inconsistent activity roles')
    roles = {}
    for key, row in integration['roles'].items():
        roles[key] = dict(name=row['nom'], scope=row['perimetre'], activity=row['activite_tjm'],
                          source=document(f'{INTEGRATION}#roles/{key}'))
    _add(result, 'roles', roles)

    for option in result['tariffs']:
        slug = option['key']
        model = stacks[slug]['model']
        interventions = model['interventions']
        path = f'source/stacks/{slug}.yaml'
        context = dict(market=interventions['marche'], purchase_mode=interventions['mode_achat'],
                       profile=interventions['profil_comparable'], geography=interventions['base_geographique'])
        _require(context['purchase_mode'] in ui['reading']['purchase_modes'], 'unlabelled purchase mode')
        _add(option, 'context', context)
        _add(option, 'source', document(path + '#interventions'))
        for row in option['prices']:
            rate = interventions['tarifs'][row['key']]
            _require(row['value'] == rate['reference'], f'inconsistent tariff:{slug}/{row["key"]}')
            _add(row, 'evidence', evidence(model['sources'], rate['sources']))

    spec = calibration['specialisation_maintenance_make']
    _require(set(spec) == {'statut', 'activites_refs', 'profil_base', 'profil_cible',
                          'plafond_jh_avant_sensibilite', 'origine', 'assiette', 'calcul'},
             'specialist fields')
    specialist = deepcopy(spec)
    _require(spec['profil_base'] in roles and spec['profil_cible'] == 'architecte', 'specialist profiles')
    activities = {row['id']: row for row in maintenance['activites']}
    _require(set(spec['activites_refs']) <= set(activities), 'unknown specialist activity')
    specialist['activities'] = [dict(id=key, label=activities[key]['nom'],
                                    source=document(f'{MAINTENANCE}#activites/{key}'))
                                for key in spec['activites_refs']]
    # The central scenario is the identity factor in maintenance_specialist_adjustment.
    specialist['factors_jh'] = dict(bas=calibration['sensibilite']['jh_bas'], central=1,
                                   haut=calibration['sensibilite']['jh_haut'])
    specialist['source'] = document(CALIBRATION + '#specialisation_maintenance_make')
    specialist['sensitivity_source'] = document(CALIBRATION + '#sensibilite')
    _add(result, 'specialist', specialist)

    annual_means = {
        'outillage_realisation': ('outillage_realisation_eur_par_jh', None, None, False),
        'ipaas_make_microsoft': ('ipaas_make_microsoft_annuel', 'ipaas', ['java-spring', 'dotnet', 'rust', 'microsoft'], False),
        'ipaas_sap': ('ipaas_sap_annuel', 'ipaas', ['sap'], False),
        'outillage_support': ('outillage_support_annuel', None, None, False),
        'power_platform': ('power_platform_supplementaire_annuel', 'licences_complementaires', ['microsoft'], False),
        'accompagnement_make': ('accompagnement_applicatif_make_jh', None, None, False),
    }
    for row in result['other']:
        key = row['key']
        if key.startswith('cloud_'):
            source_key = 'cloud_make_annuel/' + key[len('cloud_'):]
            parameter, slugs, aggregate = 'hebergement', ['java-spring', 'dotnet', 'rust'], True
        elif key.startswith('capacite_buy_'):
            slug = key[len('capacite_buy_'):]
            source_key = 'capacite_buy_supplementaire_annuel/' + slug
            parameter, slugs, aggregate = 'hebergement', [slug], False
        else:
            _require(key in annual_means, f'unknown means:{key}')
            source_key, parameter, slugs, aggregate = annual_means[key]
        _add(row, 'source', document(CALIBRATION + '#couts_communs'))
        _add(row, 'value_source', document(CALIBRATION + '#couts_communs/' + source_key))
        _add(row, 'personal', personal(parameter, slugs, aggregate))

    for row in result['inflation']:
        spec = inflation['categories'][row['key']]
        _add(row, 'evidence', evidence(inflation['sources'], spec['sources']))
        key = next((key for key, field in common.items() if field['source'] == row['source']), None)
        _add(row, 'personal', personal(key, shared=True))

    _add(result['support'], 'source', document('source/stacks/java-spring.yaml#interventions/tarifs/support_utilisateur'))
    _add(result['frontend'], 'source', document(CALIBRATION + '#calibration/frontend'))
    _add(result, 'sources', dict(
        gains=document(CALIBRATION + '#ia'),
        annual_gains=[dict(key=slug, path=document(f'source/chiffrage/chiffrage-{slug}.yaml#maintenance/activites'))
                      for slug in modes],
        coordination=document(CALIBRATION + '#pilotage'),
        programme=document('source/deploiement-groupe.yaml#/pilotage'),
        deployment=document('source/deploiement-groupe.yaml#deploiement'),
        allocation=document('source/architecture.yaml'),
    ))
    return result


def hydrate_framework_parameters(framework, stacks, calibration, ui, documents):
    """Read the existing owners in the current isolated model load."""
    return compile_framework_parameters(framework, stacks, calibration, ui, documents,
                                        read(ROOT / INTEGRATION), read(ROOT / MAINTENANCE),
                                        read(ROOT / INFLATION))
