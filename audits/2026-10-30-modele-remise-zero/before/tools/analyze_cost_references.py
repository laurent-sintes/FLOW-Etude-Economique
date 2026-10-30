"""Check market cost references and dispersion eligibility without editing YAML."""

from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from math import ceil, floor
import re
from statistics import mean, variance

from validate_stacks import read


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / 'source/references-couts-integration.yaml'


def number(value):
    assert not isinstance(value, bool) and isinstance(value, (int, float, Decimal)), f'Nombre attendu : {value!r}'
    result = Decimal(str(value))
    assert result.is_finite(), f'Nombre non fini : {value!r}'
    return result


def validate_normalization(entry, monetary_sources):
    """Check published-scope EUR 2026 bounds without creating a FLOW estimate.

    Amounts remain in currency units (not thousands). Missing source prices and
    missing normalizations remain unknown; neither is silently replaced by zero.
    """
    ref_id = entry['id']
    price, norm = entry['cout_publie'], entry['normalisation_2026']
    assert price['devise'] in {'USD', 'CAD', 'AUD', 'GBP', 'EUR'}, f'{ref_id}: devise inconnue'
    assert entry['projet']['perimetre'] and entry['projet']['inclus_dans_prix'] and entry['projet']['exclus_du_prix'], f'{ref_id}: assiette publiée incomplète'
    assert isinstance(price['externe_confirme'], bool), f'{ref_id}: qualification externe invalide'
    assert price['statut'], f'{ref_id}: régime du prix absent'
    lo, hi = price['min'], price['max']
    lower, upper = norm['min_eur'], norm['max_eur']
    assert (lo is None) == (hi is None), f'{ref_id}: prix partiellement inconnu'
    assert (lower is None) == (upper is None), f'{ref_id}: normalisation partiellement inconnue'
    if lo is None:
        assert lower is None, f'{ref_id}: normalisation sans prix publié'
        return False
    assert 0 < number(lo) <= number(hi), f'{ref_id}: bornes de prix invalides'
    if lower is None:
        return False
    assert price['date_prix'] and norm['indice'] and norm['periode_depart'], f'{ref_id}: normalisation sans date ou indice'
    source_date = str(price['date_prix'])
    assert re.fullmatch(r'\d{4}-\d{2}(?:-\d{2})?', source_date), f'{ref_id}: date du prix invalide'
    dated = date.fromisoformat(source_date + '-01' if len(source_date) == 7 else source_date)
    periods = {source_date, source_date[:7], str(dated.year), f'{dated.year}-T{(dated.month-1)//3+1}', f'moyenne-{dated.year}'}
    assert str(norm['periode_depart']) in periods, f'{ref_id}: indice de départ sans concordance avec la date du prix'
    start, end, fx = (number(norm[k]) for k in ('valeur_depart', 'valeur_2026', 'devise_par_eur'))
    assert start > 0 and end > 0 and fx > 0, f'{ref_id}: facteur de normalisation invalide'
    exchanges = [value for key, value in monetary_sources.items() if key.startswith('change_bce_')]
    assert len(exchanges) == 1 and exchanges[0]['url'], 'Source de change BCE ambiguë ou absente'
    expected_fx = 1 if price['devise'] == 'EUR' else exchanges[0][price['devise'].lower() + '_par_eur']
    assert fx == number(expected_fx), f'{ref_id}: taux de change différent de sa source'
    if dated.year == 2026:
        assert start == end == 1, f'{ref_id}: montant 2026 réindexé'
    else:
        index_sources = {'USD': ('cpi_us', 'septembre_2026'), 'GBP': ('sppi_uk_informatique', 'trimestre_2026_t3'), 'CAD': ('ipc_canada', 'septembre_2026')}
        assert price['devise'] in index_sources, f'{ref_id}: source d’indice 2026 à qualifier'
        section, key = index_sources[price['devise']]
        assert end == number(monetary_sources[section][key]), f'{ref_id}: indice 2026 différent de sa source'
    assert 0 < number(lower) <= number(upper), f'{ref_id}: bornes normalisées invalides'
    for value, actual in ((lo, lower), (hi, upper)):
        calculated = number(value) * end / start / fx
        assert abs(calculated - number(actual)) <= 1, f'{ref_id}: actualisation incohérente: {calculated} vs {actual}'
    return True


def validate_reading(data):
    """Keep usefulness, price evidence and FLOW price transposition independent."""
    rubric = data['utilite_flow']
    labels = data['presentation_references']
    assert rubric['seuil_mise_en_avant'] in rubric['echelle']
    assert set(labels['postes']) == {'build', 'integration', 'mco_run'}
    for entry in data['references']:
        reading = entry['lecture_flow']
        assert reading['score_utilite'] in rubric['echelle'], entry['id']
        assert reading['raison'] and reading['enseignement'] and reading['date_revue'], entry['id']
        assert set(reading['postes']) == set(labels['postes']), entry['id']
        assert all(s in labels['statuts'] for s in reading['postes'].values()), entry['id']
        assert reading['integration'] and reading['mco_run'], entry['id']
        assert reading['preuves'], entry['id']
        for proof in reading['preuves']:
            assert proof['source'] in entry['sources'] and proof['localisation'], entry['id']
        for observation in reading['observations']:
            assert observation['source'] in entry['sources'], entry['id']
            assert observation['localisation'] and observation['periode'] and observation['assiette'], entry['id']
            assert observation['qualite_prix_source'] in data['echelle_qualite_prix_source'], entry['id']
            assert observation['devise'] in {'USD', 'CAD', 'AUD', 'GBP', 'EUR'}, entry['id']
            assert 0 < observation['min'] <= observation['max'], entry['id']
        if reading['postes']['mco_run'] == 'chiffre_separe':
            assert reading['observations'], entry['id']


def validate_market_references(data):
    """Validate already loaded evidence; no file reads, prints or mutations.

    Shared by the ordinary study loading path and the standalone diagnostic.
    Exploratory checks never populate the active economic model.
    """
    assert data['version_schema'] == 1
    validate_reading(data)
    references = data['references']
    ids = [entry['id'] for entry in references]
    assert len(ids) == len(set(ids)), 'Identifiants de références dupliqués'
    eligible = defaultdict(list)
    prices = 0
    normalized = 0
    for entry in references:
        ref_id = entry['id']
        assert entry['sources'], f'{ref_id}: source primaire absente'
        assert entry['contexte_business']['activite'], f'{ref_id}: activité absente'
        assert entry['projet']['perimetre'], f'{ref_id}: périmètre absent'
        price = entry['cout_publie']
        norm = entry['normalisation_2026']
        flow = entry['transposition_au_perimetre_flow_beaumanoir']
        assert 0 <= price['qualite_prix_source'] <= 5, ref_id
        assert 0 <= flow['truth_level'] <= 5, ref_id
        assert price['famille_source'], f'{ref_id}: famille de source absente'
        normalized += validate_normalization(entry, data['sources_monetaires'])
        prices += price['min'] is not None
        if flow['truth_level'] == 0:
            assert flow['cout_central_eur_2026'] is None, ref_id
            assert flow['fourchette_min_eur_2026'] is None, ref_id
            assert flow['fourchette_max_eur_2026'] is None, ref_id
        else:
            assert flow['cout_central_eur_2026'] is not None, (
                f'{ref_id}: truth level positif sans estimation chiffrée'
            )
            assert number(flow['cout_central_eur_2026']) > 0, ref_id
        if flow['truth_level'] >= data['analyse_dispersion']['criteres']['truth_level_minimum']:
            assert price['externe_confirme'], f'{ref_id}: assiette externe incertaine'
            assert flow['cohorte'], f'{ref_id}: cohorte non renseignée'
            central = flow['cout_central_eur_2026']
            lower = flow['fourchette_min_eur_2026']
            upper = flow['fourchette_max_eur_2026']
            assert central is not None and lower is not None and upper is not None, ref_id
            assert 0 < number(lower) <= number(central) <= number(upper), ref_id
            eligible[flow['cohorte']].append(entry)

    count_eligible = sum(len(group) for group in eligible.values())
    assert data['analyse_dispersion']['resultat_actuel']['references_eligibles'] == count_eligible, (
        'Mettre à jour analyse_dispersion.resultat_actuel après changement du registre'
    )

    # A published-project price interval is only an order-of-magnitude check.
    # It must never populate the FLOW/Beaumanoir counterfactual fields above.
    by_id = {entry['id']: entry for entry in references}
    market = data['reperes_exploratoires_marche']
    sap = market['grands_programmes_sap_publics']
    anchor_lows, anchor_highs = [], []
    for anchor in sap['ancres']:
        ref_id = anchor['reference_id']
        entry = by_id[ref_id]
        assert entry['cout_publie']['externe_confirme'], ref_id
        assert entry['transposition_au_perimetre_flow_beaumanoir']['truth_level'] == 0, ref_id
        norm = entry['normalisation_2026']
        excluded = number(anchor.get('lot_exclu_devise_origine', 0))
        factor = number(norm['valeur_2026']) / number(norm['valeur_depart']) / number(norm['devise_par_eur'])
        for bound, actual in (('min', 'montant_min_eur_2026'), ('max', 'montant_max_eur_2026')):
            expected = ((number(entry['cout_publie'][bound]) - excluded) * factor).quantize(
                Decimal('1'), rounding=ROUND_HALF_UP)
            assert expected == number(anchor[actual]), f'{ref_id}: ancre {bound} incohérente'
        anchor_lows.append(number(anchor['montant_min_eur_2026']))
        anchor_highs.append(number(anchor['montant_max_eur_2026']))
    assert min(anchor_lows) == number(sap['minimum_ancres_eur_2026'])
    assert max(anchor_highs) == number(sap['maximum_ancres_eur_2026'])
    assert floor(min(anchor_lows) / 1_000_000) == sap['plage_arrondie_m_eur_2026']['min']
    assert ceil(max(anchor_highs) / 1_000_000) == sap['plage_arrondie_m_eur_2026']['max']
    assert sap['verite_transposition_flow_beaumanoir'] == 0
    dynamics = market['contrepoints_dynamics']
    d365 = [by_id[ref_id] for ref_id in dynamics['references_ids']]
    assert all(entry['cout_publie']['externe_confirme'] for entry in d365)
    assert min(number(entry['normalisation_2026']['min_eur']) for entry in d365) == number(dynamics['minimum_eur_2026'])
    assert max(number(entry['normalisation_2026']['max_eur']) for entry in d365) == number(dynamics['maximum_eur_2026'])
    assert dynamics['verite_transposition_flow_beaumanoir'] == 0

    minimum = data['analyse_dispersion']['criteres']['references_independantes_minimum']
    assert isinstance(minimum, int) and not isinstance(minimum, bool) and minimum >= 2
    usable = 0
    cohorts = []
    for cohort, group in sorted(eligible.items()):
        families = [entry['cout_publie']['famille_source'] for entry in group]
        assert len(families) == len(set(families)), (
            f'{cohort}: sources corrélées ; constituer des familles indépendantes'
        )
        if len(group) < minimum:
            cohorts.append(dict(id=cohort, count=len(group), eligible=False))
            continue
        usable += 1
        values = [float(entry['transposition_au_perimetre_flow_beaumanoir']['cout_central_eur_2026'])
                  for entry in group]
        avg = mean(values)
        sample_variance = variance(values)
        cv = sample_variance ** 0.5 / avg
        cohorts.append(dict(id=cohort, count=len(group), eligible=True, mean=avg, variance=sample_variance, cv=cv))
    if usable == 0:
        assert data['analyse_dispersion']['resultat_actuel']['variance_eur_2026_carre'] is None
        assert data['analyse_dispersion']['resultat_actuel']['coefficient_variation'] is None
    return dict(references=len(references), prices=prices, normalized=normalized,
                eligible=count_eligible, minimum=minimum, usable=usable, cohorts=cohorts)


def analyze():
    report = validate_market_references(read(PATH))
    print(f"{report['references']} références ; {report['prices']} prix publiés ; "
          f"{report['normalized']} prix convertis en EUR 2026 ; "
          f"{report['eligible']} retraitements au périmètre FLOW Beaumanoir de truth level suffisant.")
    print('Stress test SAP/public : 7–20 M EUR 2026 aux périmètres publiés ; '
          'contrepoints Dynamics : 1,52–14,29 M EUR. Aucune borne FLOW/Beaumanoir démontrée.')
    for cohort in report['cohorts']:
        if not cohort['eligible']:
            print(f"{cohort['id']}: {cohort['count']} référence(s), seuil {report['minimum']} non atteint.")
        else:
            print(f"{cohort['id']}: n={cohort['count']}, moyenne={cohort['mean']:,.0f} EUR 2026, "
                  f"variance={cohort['variance']:,.0f} EUR², CV={cohort['cv']:.1%}.")
    if report['usable'] == 0:
        print('Dispersion non calculable : aucune cohorte indépendante suffisante.')


if __name__ == '__main__':
    analyze()
