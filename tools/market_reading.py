"""Project and service evidence for the economic study, without valuation.

The projection copies already validated source values and their provenance.
It neither normalizes prices again nor turns a documentary comparison into a
FLOW budget. It reads only the Study content passed by the caller.
"""

from copy import deepcopy


def _label(scale, value):
    # JSON transport turns numeric dictionary keys into strings.
    return scale[value] if value in scale else scale[str(value)]


def build_market_reading(market):
    projects = []
    services = []
    for reference in market['references']:
        reading = reference['lecture_flow']
        source_ref = 'source/references-couts-integration.yaml#references/' + reference['id']
        common = dict(
            id=reference['id'], name=reference['nom'],
            platform=reference['projet']['plateforme'],
            country=reference['contexte_business']['pays'],
            source_ref=source_ref,
            sources=deepcopy(reference['sources']),
            proofs=deepcopy(reading['preuves']),
        )
        price = deepcopy(reference['cout_publie'])
        projects.append(dict(
            **common,
            scope=reference['projet']['perimetre'],
            included=reference['projet']['inclus_dans_prix'],
            excluded=reference['projet']['exclus_du_prix'],
            price=price,
            price_evidence=_label(market['echelle_qualite_prix_source'], price['qualite_prix_source']),
            normalized=deepcopy(reference['normalisation_2026']),
            transposed=deepcopy(reference['transposition_au_perimetre_flow_beaumanoir']),
            lesson=reading['enseignement'],
        ))
        services.append(dict(
            **deepcopy(common),
            status=market['presentation_references']['statuts'][reading['postes']['mco_run']],
            scope=reading['mco_run'],
            observations=[dict(
                **deepcopy(observation),
                evidence=_label(market['echelle_qualite_prix_source'], observation['qualite_prix_source']),
            ) for observation in reading['observations']],
        ))
    return dict(projects=projects, services=services,
                normalization=market['conventions']['normalisation'],
                transposition=market['presentation_references']['transposition_note'],
                operations_note=market['presentation_references']['observations_note'],
                registry_ref='source/references-couts-integration.yaml',
                monetary_sources_ref='source/references-couts-integration.yaml#sources_monetaires')
