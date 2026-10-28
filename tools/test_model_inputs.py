"""Editable-input contracts: reject silent omissions and prove parameter effects."""
import unittest
from copy import deepcopy
from jsonschema import Draft202012Validator,ValidationError
from validate_stacks import ROOT,read
from model_inputs import annual_scenario,annual_scenario_from,validate_funding
from composable_costs import initial_ledger,annual_split
from test_support import study_copy
from unittest.mock import patch

class ModelInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.study=study_copy()

    def test_current_cycle_contracts_and_supplier_inclusions(self):
        from validate_cycle import validate
        self.assertTrue(validate())

    def test_stacks_and_indexation_have_no_document_registration_gate(self):
        from validate_stacks import validate,validate_inflation
        validate();validate_inflation()

    def test_removed_core_cannot_return_as_silent_editable_data(self):
        schema=Draft202012Validator(read(ROOT/'source/schema-chiffrage.yaml'))
        for slug in self.study.options:
            doc=read(ROOT/f'source/chiffrage/chiffrage-{slug}.yaml')
            self.assertNotIn('core',doc)
            self.assertFalse({'features','solution'} & doc['dependances'].keys())
            schema.validate(doc)
            doc['core']=[]
            with self.assertRaises(ValidationError):schema.validate(doc)

    def test_publication_manifest_preserves_evidence_and_excludes_removed_core(self):
        declared=set(read(ROOT/'config/publication.yaml')['documents'])
        self.assertEqual(self.study.files,declared|set(self.study.data['empreintes']))
        self.assertIn('sources/client/microsoft-questionnaire.xlsx',declared)
        self.assertIn('sources/client/sap-questionnaire.xlsx',declared)
        self.assertIn('archives/etude-avant-yaml-2026-10-24/07-analyse-synvance.md',declared)
        self.assertNotIn('source/core-system-features.yaml',declared)

    def test_valuation_keeps_prices_without_building_fifteen_service_years(self):
        from calculate_costs import calculate_option,validate_inputs
        cal,docs=validate_inputs()
        expected={'java-spring':1,'dotnet':1,'rust':1,'microsoft':5,'sap':2}
        for option in self.study.economic['options']:
            slug=option['stack'];self.assertEqual(len(option['maintenance_annuelle']),expected[slug])
            diagnostic=calculate_option(slug,docs[slug],cal)
            self.assertEqual(len(diagnostic['maintenance_annuelle']),15)
            self.assertEqual(option['maintenance_annuelle'],diagnostic['maintenance_annuelle'][:expected[slug]])
            for key,value in option['synthese_eur_ht'].items():self.assertEqual(value,diagnostic['synthese_eur_ht'][key])

    def test_volumes_are_derived_and_reject_competing_values(self):
        source=read(ROOT/'source/maintenance.yaml')['scenario_annuel']
        source['volumes']['demandes_n1_par_utilisateur_an']=12
        result=annual_scenario_from(source)
        self.assertEqual(result['volumes']['demandes_n1_an'],11400)
        self.assertEqual(result['volumes']['escalades_n3_an'],2280)
        source['volumes']['demandes_n1_an']=1
        with self.assertRaises(AssertionError):annual_scenario_from(source)

    def test_deployment_shapes_shares_roles_and_dates_are_checked(self):
        config=read(ROOT/'source/modele-composable.yaml');group=read(ROOT/'source/deploiement-groupe.yaml')
        changes=[lambda g:g['perimetre']['repartition_usagers_par_unite'].pop(),
                 lambda g:g['perimetre'].__setitem__('repartition_usagers_par_unite',[.5]*4),
                 lambda g:g['scenarios']['central']['ouvertures_mois'].__setitem__(0,40),
                 lambda g:g['deploiement']['roles_pct'].__setitem__('integration',80)]
        for change in changes:
            altered=deepcopy(group);change(altered)
            with self.assertRaises(AssertionError):validate_funding(config,altered,annual_scenario())

    def test_unknown_yaml_classification_field_is_rejected(self):
        config=read(ROOT/'source/modele-composable.yaml');group=read(ROOT/'source/deploiement-groupe.yaml')
        config['classification_make']['MAI-008']['accidental prose']=None
        with self.assertRaises(AssertionError):validate_funding(config,group,annual_scenario())

    def test_group_contract_rejects_unknown_fields_and_competing_volume_inputs(self):
        config=read(ROOT/'source/modele-composable.yaml');group=read(ROOT/'source/deploiement-groupe.yaml')
        def unknown_root(g):g['duree_mois']=30
        def unknown_section(g):g['deploiement']['coordination_pct']=10
        def unknown_scenario(g):g['scenarios']['central']['duree_annees']=3
        def missing_scenario(g):g['scenarios']['central'].pop('duree_mois')
        def extra_scenario(g):g['scenarios']['other']=deepcopy(g['scenarios']['central'])
        def competing_volume(g):g['scenarios']['central']['corrections_core_par_an']=12
        def missing_volume(g):g['scenarios']['central'].pop('corrections_core_par_an_ref')
        def wrong_volume(g):g['scenarios']['central']['corrections_core_par_an_ref']='demandes_n1_an'
        for change in (unknown_root,unknown_section,unknown_scenario,missing_scenario,extra_scenario,
                       competing_volume,missing_volume,wrong_volume):
            altered=deepcopy(group);change(altered)
            with self.subTest(change=change.__name__),self.assertRaises(AssertionError):
                validate_funding(config,altered,annual_scenario())

    def test_group_substitution_is_complete_unique_and_matches_replaced_work(self):
        config=read(ROOT/'source/modele-composable.yaml');group=read(ROOT/'source/deploiement-groupe.yaml')
        def unknown(s):s['activites_conservees'][0]='INT-999'
        def duplicate_retained(s):s['activites_conservees'].append('INT-001')
        def duplicate_removed(s):s['activites_retirees'].append('INT-012')
        def missing(s):s['activites_conservees'].remove('INT-001')
        def overlap(s):s['activites_conservees'].append('INT-012')
        def wrong_replacement(s):s['activites_conservees'][0],s['activites_retirees'][0]='INT-012','INT-001'
        def false_accompaniment(s):s['accompagnement_retire']=False
        def false_preparation(s):s['preparation_retiree']=False
        for change in (unknown,duplicate_retained,duplicate_removed,missing,overlap,wrong_replacement,
                       false_accompaniment,false_preparation):
            altered=deepcopy(group);change(altered['substitution'])
            with self.subTest(change=change.__name__),self.assertRaises(AssertionError):
                validate_funding(config,altered,annual_scenario())

    def test_group_validation_uses_catalogue_and_preserves_editable_values(self):
        config=read(ROOT/'source/modele-composable.yaml');group=read(ROOT/'source/deploiement-groupe.yaml')
        catalogue=read(ROOT/'source/integration.yaml');original=deepcopy(group)
        changed=deepcopy(group)
        changed['scenarios']['central']['direction_etp']=.7
        changed['scenarios']['central']['deploiement_jh_par_unite'][0]=450
        changed['scenarios']['central'].pop('corrections_core_par_an_ref')
        changed['scenarios']['central']['corrections_core_par_an']=17
        _,compiled=validate_funding(config,changed,annual_scenario(),catalogue)
        self.assertEqual(compiled['scenarios']['central']['direction_etp'],.7)
        self.assertEqual(compiled['scenarios']['central']['corrections_core_par_an'],17)
        self.assertEqual(compiled['scenarios']['central']['deploiement_jh_par_unite'][0],450)
        self.assertNotIn('contexte',changed['perimetre'])
        self.assertEqual(group,original)
        catalogue['activites'].append({**deepcopy(catalogue['activites'][0]),'id':'INT-014'})
        with self.assertRaisesRegex(AssertionError,'Unclassified integration'):
            validate_funding(config,group,annual_scenario(),catalogue)

    def test_hosting_selection_and_classification_are_executed(self):
        o=deepcopy(self.study.options['java-spring']);ref=o['composable']['reference_services']
        before=initial_ledger(o,ref)
        o['composable']['inputs']['config']['hebergement_build']['cas_central']='soutenu'
        after=initial_ledger(o,ref)
        amount=lambda rows:sum(r['amount'] for r in rows if r['id'].startswith('hebergement_build/'))
        self.assertGreater(amount(after),amount(before))
        o['composable']['inputs']['config']['classification_make']['MAI-001']['responsabilite']='mco_client'
        changed=initial_ledger(o,ref)
        self.assertTrue(all(r['responsibility']=='mco_client' for r in changed if r['id'].startswith('MAI-001')))
        self.assertEqual(sum(r['amount'] for r in changed),sum(r['amount'] for r in after))
        cfg=o['composable']['inputs']['config'];group=o['composable']['inputs']['group']
        economic=next(e for e in self.study.economic['options'] if e['stack']==o['stack'])
        cal=o['composable']['inputs']['calibration']
        base=annual_split(o['stack'],economic,o['base_annuelle']['services_mco'],ref['core'],cal)
        with patch('composable_costs.funding_inputs',return_value=(cfg,group)):
            shifted=annual_split(o['stack'],economic,o['base_annuelle']['services_mco'],ref['core'],cal)
        self.assertGreater(shifted['mco_client'],base['mco_client'])
        self.assertEqual(round(sum(shifted.values()),2),round(sum(base.values()),2))

if __name__=='__main__':unittest.main()
