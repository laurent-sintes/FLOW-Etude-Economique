"""Validate and derive the documentary Core product market references.

This module never feeds the five-option economic calculation. It keeps the
source measures, method and FLOW coverage claims internally consistent before
they enter the public market reading.
"""

from copy import deepcopy
from datetime import date
import math
import re
from pathlib import Path
from urllib.parse import urlsplit

from validate_stacks import ROOT


OFFER_STATUSES = {'sans_objet', 'inclus', 'option', 'non_demontre', 'mixte'}
PARITY_STATUSES = {'non_demontree', 'non_evaluee', 'partielle', 'demontree'}
PRODUCT_FAMILIES = {'oss', 'proprietaire'}
PRODUCT_STATUSES = {'diagnostic_mesure', 'analyse_documentaire'}
CODE_OBSERVABILITY = {'mesure_oss', 'code_public_non_mesure', 'code_non_public'}
REQUIRED_PRODUCT_FICHES = {'erpnext', 'microsoft', 'sap', 'odoo-community', 'tryton', 'axelor-open-suite'}
NEW_MEASURED_OSS = {'odoo-community', 'tryton', 'axelor-open-suite'}
DEPLOYMENT_EVIDENCE_STATUS = {'recent', 'historique_non_reconfirme', 'source_non_datee'}
COMMERCE_SCOPE_STATUSES = {'dans_perimetre', 'hors_perimetre', 'partiel', 'non_demontre'}
COMMERCE_SEGMENTS = {'retail', 'ecommerce', 'wholesale'}
CANDIDATE_CATEGORIES = {'erp_oss', 'ecosysteme_complementaire'}
CANDIDATE_PRIORITIES = {'prioritaire', 'a_etudier', 'secondaire'}
COMPONENT_SELECTIONS = {
    'frappe': {'retenu', 'elargi'},
    'erpnext': {'planification', 'execution', 'fabrication_entiere'},
    'insights': {'serveur', 'interface', 'v3'},
}
OUT_OF_SCOPE_BCS = {'BC-016', 'BC-017', 'BC-074', 'BC-075'}
COMMIT_RE = re.compile(r'[0-9a-f]{40}\Z')


def _fail(path, reason):
    raise ValueError(f'ERR_MARKET_OSS {path}: {reason}')


def _object(value, keys, path):
    if not isinstance(value, dict) or set(value) != set(keys):
        _fail(path, f'fields must be {sorted(keys)}')
    return value


def _text(value, path):
    if not isinstance(value, str) or not value.strip():
        _fail(path, 'nonempty text required')
    return value


def _integer(value, path, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, int) or value < (1 if positive else 0):
        _fail(path, 'positive integer required' if positive else 'nonnegative integer required')
    return value


def _number(value, path, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        _fail(path, 'finite number required')
    if (positive and value <= 0) or (not positive and value < 0):
        _fail(path, 'positive number required' if positive else 'nonnegative number required')
    return float(value)


def _reference(value, path):
    _text(value, path)
    parsed = urlsplit(value)
    if parsed.scheme:
        if parsed.scheme != 'https' or not parsed.netloc:
            _fail(path, 'HTTPS source required')
        return value
    relative = value.partition('#')[0]
    if not relative.startswith(('source/', 'sources/', 'tools/')) or '\\' in relative:
        _fail(path, 'repository source path required')
    target = (ROOT / relative).resolve()
    if not target.is_relative_to(ROOT.resolve()) or not target.is_file():
        _fail(path, 'source file missing')
    return value


def _selection(value, path):
    _object(value, {'fichiers', 'pncloc'}, path)
    _integer(value['fichiers'], path + '.fichiers', positive=True)
    _integer(value['pncloc'], path + '.pncloc', positive=True)


def _validate_measure(measure):
    _object(measure, {'unite', 'script_ref', 'limites', 'versions', 'composants', 'sous_ensembles'}, 'mesure')
    if measure['unite'] != 'PNCLOC':
        _fail('mesure.unite', 'PNCLOC expected')
    _reference(measure['script_ref'], 'mesure.script_ref')
    if not measure['script_ref'].startswith('tools/'):
        _fail('mesure.script_ref', 'local script required')
    _text(measure['limites'], 'mesure.limites')
    versions = measure['versions']
    if not isinstance(versions, list) or len(versions) != 3:
        _fail('mesure.versions', 'three pinned product versions required')
    found = set()
    for index, item in enumerate(versions):
        path = f'mesure.versions[{index}]'
        _object(item, {'id', 'version', 'commit', 'url'}, path)
        if item['id'] not in COMPONENT_SELECTIONS or item['id'] in found:
            _fail(path + '.id', 'unique frappe, erpnext or insights id required')
        found.add(item['id'])
        _text(item['version'], path + '.version')
        if not isinstance(item['commit'], str) or not COMMIT_RE.fullmatch(item['commit']):
            _fail(path + '.commit', '40-character Git SHA required')
        _reference(item['url'], path + '.url')
        expected = f"https://github.com/frappe/{item['id']}/tree/{item['commit']}"
        if item['url'] != expected:
            _fail(path + '.url', 'URL must identify the pinned commit')
    if found != set(COMPONENT_SELECTIONS):
        _fail('mesure.versions', 'missing product version')
    components = _object(measure['composants'], COMPONENT_SELECTIONS, 'mesure.composants')
    for product, allowed in COMPONENT_SELECTIONS.items():
        selections = _object(components[product], allowed, f'mesure.composants.{product}')
        for key, value in selections.items():
            _selection(value, f'mesure.composants.{product}.{key}')
    if components['frappe']['retenu']['pncloc'] >= components['frappe']['elargi']['pncloc']:
        _fail('mesure.composants.frappe', 'retained selection must be smaller than expanded')
    erp = components['erpnext']
    if not erp['planification']['pncloc'] < erp['execution']['pncloc'] < erp['fabrication_entiere']['pncloc']:
        _fail('mesure.composants.erpnext', 'manufacturing selections must increase')
    insights = components['insights']
    for key in ('fichiers', 'pncloc'):
        if insights['serveur'][key] + insights['interface'][key] != insights['v3'][key]:
            _fail('mesure.composants.insights.v3', f'{key} must equal server + interface')
    subsets = _object(measure['sous_ensembles'], {'automation_flow'}, 'mesure.sous_ensembles')
    automation = _object(subsets['automation_flow'], {'parent', 'fichiers', 'pncloc'}, 'mesure.sous_ensembles.automation_flow')
    if automation['parent'] != 'frappe':
        _fail('mesure.sous_ensembles.automation_flow.parent', 'frappe expected')
    for key in ('fichiers', 'pncloc'):
        _integer(automation[key], f'mesure.sous_ensembles.automation_flow.{key}', positive=True)
        if automation[key] >= components['frappe']['retenu'][key]:
            _fail('mesure.sous_ensembles.automation_flow', 'subset must be smaller than parent')


def _validate_method(method):
    _object(method, {'nom', 'source_ref', 'coefficient_a', 'exposant_nominal', 'heures_mois_personne', 'heures_jh', 'limites'}, 'methode')
    _text(method['nom'], 'methode.nom')
    _reference(method['source_ref'], 'methode.source_ref')
    for key in ('coefficient_a', 'exposant_nominal', 'heures_mois_personne', 'heures_jh'):
        _number(method[key], 'methode.' + key, positive=True)
    _text(method['limites'], 'methode.limites')


def _validate_singularity_proofs(proofs, path):
    if (not isinstance(proofs, list) or not proofs or
            not all(isinstance(proof, str) for proof in proofs) or len(proofs) != len(set(proofs))):
        _fail(path, 'distinct source evidence required')
    for index, proof in enumerate(proofs):
        _reference(proof, f'{path}[{index}]')


def _validate_singularities(singularities):
    path = 'cadre_comparaison.singularites'
    _object(singularities, {'methode', 'prudence', 'preuve_ref', 'produits'}, path)
    _text(singularities['methode'], path + '.methode')
    _text(singularities['prudence'], path + '.prudence')
    _reference(singularities['preuve_ref'], path + '.preuve_ref')
    profiles = _object(singularities['produits'], REQUIRED_PRODUCT_FICHES, path + '.produits')
    sections = {
        'atout': {'titre', 'constat', 'comparaison', 'limite', 'preuves'},
        'extension': {'au_dela_flow', 'complements_flow', 'limite', 'preuves'},
        'integration': {'mecanismes', 'limite', 'preuves'},
        'charge': {'mecanismes', 'repere_observe', 'limite', 'preuves'},
    }
    for product, profile in profiles.items():
        prefix = f'{path}.produits.{product}'
        _object(profile, set(sections) | {'commerce'}, prefix)
        for section, fields in sections.items():
            entry_path = f'{prefix}.{section}'
            entry = _object(profile[section], fields, entry_path)
            for field in fields - {'preuves', 'repere_observe'}:
                _text(entry[field], entry_path + '.' + field)
            if section == 'charge' and entry['repere_observe'] is not None:
                _text(entry['repere_observe'], entry_path + '.repere_observe')
            _validate_singularity_proofs(entry['preuves'], entry_path + '.preuves')
        commerce = _object(profile['commerce'], COMMERCE_SEGMENTS, prefix + '.commerce')
        for segment, entry in commerce.items():
            entry_path = f'{prefix}.commerce.{segment}'
            _object(entry, {'statut', 'constat', 'limite', 'preuves'}, entry_path)
            if entry['statut'] not in COMMERCE_SCOPE_STATUSES:
                _fail(entry_path + '.statut', 'unknown commercial scope status')
            _text(entry['constat'], entry_path + '.constat')
            _text(entry['limite'], entry_path + '.limite')
            _validate_singularity_proofs(entry['preuves'], entry_path + '.preuves')


def _validate_comparison_frame(comparison, retained_bcs):
    _object(comparison, {'introduction', 'axes', 'singularites'}, 'cadre_comparaison')
    _text(comparison['introduction'], 'cadre_comparaison.introduction')
    _validate_singularities(comparison['singularites'])
    axes = comparison['axes']
    if not isinstance(axes, list) or not axes:
        _fail('cadre_comparaison.axes', 'at least one axis required')
    found = set()
    for index, axis in enumerate(axes):
        path = f'cadre_comparaison.axes[{index}]'
        _object(axis, {'id', 'titre', 'bc_refs', 'cible_flow', 'essai'}, path)
        identifier = _text(axis['id'], path + '.id')
        if identifier in found:
            _fail(path + '.id', 'duplicate axis id')
        found.add(identifier)
        for key in ('titre', 'cible_flow', 'essai'):
            _text(axis[key], path + '.' + key)
        refs = axis['bc_refs']
        if not isinstance(refs, list) or not refs or not all(isinstance(ref, str) for ref in refs) or len(refs) != len(set(refs)):
            _fail(path + '.bc_refs', 'unique BC references required')
        if not set(refs) <= retained_bcs:
            _fail(path + '.bc_refs', 'unknown or excluded BC reference')
    return found


def _validate_product_fiches(fiches, axis_ids, oss):
    if not isinstance(fiches, dict) or not REQUIRED_PRODUCT_FICHES <= set(fiches):
        _fail('fiches_produit', 'six studied product fiches required')
    for key, fiche in fiches.items():
        path = f'fiches_produit.{key}'
        _object(fiche, {'id', 'nom', 'famille', 'statut', 'date_observation', 'version_edition', 'preuve_ref',
                        'composition', 'code', 'references_deploiement', 'prix_observe_eur_ht',
                        'prix_retraite_flow_eur_2026', 'evaluations'} | ({'qualification_prix'} if 'qualification_prix' in fiche else set()), path)
        if _text(fiche['id'], path + '.id') != key:
            _fail(path + '.id', 'must match fiche key')
        for field in ('nom', 'date_observation', 'version_edition'):
            _text(fiche[field], path + '.' + field)
        _reference(fiche['preuve_ref'], path + '.preuve_ref')
        if fiche['famille'] not in PRODUCT_FAMILIES:
            _fail(path + '.famille', 'unknown product family')
        if fiche['statut'] not in PRODUCT_STATUSES:
            _fail(path + '.statut', 'unknown study status')
        composition = _object(fiche['composition'], {'produits', 'technologies', 'preuve_ref'}, path + '.composition')
        products = composition['produits']
        if not isinstance(products, list) or not products or not all(isinstance(item, str) and item.strip() for item in products) or len(products) != len(set(products)):
            _fail(path + '.composition.produits', 'unique nonempty products required')
        _text(composition['technologies'], path + '.composition.technologies')
        _reference(composition['preuve_ref'], path + '.composition.preuve_ref')
        code = _object(fiche['code'], {'observabilite', 'mesure_ref', 'calcul_ref', 'pncloc', 'effort_jh', 'limite'}, path + '.code')
        if code['observabilite'] not in CODE_OBSERVABILITY:
            _fail(path + '.code.observabilite', 'unknown code observability')
        _text(code['limite'], path + '.code.limite')
        references = fiche['references_deploiement']
        if references is not None:
            if not isinstance(references, list) or not references:
                _fail(path + '.references_deploiement', 'nonempty list or null required')
            seen_references = set()
            for index, reference in enumerate(references):
                ref_path = f'{path}.references_deploiement[{index}]'
                _object(reference, {'id', 'organisation', 'taille_organisation', 'entite_equipee',
                                    'usage_atteste', 'edition_deploiement', 'annee_preuve',
                                    'actualite', 'limite_flow', 'preuves'}, ref_path)
                identifier = _text(reference['id'], ref_path + '.id')
                if identifier in seen_references:
                    _fail(ref_path + '.id', 'duplicate deployment reference')
                seen_references.add(identifier)
                for field in ('organisation', 'taille_organisation', 'entite_equipee',
                              'usage_atteste', 'limite_flow'):
                    _text(reference[field], ref_path + '.' + field)
                if reference['edition_deploiement'] is not None:
                    _text(reference['edition_deploiement'], ref_path + '.edition_deploiement')
                if reference['annee_preuve'] is not None:
                    year = _integer(reference['annee_preuve'], ref_path + '.annee_preuve', positive=True)
                    if year > int(fiche['date_observation'][:4]):
                        _fail(ref_path + '.annee_preuve', 'future evidence year')
                if reference['actualite'] not in DEPLOYMENT_EVIDENCE_STATUS:
                    _fail(ref_path + '.actualite', 'unknown evidence recency')
                if reference['actualite'] == 'source_non_datee' and reference['annee_preuve'] is not None:
                    _fail(ref_path + '.annee_preuve', 'undated source requires null year')
                if reference['actualite'] != 'source_non_datee' and reference['annee_preuve'] is None:
                    _fail(ref_path + '.annee_preuve', 'dated source requires year')
                proofs = reference['preuves']
                if (not isinstance(proofs, list) or len(proofs) < 2
                        or not all(isinstance(proof, str) for proof in proofs)
                        or len(proofs) != len(set(proofs))):
                    _fail(ref_path + '.preuves', 'distinct size and usage sources required')
                for proof_index, proof in enumerate(proofs):
                    _reference(proof, f'{ref_path}.preuves[{proof_index}]')
        if key == 'erpnext':
            if code['pncloc'] is not None or code['effort_jh'] is not None:
                _fail(path + '.code', 'ERPNext size and effort must be derived from its single OSS study')
            if fiche['famille'] != 'oss' or fiche['statut'] != 'diagnostic_mesure' or code['observabilite'] != 'mesure_oss':
                _fail(path, 'ERPNext must identify the measured OSS diagnostic')
            if code['mesure_ref'] != 'etude_oss.mesure' or code['calcul_ref'] != 'etude_oss.calcul_cocomo':
                _fail(path + '.code', 'ERPNext must reference the single OSS measure and calculation')
            if fiche['preuve_ref'] != oss['preuve_ref'] or fiche['date_observation'] != oss['date_observation']:
                _fail(path, 'ERPNext proof and observation date must match the measured study')
        elif key in NEW_MEASURED_OSS:
            if fiche['famille'] != 'oss' or fiche['statut'] != 'diagnostic_mesure' or code['observabilite'] != 'mesure_oss':
                _fail(path, 'candidate must identify a measured OSS diagnostic')
            if code['mesure_ref'] != 'tools/oss_candidates_code_audit.py' or code['calcul_ref'] is not None:
                _fail(path + '.code', 'candidate must reference its pinned source counter without an unevaluated effort calculation')
            _reference(code['mesure_ref'], path + '.code.mesure_ref')
            _integer(code['pncloc'], path + '.code.pncloc', positive=True)
            if code['effort_jh'] is not None:
                _fail(path + '.code.effort_jh', 'candidate JH require a separately modelled and derived method')
        elif code['observabilite'] == 'code_non_public':
            if fiche['famille'] != 'proprietaire' or fiche['statut'] != 'analyse_documentaire':
                _fail(path, 'nonpublic code requires a documentary proprietary fiche')
            if code['mesure_ref'] is not None or code['calcul_ref'] is not None or code['pncloc'] is not None or code['effort_jh'] is not None:
                _fail(path + '.code', 'proprietary core has no measured code or COCOMO calculation')
        elif code['observabilite'] == 'code_public_non_mesure':
            if fiche['famille'] != 'oss' or code['mesure_ref'] is not None or code['calcul_ref'] is not None or code['pncloc'] is not None or code['effort_jh'] is not None:
                _fail(path + '.code', 'unmeasured OSS code has no size or effort')
        else:
            _fail(path + '.code', 'additional measured code requires an audited calculation')
        _validate_product_prices(fiche, path)
        evaluations = _object(fiche['evaluations'], axis_ids, path + '.evaluations')
        for axis_id, entry in evaluations.items():
            prefix = f'{path}.evaluations.{axis_id}'
            _object(entry, {'fonctionnalite', 'statut_offre', 'offre', 'limite', 'preuves', 'parite_flow'}, prefix)
            for field in ('fonctionnalite', 'offre', 'limite'):
                _text(entry[field], prefix + '.' + field)
            if entry['statut_offre'] not in OFFER_STATUSES:
                _fail(prefix + '.statut_offre', 'unknown offer status')
            if entry['parite_flow'] not in PARITY_STATUSES:
                _fail(prefix + '.parite_flow', 'unknown FLOW parity status')
            proofs = entry['preuves']
            if not isinstance(proofs, list) or not proofs:
                _fail(prefix + '.preuves', 'source evidence required')
            for index, proof in enumerate(proofs):
                _reference(proof, f'{prefix}.preuves[{index}]')


def _validate_product_prices(fiche, path):
    """A documented reconstruction price may be recorded, never auto-budgeted.

    Existing unknowns need no fabricated metadata. Licensing tariffs belong to
    their economic sources and cannot masquerade as a reconstruction price.
    """
    qualification = fiche.get('qualification_prix')
    prices = {'observe': fiche['prix_observe_eur_ht'], 'retraite_flow': fiche['prix_retraite_flow_eur_2026']}
    if qualification is None:
        if any(value is not None for value in prices.values()):
            _fail(path + '.prix', 'non-null reconstruction price requires qualification_prix')
        return
    _object(qualification, prices, path + '.qualification_prix')
    for kind, amount in prices.items():
        prefix = path + '.qualification_prix.' + kind
        details = qualification[kind]
        if amount is None:
            if details is not None:
                _fail(prefix, 'unknown price requires null qualification')
            continue
        _number(amount, path + '.prix.' + kind, positive=True)
        fields = {'nature', 'date', 'devise', 'unite', 'regime_fiscal', 'perimetre', 'inclusions', 'exclusions', 'sequence', 'preuves'}
        if kind == 'retraite_flow':
            fields |= {'annee_valeur', 'pont_perimetre', 'hypotheses', 'revue'}
        _object(details, fields, prefix)
        if details['nature'] != 'reconstruction_produit':
            _fail(prefix + '.nature', 'reconstruction product scope required, not licence prices')
        if details['devise'] != 'EUR' or details['unite'] != 'EUR' or details['regime_fiscal'] != 'HT':
            _fail(prefix, 'price field requires EUR units excluding tax')
        for field in ('date', 'perimetre', 'inclusions', 'exclusions', 'sequence'):
            _text(details[field], prefix + '.' + field)
        try:
            date.fromisoformat(details['date'])
        except ValueError:
            _fail(prefix + '.date', 'ISO date required')
        proofs = details['preuves']
        if not isinstance(proofs, list) or not proofs:
            _fail(prefix + '.preuves', 'located price evidence required')
        for proof in proofs:
            _object(proof, {'source_ref', 'localisation'}, prefix + '.preuves')
            _reference(proof['source_ref'], prefix + '.preuves.source_ref')
            _text(proof['localisation'], prefix + '.preuves.localisation')
        if kind == 'retraite_flow':
            if prices['observe'] is None or details['annee_valeur'] != 2026:
                _fail(prefix, 'FLOW transposition requires observed price and EUR 2026 basis')
            for field in ('pont_perimetre', 'hypotheses'):
                _text(details[field], prefix + '.' + field)
            review = _object(details['revue'], {'date', 'auteur', 'decision'}, prefix + '.revue')
            _text(review['auteur'], prefix + '.revue.auteur')
            _text(review['date'], prefix + '.revue.date')
            try:
                date.fromisoformat(review['date'])
            except ValueError:
                _fail(prefix + '.revue.date', 'ISO review date required')
            if review['decision'] != 'retenu':
                _fail(prefix + '.revue.decision', 'explicit retained review required')


def _validate_candidates(candidates, studied_ids):
    if not isinstance(candidates, list) or not candidates:
        _fail('candidats_a_etudier', 'nonempty separate shortlist required')
    found = set()
    for index, candidate in enumerate(candidates):
        path = f'candidats_a_etudier[{index}]'
        _object(candidate, {'id', 'nom', 'categorie', 'priorite', 'motif', 'preuve_ref'}, path)
        identifier = _text(candidate['id'], path + '.id')
        if identifier in studied_ids or identifier in found:
            _fail(path + '.id', 'duplicate or already studied candidate')
        found.add(identifier)
        for field in ('nom', 'motif'):
            _text(candidate[field], path + '.' + field)
        if candidate['categorie'] not in CANDIDATE_CATEGORIES:
            _fail(path + '.categorie', 'unknown candidate category')
        if candidate['priorite'] not in CANDIDATE_PRIORITIES:
            _fail(path + '.priorite', 'unknown study priority')
        _reference(candidate['preuve_ref'], path + '.preuve_ref')


def enrich_market_products(reperes, capability_ids):
    """Validate comparable product fiches and derive their single measured effort."""
    value = deepcopy(reperes)
    for field in ('etude_oss', 'cadre_comparaison', 'fiches_produit', 'candidats_a_etudier'):
        if field not in value:
            _fail('reperes_build_core', f'missing {field}')
    oss = enrich_market_oss(value['etude_oss'], capability_ids)
    retained_bcs = capability_ids - OUT_OF_SCOPE_BCS
    axis_ids = _validate_comparison_frame(value['cadre_comparaison'], retained_bcs)
    _validate_product_fiches(value['fiches_produit'], axis_ids, oss)
    _validate_candidates(value['candidats_a_etudier'], set(value['fiches_produit']))
    code = value['fiches_produit']['erpnext']['code']
    code['pncloc'] = oss['calcul_cocomo']['pncloc_total']
    code['effort_jh'] = oss['calcul_cocomo']['jh']
    # Preserve the current market drawer contract without a second source of truth.
    oss['comparaison'] = {
        'introduction': value['cadre_comparaison']['introduction'],
        'axes': [dict(axis, produits={key: {name: item for name, item in fiche['evaluations'][axis['id']].items()
                                           if name != 'parite_flow'}
                                    for key, fiche in value['fiches_produit'].items()})
                 for axis in value['cadre_comparaison']['axes']],
    }
    value['etude_oss'] = oss
    return value


def _validate_architecture(architecture):
    _object(architecture, {'technologies', 'points_chauds'}, 'architecture')
    for section in ('technologies', 'points_chauds'):
        entries = architecture[section]
        if not isinstance(entries, list) or not entries:
            _fail('architecture.' + section, 'nonempty list required')
        found = set()
        for index, entry in enumerate(entries):
            path = f'architecture.{section}[{index}]'
            _object(entry, {'id', 'titre', 'description', 'preuve_ref'}, path)
            identifier = _text(entry['id'], path + '.id')
            if identifier in found:
                _fail(path + '.id', 'duplicate architecture id')
            found.add(identifier)
            _text(entry['titre'], path + '.titre')
            _text(entry['description'], path + '.description')
            _reference(entry['preuve_ref'], path + '.preuve_ref')


def enrich_market_oss(oss, capability_ids):
    """Return an isolated, checked study with one nominal OSS code calculation."""
    value = deepcopy(oss)
    _object(value, {'id', 'titre', 'date_observation', 'nature', 'statut', 'niveau_comparaison',
                    'preuve_ref', 'prix_observe_eur_ht', 'prix_retraite_flow_eur_2026',
                    'perimetre', 'architecture', 'mesure', 'methode', 'calcul_cocomo', 'lecture'}, 'etude_oss')
    for key in ('id', 'titre', 'date_observation'):
        _text(value[key], 'etude_oss.' + key)
    if value['nature'] != 'diagnostic_reconstruction_oss':
        _fail('etude_oss.nature', 'documentary OSS reconstruction diagnostic required')
    if value['statut'] != 'non_calibre' or value['niveau_comparaison'] != 'axes_selectifs':
        _fail('etude_oss', 'non-calibrated selective comparison expected')
    _reference(value['preuve_ref'], 'etude_oss.preuve_ref')
    if value['prix_observe_eur_ht'] is not None or value['prix_retraite_flow_eur_2026'] is not None:
        _fail('etude_oss.prix', 'no observed or transposed price exists')
    perimeter = _object(value['perimetre'], {'objet', 'bc_total', 'bc_exclus', 'exclus', 'assiette_effort'}, 'perimetre')
    for key in ('objet', 'exclus', 'assiette_effort'):
        _text(perimeter[key], 'perimetre.' + key)
    _integer(perimeter['bc_total'], 'perimetre.bc_total', positive=True)
    if not isinstance(capability_ids, set) or len(capability_ids) != perimeter['bc_total']:
        _fail('perimetre.bc_total', 'does not match the FLOW grid')
    excluded = perimeter['bc_exclus']
    if not isinstance(excluded, list) or not all(isinstance(ref, str) for ref in excluded) or len(excluded) != len(set(excluded)) or set(excluded) != OUT_OF_SCOPE_BCS:
        _fail('perimetre.bc_exclus', 'four explicit Finance/product-development BCs required')
    if not OUT_OF_SCOPE_BCS <= capability_ids:
        _fail('perimetre.bc_exclus', 'BC missing from FLOW grid')
    _validate_architecture(value['architecture'])
    _validate_measure(value['mesure'])
    _validate_method(value['methode'])
    calculation = _object(value['calcul_cocomo'], {'selections'}, 'calcul_cocomo')
    selections = _object(calculation['selections'], COMPONENT_SELECTIONS, 'calcul_cocomo.selections')
    if selections['insights'] != 'v3':
        _fail('calcul_cocomo.selections.insights', 'complete Insights v3 expected')
    method = value['methode']
    components = value['mesure']['composants']
    physical = {}
    exact_months = {}
    for product, selection in selections.items():
        if selection not in COMPONENT_SELECTIONS[product]:
            _fail('calcul_cocomo.selections.' + product, 'unknown source selection')
        physical[product] = components[product][selection]['pncloc']
        ksloc = physical[product] / 1000
        exact_months[product] = method['coefficient_a'] * ksloc ** method['exposant_nominal']
    calculation['pncloc_par_composant'] = physical
    calculation['pncloc_total'] = sum(physical.values())
    calculation['mois_personne'] = sum(exact_months.values())
    hours_per_day = method['heures_mois_personne'] / method['heures_jh']
    calculation['jh'] = round(calculation['mois_personne'] * hours_per_day)
    cumulative = 0.0
    previous = 0
    allocated = {}
    for product in ('frappe', 'erpnext', 'insights'):
        cumulative += exact_months[product] * hours_per_day
        rounded = round(cumulative)
        allocated[product] = rounded - previous
        previous = rounded
    calculation['jh_par_composant'] = allocated
    reading = _object(value['lecture'], {'conclusion', 'limites'}, 'lecture')
    for key in ('conclusion', 'limites'):
        _text(reading[key], 'lecture.' + key)
    return value
