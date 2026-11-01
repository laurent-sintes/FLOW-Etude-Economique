"""Project and service evidence for the economic study, without valuation.

The projection copies already validated source values and their provenance.
It neither normalizes prices again nor turns a documentary comparison into a
FLOW budget. It reads only the Study content passed by the caller.
"""

from copy import deepcopy


def _label(scale, value):
    # JSON transport turns numeric dictionary keys into strings.
    return scale[value] if value in scale else scale[str(value)]


def build_phase_summary(market):
    """Read documentary guardrails from their owners, without a FLOW valuation."""
    summary = deepcopy(market['synthese_phases'])
    if [row['id'] for row in summary['phases']] != ['acquisition', 'integration', 'fonctionnement']:
        raise ValueError('Expected the three FLOW phases in order')
    references = {row['id']: row for row in market['references']}
    def reference(ref_id, view='projects'):
        row = references[ref_id]
        return dict(id=ref_id, label=summary['reference_labels'][ref_id],
                    name=row['nom'], href='#preetude-projets?view=' + view +
                    '&focus=market-reference-' + ref_id)
    groups = {}
    for group_id, presentation in summary.pop('groupes').items():
        original = market['reperes_exploratoires_marche'][group_id]
        if group_id == 'grands_programmes_sap_publics':
            bounds = original['plage_arrondie_m_eur_2026']
            lower, upper = bounds['min'] * 1_000_000, bounds['max'] * 1_000_000
            ref_ids = [anchor['reference_id'] for anchor in original['ancres']]
        elif group_id == 'contrepoints_dynamics':
            lower, upper = original['minimum_eur_2026'], original['maximum_eur_2026']
            ref_ids = original['references_ids']
        else:
            raise ValueError('Unknown documentary range: ' + group_id)
        groups[group_id] = dict(id=group_id, **presentation, min_eur=lower, max_eur=upper,
                                references=[reference(ref_id) for ref_id in ref_ids])
    for phase in summary['phases']:
        phase['groups'] = [deepcopy(groups[key]) for key in phase.pop('groupes')]
        phase['references'] = [reference(ref_id, 'services') for ref_id in phase['references']]
        phase['documents'] = [dict(label=doc['label'], path=market['dependances'][doc['dependency_ref']])
                              for doc in phase['documents']]
        # Published-scope intervals above are never a FLOW range or an annualization.
        phase['flow_range'] = None
    summary.pop('reference_labels')
    return summary


def documentary_products(market):
    """Expose observed product facts, never nominal or adopted estimates."""
    frame = market['reperes_build_core']
    fields = ('id', 'nom', 'famille', 'version_edition', 'date_observation',
              'preuve_ref', 'composition', 'references_deploiement', 'evaluations')
    products = {}
    for key, row in frame['fiches_produit'].items():
        result = {field: deepcopy(row[field]) for field in fields if field in row}
        result['statut'] = 'code_mesure' if row['code']['pncloc'] is not None else row['statut']
        result['code'] = {field: deepcopy(row['code'][field]) for field in ('observabilite', 'pncloc')}
        products[key] = result
    return dict(cadre_comparaison={key: deepcopy(frame['cadre_comparaison'][key])
                                 for key in ('introduction', 'axes', 'singularites')},
                fiches_produit=products)


def documentary_comparison(comparison):
    if comparison is None:
        return None
    keys = ('id', 'date', 'source_ref', 'reading', 'context', 'products', 'sources', 'rows', 'rfi_crosswalk')
    result = {key: deepcopy(comparison[key]) for key in keys}
    result['gaps'] = [{key: deepcopy(row[key]) for key in ('id', 'title', 'acceptance_scenario', 'evidence_refs')}
                      for row in comparison['gaps']]
    return result


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
            review_date=reading['date_revue'],
            similarities=reading['similitudes'],
            differences=reading['differences'],
            lesson=reading['enseignement'],
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
                documentary_products=documentary_products(market),
                documentary_comparison=documentary_comparison(market.get('comparison')),
                phase_summary=build_phase_summary(market),
                cost_evidence=deepcopy(market.get('cost_evidence')),
                instruction=deepcopy(market.get('instruction')),
                comparison=deepcopy(market.get('comparison')),
                comparison_scope=deepcopy(market['reperes_build_core']['etude_oss']['perimetre']),
                effort={key:deepcopy(market['reperes_build_core'][key])
                        for key in ('introduction','colonnes','lignes','conclusion')},
                effort_sources=[market['dependances']['preuve_build_core'],market['dependances']['revue_referentiel']],
                product_observations={key:dict(date=fiche['date_observation'],
                    observations=deepcopy(fiche['evaluations']))
                    for key,fiche in market['reperes_build_core']['fiches_produit'].items()},
                review_source=market['dependances']['revue_referentiel'],
                normalization_context=market['conventions']['prix_2026'],
                monetary_sources=deepcopy(market['sources_monetaires']),
                normalization=market['conventions']['normalisation'],
                transposition=market['presentation_references']['transposition_note'],
                operations_note=market['presentation_references']['observations_note'],
                registry_ref='source/references-couts-integration.yaml',
                monetary_sources_ref='source/references-couts-integration.yaml#sources_monetaires')
