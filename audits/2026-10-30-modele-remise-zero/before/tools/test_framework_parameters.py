"""Read-only projections, evidence and real personal parameter availability."""
from copy import deepcopy
import unittest

from document_excerpt import document_excerpt
from framework_parameters import compile_framework_parameters, hydrate_framework_parameters
from test_support import study_copy
from validate_stacks import ROOT, read


class FrameworkParametersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study = study_copy()
        cls.integration = read(ROOT / 'source/integration.yaml')
        cls.maintenance = read(ROOT / 'source/maintenance.yaml')
        cls.inflation = read(ROOT / 'source/inflation.yaml')

    def setUp(self):
        self.framework = deepcopy(self.study.content['framework'])
        for key in ('roles', 'specialist', 'sources'):
            self.framework.pop(key, None)
        for option in self.framework['tariffs']:
            for key in ('context', 'source'):
                option.pop(key, None)
            for price in option['prices']:
                price.pop('evidence', None)
        for row in self.framework['other']:
            for key in ('source', 'value_source', 'personal'):
                row.pop(key, None)
        for row in self.framework['inflation']:
            for key in ('evidence', 'personal'):
                row.pop(key, None)
        for key in ('support', 'frontend'):
            self.framework[key].pop('source', None)

    def compile(self, **changes):
        values = dict(framework=self.framework, stacks=self.study.content['stacks'],
                      calibration=self.study.content['calibration'], ui=self.study.ui,
                      documents=self.study.files, integration=self.integration,
                      maintenance=self.maintenance, inflation=self.inflation)
        values.update(changes)
        return compile_framework_parameters(**values)

    def assertRetained(self, original, enriched):
        if isinstance(original, dict):
            for key, value in original.items():
                self.assertIn(key, enriched)
                self.assertRetained(value, enriched[key])
        elif isinstance(original, list):
            self.assertEqual(len(original), len(enriched))
            for before, after in zip(original, enriched):
                self.assertRetained(before, after)
        else:
            self.assertEqual(original, enriched)

    def test_all_previous_values_and_full_justifications_survive_in_isolated_copy(self):
        before = deepcopy(self.framework)
        baseline = deepcopy(self.study.baseline)
        contract = self.study.simulation_contract()
        result = self.compile()
        self.assertRetained(before, result)
        self.assertEqual(self.framework, before)
        self.assertEqual(result, self.compile(framework=result))
        result['tariffs'][0]['prices'][0]['method'] = 'changed copy'
        result['specialist']['activites_refs'].clear()
        self.assertEqual(self.framework, before)
        self.assertEqual(self.study.baseline, baseline)
        self.assertEqual(self.study.simulation_contract(), contract)

    def test_profiles_purchase_context_evidence_and_specialist_follow_their_owners(self):
        result = self.compile()
        for key, role in result['roles'].items():
            self.assertEqual(role['name'], self.integration['roles'][key]['nom'])
            self.assertEqual(role['scope'], self.integration['roles'][key]['perimetre'])
        for option in result['tariffs']:
            model = self.study.content['stacks'][option['key']]['model']
            self.assertEqual(option['context']['purchase_mode'], model['interventions']['mode_achat'])
            self.assertEqual(option['context']['geography'], model['interventions']['base_geographique'])
            for price in option['prices']:
                expected = model['interventions']['tarifs'][price['key']]['sources']
                self.assertEqual([row['id'] for row in price['evidence']], expected)
                for row in price['evidence']:
                    self.assertEqual(row['title'], model['sources'][row['id']]['titre'])
                    self.assertEqual(row['path'], model['sources'][row['id']]['reference'])
        source = self.study.content['calibration']
        self.assertRetained(source['specialisation_maintenance_make'], result['specialist'])
        self.assertEqual(result['specialist']['factors_jh'], dict(
            bas=source['sensibilite']['jh_bas'], central=1, haut=source['sensibilite']['jh_haut']))
        self.assertNotIn('factors_jh', result['workload'])

    def test_personal_controls_distinguish_direct_aggregate_and_reference(self):
        result = self.compile()
        means = {row['key']: row for row in result['other']}
        self.assertEqual(means['cloud_calcul_conteneurs']['personal']['kind'], 'aggregate')
        self.assertEqual(means['cloud_calcul_conteneurs']['personal']['key'], 'hebergement')
        self.assertEqual(means['power_platform']['personal']['key'], 'licences_complementaires')
        self.assertEqual(means['power_platform']['personal']['options'], ['microsoft'])
        for key in ('outillage_support', 'outillage_realisation', 'accompagnement_make'):
            self.assertEqual(means[key]['personal'], {'kind': 'reference'})
        self.assertEqual(means['accompagnement_make']['status'], 'replaced')
        self.assertTrue(all(row['personal']['kind'] == 'direct' for row in result['inflation']))

        ui = deepcopy(self.study.ui)
        ui['parameters']['common'] = [r for r in ui['parameters']['common'] if r['key'] != 'inflation_tjm']
        for spec in ui['parameters']['option']:
            if spec['key'] in ('hebergement', 'ipaas'):
                spec['modes'] = ['Buy']
        changed = self.compile(ui=ui)
        means = {row['key']: row for row in changed['other']}
        self.assertEqual(means['cloud_calcul_conteneurs']['personal']['kind'], 'reference')
        self.assertEqual(means['ipaas_make_microsoft']['personal']['options'], ['microsoft'])
        prices = {row['key']: row for row in changed['inflation']}
        self.assertEqual(prices['tjm_ingenierie']['personal']['kind'], 'reference')

    def test_unknown_evidence_documents_profiles_and_projection_conflicts_fail(self):
        stacks = deepcopy(self.study.content['stacks'])
        stacks['java-spring']['model']['interventions']['tarifs']['expert']['sources'].append('UNKNOWN')
        with self.assertRaisesRegex(ValueError, 'unknown evidence'):
            self.compile(stacks=stacks)
        stacks = deepcopy(self.study.content['stacks'])
        stacks['java-spring']['model']['sources']['SILKHOM']['reference'] = 'javascript:bad'
        with self.assertRaisesRegex(ValueError, 'invalid evidence URL'):
            self.compile(stacks=stacks)
        with self.assertRaisesRegex(ValueError, 'undeclared document'):
            self.compile(documents=set(self.study.files) - {'source/integration.yaml'})
        maintenance = deepcopy(self.maintenance)
        maintenance['roles']['developpement']['nom'] = 'Different role'
        with self.assertRaisesRegex(ValueError, 'inconsistent activity roles'):
            self.compile(maintenance=maintenance)
        projection = self.compile()
        projection['specialist']['plafond_jh_avant_sensibilite'] += 1
        with self.assertRaisesRegex(ValueError, 'conflicting projection'):
            self.compile(framework=projection)

    def test_local_reading_references_resolve_to_the_expected_excerpt(self):
        result = self.compile()
        paths = set()

        def collect(value):
            if isinstance(value, dict):
                for entry in value.values():
                    collect(entry)
            elif isinstance(value, list):
                for entry in value:
                    collect(entry)
            elif isinstance(value, str) and value.startswith('source/') and '#' in value:
                paths.add(value)

        collect(result)
        for reference in paths:
            with self.subTest(reference=reference):
                path, fragment = reference.split('#', 1)
                file = self.study.document_path(path)
                focus = document_excerpt(file.read_text(encoding='utf-8'), file.suffix, fragment)['focus']
                self.assertEqual(focus['status'], 'matched')
        hydrated = hydrate_framework_parameters(self.framework, self.study.content['stacks'],
            self.study.content['calibration'], self.study.ui, self.study.files)
        self.assertEqual(hydrated, result)


if __name__ == '__main__':
    unittest.main()
