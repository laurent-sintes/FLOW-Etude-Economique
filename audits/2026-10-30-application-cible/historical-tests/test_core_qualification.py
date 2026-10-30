"""Qualification behavior, including an isolated synthetic candidate, not calibration."""
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import patch
from jsonschema import ValidationError
from core_qualification import validate, summarize, candidate, QualificationError, SOURCE, MARKET_SOURCE, MARKET_PREFIX
from model_context import model_session
from validate_stacks import ROOT, read


def retained_fixture():
    """Synthetic effort values exercise the adapter; they never enter source files."""
    d = read(ROOT / SOURCE)
    d['purpose'] = 'qualification'
    for function in d['functions']:
        function['status'] = 'qualifie'
        function['observations'] = [dict(product_ref='erpnext', edition=None, version=None,
            classification='analogie', evidence_refs=['calibration-historique'],
            differences='Analogie synthétique réservée au test du contrat, sans constat produit réel.')]
        function['unknowns'] = []
    for lot in d['lots']:
        for ecosystem, rows in lot['estimates'].items():
            for effort in rows:
                effort.update(status='estime', decision='retenu',
                    jh=dict(bas=1, central=2 if effort['kind'] == 'developpeur' else 3, haut=4),
                    provenance=dict(origin='ingenierie', author=None, date='2026-10-28', evidence_refs=[],
                                    rationale='Hypothèse synthétique uniquement pour le test.', assisted_by_ai=True),
                    conditions=dict(team='Équipe fictive de test', environment='Fixture isolée',
                                    quality='Contrat uniquement', day_convention='JH développeur ou QA selon le type explicite'),
                    uncertainty=dict(lower_reason='Borne basse de test', upper_reason='Borne haute de test', shared_hypotheses=[]))
            if lot['id'] == 'lot-ingestion':
                rows[0]['mechanism_refs'] = ['reception-references']
            else:
                included = deepcopy(rows[0])
                included.update(id='reception-partagee', status='inclus', jh=None,
                    included_in=dict(lot_ref='lot-ingestion', effort_ref='developpeur'),
                    mechanism_refs=['reception-references'], explanation='Le lot propriétaire finance la réception commune.')
                rows.append(included)
    return d


def linked_market_fixture():
    d = retained_fixture()
    function = d['functions'][0]
    function['observations'] = []
    function['market_qualification_refs'] = [MARKET_PREFIX + 'test-ingestion']
    instruction = read(ROOT / MARKET_SOURCE)
    instruction['qualifications'] = [dict(id='test-ingestion',
        capability_ref=function['capability_refs'][0], product_ref='erpnext',
        need_refs=function['need_refs'][:], function_label='Fonction synthétique du test',
        evaluation_function_ref=function['id'], status='qualifie', classification='analogie',
        evidence_refs=[dict(source_ref='sources/benchmark-build-core-scm-2026-10-27.md',
                            location='Localisation synthétique réservée au test du contrat')],
        differences=['Analogie de test, sans constat produit réel.'], unknowns=[],
        review=dict(date='2026-10-28', reviewer='Relecteur synthétique du test', decision='retenu'))]
    def fixture_read(path):
        return deepcopy(instruction) if path == ROOT / MARKET_SOURCE else read(path)
    return d, instruction, fixture_read


class CoreQualificationTests(unittest.TestCase):
    def test_historical_pilot_keeps_unknowns_and_reference_without_new_numbers(self):
        d = validate()
        self.assertEqual(d['purpose'], 'pilote_historique')
        self.assertEqual(len(d['scope']['capability_refs']), 3)
        self.assertEqual(len(d['scope']['ecosystems']), 3)
        self.assertTrue(all(e['jh'] is None and e['review']['reviewer'] is None
                            for lot in d['lots'] for rows in lot['estimates'].values() for e in rows))
        report = summarize(d)
        self.assertEqual(len(report['historical_reference']), 3)
        for ecosystem in report['ecosystems'].values():
            self.assertFalse(ecosystem['complete'])
            self.assertEqual(len(ecosystem['unknown']), 6)
        with self.assertRaises(QualificationError):
            candidate(d)

    def test_candidate_counts_shared_work_once_and_separates_kinds(self):
        d = retained_fixture()
        before = deepcopy(d)
        active = (ROOT / 'source/recalibration-metier.yaml').read_bytes()
        result = candidate(d)
        self.assertFalse(result['applied'])
        for ecosystem in result['ecosystems'].values():
            self.assertEqual(ecosystem['totals_jh']['developpeur']['central'], 6)
            self.assertEqual(ecosystem['totals_jh']['qa_independante']['central'], 9)
            self.assertNotIn('pilotage', ecosystem['totals_jh'])
            self.assertIn('pilotage', ecosystem['unrepresented_effort_kinds'])
            self.assertEqual(sum(e['status'] == 'inclus' for e in ecosystem['efforts']), 2)
        self.assertEqual(d, before)
        self.assertEqual((ROOT / 'source/recalibration-metier.yaml').read_bytes(), active)

    def test_candidate_includes_dependencies_without_duplicate_owner(self):
        result = candidate(retained_fixture(), ['lot-accords'])
        self.assertEqual(result['lot_refs'], ['lot-accords', 'lot-ingestion'])
        self.assertEqual(result['ecosystems']['java-spring']['totals_jh']['developpeur']['central'], 4)

    def test_historical_purpose_blocks_candidate_even_with_retained_numbers(self):
        d = retained_fixture()
        d['purpose'] = 'pilote_historique'
        validate(d)
        with self.assertRaisesRegex(QualificationError, 'Historical qualification'):
            candidate(d)

    def test_local_evidence_must_be_frozen_with_its_declaration(self):
        d = retained_fixture()
        d['evidence']['calibration-historique']['reference'] = 'AGENTS.md'
        with self.assertRaisesRegex(QualificationError, 'declared for snapshot'):
            validate(d)

    def test_shared_mechanism_requires_an_explicit_owner_effort(self):
        d = retained_fixture()
        d['lots'][0]['estimates']['java-spring'][0]['mechanism_refs'] = []
        with self.assertRaisesRegex(QualificationError, 'explicit owner effort'):
            validate(d)

    def test_unknown_unretained_or_incomplete_estimate_blocks_candidate(self):
        for change in ('unknown', 'unretained', 'conditions', 'functions'):
            d = retained_fixture()
            effort = d['lots'][0]['estimates']['java-spring'][0]
            if change == 'unknown':
                effort.update(status='inconnu', decision='a_qualifier', jh=None)
            elif change == 'unretained':
                effort['decision'] = 'a_qualifier'
            elif change == 'conditions':
                effort['conditions']['team'] = None
            else:
                d['functions'][0]['status'] = 'a_qualifier'
            with self.subTest(change=change), self.assertRaises(QualificationError):
                candidate(d)

    def test_double_funding_unknown_refs_cycles_and_kind_changes_rejected(self):
        for change in ('double', 'missing', 'cycle', 'kind', 'mechanism_owner'):
            d = retained_fixture()
            included = d['lots'][1]['estimates']['java-spring'][-1]
            if change == 'double':
                included.update(status='estime', jh=dict(bas=1, central=2, haut=3), included_in=None)
            elif change == 'missing':
                included['included_in']['effort_ref'] = 'missing'
            elif change == 'cycle':
                d['lots'][0]['dependency_refs'] = ['lot-accords']
            elif change == 'kind':
                included['kind'] = 'qa_independante'
            else:
                d['mechanisms'][0]['owner_lot_ref'] = 'lot-accords'
            with self.subTest(change=change), self.assertRaises(QualificationError):
                validate(d)

    def test_null_zero_included_and_not_applicable_remain_distinct(self):
        d = retained_fixture()
        effort = d['lots'][0]['estimates']['java-spring'][1]
        effort['jh'] = dict(bas=0, central=0, haut=0)
        effort['explanation'] = None
        with self.assertRaises(QualificationError):
            validate(d)
        effort['explanation'] = 'Zéro explicite dans la fixture.'
        validate(d)
        effort.update(status='sans_objet', jh=None)
        validate(d)
        effort['jh'] = dict(bas=0, central=0, haut=0)
        with self.assertRaises(QualificationError):
            validate(d)

    def test_measured_provenance_and_human_review_require_evidence(self):
        d = retained_fixture()
        effort = d['lots'][0]['estimates']['java-spring'][0]
        effort['provenance']['origin'] = 'mesuree'
        with self.assertRaises(QualificationError):
            validate(d)
        effort['provenance']['origin'] = 'ingenierie'
        effort['review']['reviewer'] = 'Relecteur non attesté'
        with self.assertRaises(QualificationError):
            validate(d)

    def test_engineering_author_is_preserved_without_external_evidence_or_human_review(self):
        d = retained_fixture()
        effort = d['lots'][0]['estimates']['java-spring'][0]
        effort['provenance']['author'] = 'Auteur de l’estimation synthétique'
        self.assertEqual(effort['provenance']['evidence_refs'], [])
        result = candidate(d)
        row = next(e for e in result['ecosystems']['java-spring']['efforts']
                   if e['lot_ref'] == 'lot-ingestion' and e['id'] == 'developpeur')
        self.assertEqual(row['provenance']['author'], 'Auteur de l’estimation synthétique')
        self.assertEqual(row['review']['status'], 'non_realisee')
        self.assertIsNone(row['review']['reviewer'])

    def test_market_qualification_is_referenced_without_copying_source_facts(self):
        d, instruction, fixture_read = linked_market_fixture()
        before = deepcopy(d)
        with patch('core_qualification.read', side_effect=fixture_read):
            result = candidate(d)
        self.assertEqual(d, before)
        self.assertEqual(d['functions'][0]['observations'], [])
        ref = d['functions'][0]['market_qualification_refs'][0]
        self.assertEqual(result['market_qualifications'][ref]['qualification'], instruction['qualifications'][0])
        self.assertTrue(result['market_qualifications'][ref]['evidence_digests'][0]['sha256'])
        self.assertEqual(result['functions'][0]['market_qualification_refs'], [ref])

    def test_market_unknown_mismatched_unqualified_or_partial_refs_are_rejected(self):
        for change in ('unknown', 'capability', 'inverse', 'unqualified', 'partial'):
            d, instruction, fixture_read = linked_market_fixture()
            record = instruction['qualifications'][0]
            if change == 'unknown':
                d['functions'][0]['market_qualification_refs'] = [MARKET_PREFIX + 'missing']
            elif change == 'capability':
                record['capability_ref'] = d['functions'][1]['capability_refs'][0]
                record['need_refs'] = d['functions'][1]['need_refs'][:]
                record['evaluation_function_ref'] = None
            elif change == 'inverse':
                twin = deepcopy(d['functions'][0])
                twin.update(id='other-function', market_qualification_refs=[])
                twin['observations'] = deepcopy(d['functions'][1]['observations'])
                d['functions'].append(twin)
                record['evaluation_function_ref'] = 'other-function'
            elif change == 'unqualified':
                record.update(status='a_qualifier', unknowns=['Qualification de test en attente.'], review=None)
            else:
                record['need_refs'] = record['need_refs'][:1]
            with self.subTest(change=change), patch('core_qualification.read', side_effect=fixture_read), self.assertRaises(ValueError):
                candidate(d)

    def test_candidate_provenance_changes_with_the_resolved_local_market_proof(self):
        d, instruction, fixture_read = linked_market_fixture()
        proof_path = (ROOT / instruction['qualifications'][0]['evidence_refs'][0]['source_ref']).resolve()
        actual_read_bytes = Path.read_bytes
        def changed_bytes(path):
            return b'Changed proof in memory only' if path.resolve() == proof_path else actual_read_bytes(path)
        with patch('core_qualification.read', side_effect=fixture_read):
            before = candidate(d)
            with patch.object(Path, 'read_bytes', changed_bytes):
                after = candidate(d)
        self.assertEqual(before['qualification_sha256'], after['qualification_sha256'])
        self.assertNotEqual(before['inputs_sha256'], after['inputs_sha256'])
        self.assertNotEqual(before['market_qualifications'], after['market_qualifications'])

    def test_contract_rejects_unknown_fields_bad_dates_ranges_and_scopes(self):
        for change in ('field', 'date', 'range', 'scope', 'ecosystem', 'duplicate'):
            d = retained_fixture()
            effort = d['lots'][0]['estimates']['java-spring'][0]
            if change == 'field':
                effort['hidden_gain'] = 0.4
            elif change == 'date':
                effort['provenance']['date'] = '2026-02-30'
            elif change == 'range':
                effort['jh']['bas'] = 99
            elif change == 'scope':
                d['functions'][0]['need_refs'] = ['BC-088.01']
            elif change == 'ecosystem':
                del d['lots'][0]['estimates']['rust']
            else:
                d['lots'][0]['estimates']['java-spring'].append(deepcopy(effort))
            with self.subTest(change=change), self.assertRaises((ValidationError, QualificationError)):
                validate(d)

    def test_cache_is_scoped_and_returns_isolated_copies(self):
        with model_session():
            first = validate()
            first['lots'][0]['result'] = 'Mutation du consommateur'
            self.assertNotEqual(first, validate())
        self.assertNotEqual(first, validate())


if __name__ == '__main__':
    unittest.main()
