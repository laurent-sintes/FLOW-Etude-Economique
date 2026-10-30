"""Checks for scenario boundaries, baseline parity and read-only document routing."""
from copy import deepcopy
import json
import math
import re
import unittest
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from test_support import study_copy
from study_app import Study, ScenarioError
from serve_study_app import make_handler
from project_investment import project, phase_expense
from validate_stacks import ROOT, read


class StudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.study=study_copy()
    def setUp(self): self.p=deepcopy(self.study.parameters)

    def test_global_faq_has_resolvable_links_and_live_reference_figures(self):
        study=self.study; faq=study.content['faq']; ui=study.ui
        reference_group=next(g for g in ui['navigation_groups'] if 'faq' in g['items'])
        self.assertEqual(reference_group['items'],['faq','glossaire'])
        self.assertFalse(reference_group['sequential'])
        self.assertEqual(ui['document_routes']['source/faq-sponsors.md'],'#faq')
        self.assertNotIn('explanation_document',ui)
        self.assertEqual(len({q['id'] for q in faq['questions']}),len(faq['questions']))
        self.assertEqual({q['category'] for q in faq['questions']},{c['id'] for c in faq['categories']})
        for q in faq['questions']:
            self.assertTrue(q['answer'] and q['paragraphs'] and q['links'] and q['sources'])
            for link in q['links']: self.assertIn(link['route'].split('?')[0],ui['pages'])
            for source in q['sources']: self.assertTrue(study.document_path(source['path']).is_file())
        values={f['binding']:f['value'] for q in faq['questions'] for f in q.get('figures',[])}
        self.assertEqual(values['options.java-spring.integration'],study.baseline['options'][0]['integration'])
        self.assertEqual(values['options.java-spring.hosting_build'],102000)
        before=study.baseline
        try:
            self.p['options']['java-spring']['build_mois']=60
            study.baseline=study.simulate(self.p)
            updated=study._faq()
            changed={f['binding']:f['value'] for q in updated['questions'] for f in q.get('figures',[])}
            self.assertNotEqual(values['options.java-spring.hosting_build'],changed['options.java-spring.hosting_build'])
            self.assertEqual(changed['options.java-spring.hosting_build'],127500)
        finally: study.baseline=before

    def test_faq_rejects_dangling_numeric_bindings(self):
        from unittest.mock import patch
        import study_app
        original=study_app.read
        broken=deepcopy(self.study.content['faq'])
        question=next(q for q in broken['questions'] if q.get('figures'))
        question['figures'][0]['binding']='reference.missing'
        with patch.object(study_app,'read',side_effect=lambda path:broken if path.name=='faq-sponsors.yaml' else original(path)):
            with self.assertRaisesRegex(ValueError,'ERR_FAQ_BINDING'): self.study._faq()

    def test_reading_guide_proofs_terms_and_menu_are_resolvable(self):
        guide=self.study.content['guide']
        self.assertEqual(len(guide['etapes']),6)
        self.assertEqual([n['id'] for n in self.study.ui['nav']],
            ['synthese','logique','perimetres','build','exploitation','market','simulation-hypotheses','simulations','simulation-depenses','faq','glossaire'])
        grouped=[i for g in self.study.ui['navigation_groups'] for i in g['items']]
        self.assertEqual(grouped,['logique','perimetres','build','exploitation','market','simulation-hypotheses','simulations','simulation-depenses','faq','glossaire'])
        self.assertEqual([(g['label'],g['items']) for g in self.study.ui['navigation_groups'][:2]],
                         [('Comprendre',['logique','perimetres']),('Estimer',['build','exploitation','market'])])
        self.assertEqual([p['id'] for p in self.study.ui['context_pages']],['synvance'])
        for piece in guide['pieces']: self.assertTrue(self.study.document_path(piece['path']).is_file())
        for step in guide['etapes']:
            for term in step['notions']: self.assertIn(term,self.study.glossary['notions'])
        for term in self.study.glossary['notions'].values():
            self.assertIn(term['famille'],self.study.glossary['familles'])
            self.assertTrue(self.study.document_path(term['source_ref']).is_file())

    def test_prices_share_one_thousands_display_without_rescaling_inputs(self):
        labels=self.study.ui['reading']
        for ref in self.study.content['market']['references']:
            self.assertIn(ref['cout_publie']['statut'],labels['price_kinds'])
        ui=self.study.ui
        self.assertEqual(ui['monetary_display'],dict(scale=1000,decimals=0,rate_scale=1,rate_decimals=0,quantity_decimals=1))
        self.assertEqual(ui['labels']['money_unit'],'k€ HT')
        self.assertEqual(ui['labels']['normalized_money_unit'],'k€ 2026')
        self.assertEqual(ui['labels']['price_unit'],'€ HT / JH')
        self.assertNotIn('money_scale',self.study.content['sponsor']['affichage'])
        self.assertNotIn('normalized_scale',labels)
        for spec in ui['parameters']['option']:
            if spec['scale']==1000:
                self.assertTrue(spec['unit'].startswith('k€'))
                for option in self.study.baseline['options']:
                    if option['mode'] in spec['modes']:
                        value=self.study.parameters['options'][option['stack']][spec['key']]
                        self.assertGreaterEqual(value,spec['min']*spec['scale'])
                        self.assertLessEqual(value,spec['max']*spec['scale'])
        # Presentation precision does not change the scenario's semantic contract.
        contract=self.study.simulation_contract()
        before=deepcopy(ui['monetary_display'])
        try:
            ui['monetary_display']['decimals']=2
            self.assertEqual(contract,self.study.simulation_contract())
        finally:
            ui['monetary_display']=before

    def test_market_usefulness_is_not_a_fabricated_flow_price(self):
        from analyze_cost_references import validate_reading
        market=self.study.content['market']
        validate_reading(market)
        references={r['id']:r for r in market['references']}
        self.assertEqual(len(references),15)
        self.assertGreater(len({r['lecture_flow']['score_utilite'] for r in references.values()}),1)
        for ref in references.values():
            self.assertEqual(ref['lecture_flow']['postes']['build'],'non_etudie')
            self.assertIsNone(ref['transposition_au_perimetre_flow_beaumanoir']['cout_central_eur_2026'])
        jt=references['velrada-jt-johnson-2022']['lecture_flow']['observations'][0]
        self.assertEqual((jt['min'],jt['devise']),(98000,'AUD'))
        broken=deepcopy(market)
        broken['references'][0]['lecture_flow']['observations'][0]['source']='https://unbound.example/'
        with self.assertRaises(AssertionError): validate_reading(broken)

    def test_reading_guide_rejects_unbound_proofs(self):
        from unittest.mock import patch
        import study_app
        original=study_app.read
        broken=deepcopy(self.study.content['guide'])
        broken['etapes'][0]['preuves']=['unknown-proof']
        with patch.object(study_app,'read',side_effect=lambda path:broken if path.name=='parcours-synvance.yaml' else original(path)):
            with self.assertRaisesRegex(ValueError,'ERR_GUIDE_PROOF'): self.study._synvance_guide()

    def test_reading_journey_connects_the_sponsor_questions_without_dead_ends(self):
        ui=self.study.ui
        expected=['synthese','logique','perimetres','build','exploitation','market','simulation-hypotheses','simulations','simulation-depenses','synthese']
        for page,next_page in zip(expected,expected[1:]):
            link=ui['reading_journey']['steps'][page]
            self.assertEqual(link['to'].split('?')[0],next_page)
            self.assertTrue(link['takeaway'] and link['text'])
            self.assertNotIn('title',link)
            self.assertIn(next_page,{n['id'] for n in ui['nav']})
        self.assertEqual(set(ui['reading_journey']['steps']),{n['id'] for n in ui['nav']+ui['context_pages']})
        self.assertEqual(ui['reading_journey']['steps']['synvance']['to'],'perimetres')
        self.assertEqual(ui['reading_journey']['steps']['glossaire']['to'],'synthese')
        self.assertNotIn('features',{s['id'] for s in ui['perimeter_sections']})
        self.assertNotIn('purchases',{s['id'] for s in ui['reading']['sections']})
        self.assertEqual([s['id'] for s in ui['estimation_sections']],['build','integration','annual'])
        self.assertIn('work',{s['id'] for s in ui['estimation_reading']['sections']['build']})
        pages=ui['simulation_workspace']['pages']
        self.assertEqual(set(pages),{'parameters','comparison','annual'})
        self.assertEqual(len(set(pages.values())),3)
        nav={n['id'] for n in ui['nav']}
        self.assertTrue(set(pages.values())<=nav)
        self.assertTrue(all(p in ui['pages'] for p in pages.values()))
        groups=[g for g in ui['navigation_groups'] if set(g['items'])==set(pages.values())]
        self.assertEqual(len(groups),1)

    def test_parameter_matrix_explains_noneditable_cells_and_uses_engine_results(self):
        matrix=self.study.ui['simulation_workspace']['parameter_matrix']
        parameters=self.study.ui['parameters']['option']
        options=self.study.baseline['options']
        expected={(s['key'],o['mode']) for s in parameters for o in options if o['mode'] not in s['modes']}
        actual={(key,mode) for key,cells in matrix['readonly'].items() for mode in cells}
        self.assertEqual(actual,expected)
        for key,cells in matrix['readonly'].items():
            for mode,cell in cells.items():
                self.assertTrue(cell['help'])
                if 'result_path' in cell:
                    self.assertEqual(mode,'Make')
                    self.assertIn(key,('integration','integration_mois'))
                    value=self.study.baseline['options'][0] if cell.get('result_scope')=='option' else self.study.baseline
                    for part in cell['result_path']: value=value[part]
                    self.assertIsInstance(value,(int,float))
                    self.assertGreater(value,0)
                else:
                    self.assertTrue(cell['label'])
        self.assertEqual(matrix['readonly']['integration']['Make']['result_path'],['integration'])
        self.assertEqual(matrix['readonly']['integration']['Make']['result_scope'],'option')
        self.assertEqual(matrix['readonly']['integration_mois']['Make']['result_path'],['make_integration_months'])

    def test_reload_contract_tracks_meaning_not_prices_or_bounds(self):
        before=self.study.simulation_contract()
        ui=deepcopy(self.study.ui)
        try:
            self.study.ui['parameters']['common'][0]['max']+=1
            self.study.ui['parameters']['common'][0]['label']='renamed'
            self.assertEqual(before,self.study.simulation_contract())
            self.study.ui['parameters']['common'][0]['scale']*=10
            self.assertNotEqual(before,self.study.simulation_contract())
            self.study.ui=deepcopy(ui)
            self.study.ui['simulation_contract_version']+=1
            self.assertNotEqual(before,self.study.simulation_contract())
        finally:self.study.ui=ui

    def test_ui_rejects_malformed_inline_prose(self):
        bad=deepcopy(self.study.ui)
        bad['nav'][0]['unquoted fragment']=None
        with self.assertRaises(ValueError): self.study.validate_ui(bad)

    def test_annual_responsibilities_reconcile_without_splitting_bundles(self):
        for slug in ('java-spring','dotnet','rust','microsoft','sap'):
            view=self.study.content['stacks'][slug]['economic_reading']
            self.assertAlmostEqual(sum(b['total'] for b in view['buckets'].values()),view['total'],places=2)
            option=next(o for o in self.study.baseline['options'] if o['stack']==slug)
            editor=option['editor_prices'][0] if option['editor_prices'] else 0
            self.assertAlmostEqual(view['total'],sum(option['annual_base'].values())+editor,places=2)
            items=[i for b in view['buckets'].values() for i in b['items']]
            self.assertEqual(len(items),len({i['id'] for i in items}))
            self.assertEqual(view['buckets']['shared_editor']['total'],editor)
        buckets=self.study.content['stacks']['sap']['economic_reading']['buckets']
        self.assertIn('rfi-mco',{i['id'] for i in buckets['shared_services']['items']})
        self.assertNotIn('MAI-002',{i['id'] for b in buckets.values() for i in b['items']})

    def test_make_evolutions_keep_core_and_integration_costs_once(self):
        from validate_stacks import read, ROOT
        for slug in ('java-spring','dotnet','rust'):
            buckets=self.study.content['stacks'][slug]['economic_reading']['buckets']
            core={i['id']:i['montant'] for i in buckets['socle']['items']}
            integration={i['id']:i['montant'] for i in buckets['integration']['items']}
            self.assertGreater(core['MAI-009/core'],0)
            self.assertGreater(integration['MAI-009'],0)
            economic=next(o for o in read(ROOT/'source/couts-15-ans.yaml')['options'] if o['stack']==slug)
            evolution=next(a for a in economic['maintenance_activites'] if a['activite']=='MAI-009')
            self.assertAlmostEqual(core['MAI-009/core']+integration['MAI-009'],evolution['cout_diagnostique_eur_ht'],places=2)
            self.assertIn('complements',{i['id'] for i in buckets['run']['items']})
            self.assertNotIn('complements',integration)

    def test_architecture_keeps_every_component_once_and_marks_facets(self):
        for c in self.study.content['stacks'].values():
            cards=[i for l in c['architecture'] for g in l['groups'] for i in g['items']]
            expected={i['id'] for i in c['model']['elements']}
            primary=[i['id'] for i in cards if not i['facet']]
            self.assertEqual(len(primary),len(set(primary)))
            self.assertEqual(set(primary),expected)
            self.assertTrue(all(i['id'] in expected for i in cards))
            self.assertTrue(all(i['fondement'] in self.study.content['reading']['architecture']['fondements'] for i in cards))

    def test_all_scope_rows_explain_meaning_cost_and_required_evidence(self):
        self.assertEqual(len(self.study.content['scope']),10)
        for row in self.study.content['scope']:
            self.assertTrue(all(row['lecture'][k] for k in ('sens','exemple','impact','verification','source')))

    def test_complexity_grid_has_separate_reviewed_calibration(self):
        grid=self.study.content['complexity']
        self.assertEqual(len(grid['rows']),88)
        self.assertEqual(sum(len(r['fonctions']) for r in grid['rows']),258)
        self.assertEqual(sum(len(r['variantes']) for r in grid['rows']),74)
        self.assertEqual(len({r['hierarchie'][1]['id'] for r in grid['rows']}),9)
        self.assertEqual(len({r['hierarchie'][2]['id'] for r in grid['rows']}),28)
        self.assertTrue(all('calibration' not in r and 'complexite' not in r for r in grid['rows']))
        self.assertTrue(all(not stack['features'] for slug,stack in self.study.content['stacks'].items() if self.study.options[slug]['mode']=='Make'))
        self.assertEqual(len(self.study.content['buy_review']['revues']),178)
        self.assertEqual(len(self.study.content['integration_paths']['scenarios']),43)

    def test_sponsor_summary_reconciles_all_horizons_with_service_and_remaining(self):
        summary=self.study.content['sponsor']
        self.assertEqual([h['years'] for h in summary['horizons']],[3,5,7,10])
        options={o['stack']:o for o in self.study.baseline['options']}
        for view in summary['horizons']:
            self.assertEqual(len(view['rows']),len(options))
            rows={r['stack']:r for r in view['rows']}
            for slug,row in rows.items():
                h=next(h for h in options[slug]['horizons'] if h['years']==view['years'])
                self.assertEqual((row['total'],row['remaining'],row['service_years'],row['stage']),
                                 (h['totals']['total'],h['remaining'],h['service_years'],h['stage']))
                self.assertEqual(row['service_start_month'],options[slug]['service_start_month'])
            reference=rows[view['make_reference']]
            self.assertEqual(reference['mode'],'Make')
            self.assertEqual(reference['total'],min(r['total'] for r in rows.values() if r['mode']=='Make'))
            self.assertEqual({c['buy'] for c in view['comparisons']},{s for s,o in options.items() if o['mode']=='Buy'})
            for c in view['comparisons']:
                self.assertEqual(c['delta'],round(reference['total']-rows[c['buy']]['total'],2))
                self.assertEqual(c['make_service_years'],reference['service_years'])
                self.assertEqual(c['buy_service_years'],rows[c['buy']]['service_years'])
        self.assertTrue(all(r['service_years']==0 and r['remaining']>0 for r in summary['horizons'][0]['rows'] if r['mode']=='Make'))

    def test_make_anchor_excludes_generic_work_but_keeps_supplier_prices(self):
        from validate_stacks import read,ROOT
        current={o['stack']:o for o in self.study.economic['options']}
        f=self.study.data['sensibilite_finance_sap'];s=current['sap']
        generic=sum(r['cout_eur_ht'] for r in s['features'] if r['traitement']=='complement_integration')
        rate=read(ROOT/'source/calibration-couts.yaml')['pilotage']['complements_buy_pct']/100
        self.assertAlmostEqual(f['complements_generiques_exclus_ancre_make_eur_ht'],generic*(1+rate),places=2)
        anchor=s['synthese_eur_ht']['integration']-f['retrait_indicatif_eur_ht']-f['complements_generiques_exclus_ancre_make_eur_ht']
        self.assertAlmostEqual(anchor,self.study.baseline['anchor']['ancre_avant_bonus_eur_ht'],places=2)

    def test_sponsor_reference_does_not_adopt_personal_simulations(self):
        before=deepcopy(self.study.content['sponsor'])
        self.p['options']['java-spring']['build']+=1_000_000
        self.study.simulate(self.p)
        self.assertEqual(self.study._sponsor_summary(),before)

    def test_sponsor_sources_and_navigation_are_resolvable(self):
        summary=self.study.content['sponsor']
        for path in summary['dependances']:
            self.assertTrue(self.study.document_path(path).is_file())
        for c in summary['decision']['criteres']+summary['decision']['preuves']:
            self.assertTrue(self.study.document_path(c['source']).is_file())
        self.assertEqual(self.study.ui['initial_view'],'synthese')
        routes={r['id'] for r in self.study.ui['nav']}
        self.assertTrue(all(a['route'] in routes for a in summary['decision_suivante']['actions']))

    def test_essential_reader_groups_framework_before_economic_pages(self):
        from document_excerpt import document_excerpt
        essential=self.study.ui['essential']
        self.assertEqual([item['id'] for item in essential['nav']],['synvance','perimetre-retenu','vision','modele','conditions-realisation','marche','complexite','calcul-net','calcul-run','leviers','capacite-realisation','etude-marche','parametres','evaluation-core','comparer','se-projeter','simuler','glossaire'])
        self.assertEqual(set(essential['pages']),{'synvance','synvance-microsoft','synvance-sap','perimetre-retenu','vision','modele','conditions-realisation','complexite','calcul-net','calcul-run','marche','leviers','capacite-realisation','etude-marche','parametres','comparer','evaluation-core','se-projeter','simuler','glossaire'})
        self.assertEqual([group['items'] for group in essential['nav_groups']],
                         [['synvance','perimetre-retenu'],['vision','modele','conditions-realisation','marche','complexite','calcul-net','calcul-run','leviers'],['capacite-realisation'],['etude-marche','parametres','evaluation-core','comparer','se-projeter','simuler'],['glossaire']])
        self.assertEqual([phase['key'] for phase in essential['structure']['phases']],['obtention','integration','services'])
        for concept in essential['concepts']:
            self.assertIn(concept['notion'],self.study.glossary['notions'])
        cost_keys={row['key'] for row in essential['model_rows']}
        self.assertTrue(all(row.get('examples') for row in essential['model_rows']))
        self.assertEqual(len(next(row for row in essential['model_rows'] if row['key']=='obtention')['bullets']),2)
        self.assertIn('Licences',next(row for row in essential['model_rows'] if row['key']=='grouped_buy')['text'])
        phase_keys=set()
        for phase in essential['calendar']:
            self.assertEqual(len(phase['costs']),len(set(phase['costs'])))
            self.assertTrue(set(phase['costs'])<=cost_keys)
            phase_keys.update(phase['costs'])
        self.assertEqual(phase_keys,cost_keys)
        for proof in essential['proofs'].values():
            source=proof['source']
            path=self.study.document_path(source)
            self.assertTrue(path.is_file())
            fragment=source.partition('#')[2]
            self.assertEqual(document_excerpt(path.read_text(encoding='utf-8'),path.suffix,fragment)['focus']['status'],'matched',source)

    def test_essential_complexity_keeps_native_capabilities_and_ordinal_axes(self):
        compact=self.study.bootstrap(essential=True)['content']['complexity']
        grid=self.study.content['complexity']
        self.assertEqual(len(compact['rows']),88)
        self.assertFalse(compact['axes'])
        self.assertEqual([r['capacite_id'] for r in compact['rows']],[r['capacite_id'] for r in grid['rows']])
        for row in compact['rows']:
            self.assertNotIn('complexite',row)
            self.assertNotIn('fonctions',row)
            self.assertIn('definition',row)

    def test_core_evaluation_exposes_derived_make_ranges_and_no_buy_build(self):
        rows=self.study.bootstrap(essential=True)['content']['core_evaluation']
        self.assertEqual(len(rows),5)
        for row in rows:
            baseline=next(option for option in self.study.baseline['options'] if option['stack']==row['stack'])
            self.assertAlmostEqual(row['build_eur_ht'],baseline['build'],places=2)
            if row['mode']=='Make':
                self.assertLessEqual(row['ranges_jh']['bas'],row['ranges_jh']['central'])
                self.assertLessEqual(row['ranges_jh']['central'],row['ranges_jh']['haut'])
                central=row['ranges_jh']['central']
                if row['units']:
                    self.assertEqual(central, sum(u['total_jh'] for u in row['units']))
                    self.assertIsNone(row['uncertainty_pct'])
                    self.assertEqual(row['estimation_status'], 'partially_estimated')
                elif central:
                    self.assertEqual(row['uncertainty_pct']['down'],round(100*(central-row['ranges_jh']['bas'])/central,1))
                    self.assertEqual(row['uncertainty_pct']['up'],round(100*(row['ranges_jh']['haut']-central)/central,1))
                else:
                    self.assertIsNone(row['uncertainty_pct'])
                    self.assertEqual(row['estimation_status'],'pending_reestimation')
                    self.assertEqual(row['build_eur_ht'],0)
                    self.assertGreater(baseline['integration'],0)
                    self.assertGreater(baseline['services']['core'],0)
                    self.assertGreater(baseline['initial_months'],0)
            else:
                self.assertIsNone(row['ranges_jh'])
                self.assertIsNone(row['uncertainty_pct'])
                self.assertEqual(row['build_eur_ht'],0)

    def test_framework_defaults_follow_the_economic_sources(self):
        framework=self.study.bootstrap(essential=True)['content']['framework']
        inflation={row['key']:row for row in framework['inflation']}
        for key,row in inflation.items():
            self.assertEqual(row['value'],self.study.data['taux'][key])
            self.assertTrue(row['method'] and row['influence'])
            self.assertTrue(self.study.document_path(row['source']).is_file())
        self.assertEqual(len(framework['tariffs']),5)
        for option in framework['tariffs']:
            stack=self.study.content['stacks'][option['key']]['model']['interventions']
            for price in option['prices']:
                self.assertEqual(price['value'],stack['tarifs'][price['key']]['reference'])
                self.assertTrue(self.study.document_path(price['source']).is_file())
            self.assertEqual([price['key'] for price in option['prices']],['expert','qa','architecte'])
        support_values={self.study.content['stacks'][slug]['model']['interventions']['tarifs']['support_utilisateur']['reference']
                        for slug in self.study.options}
        self.assertEqual(support_values,{framework['support']['value']})
        self.assertEqual(framework['frontend']['value'],self.study.content['stacks']['java-spring']['model']['interventions']['tarifs']['expert']['reference'])
        calibration=self.study.content['calibration']
        deployment=read(ROOT/'source/deploiement-groupe.yaml')
        self.assertEqual(framework['pilotage']['rates'],calibration['pilotage'])
        self.assertEqual(framework['pilotage']['deployment_pct'],deployment['deploiement']['coordination_technique_pct'])
        self.assertEqual(framework['pilotage']['programme']['direction_etp'],deployment['scenarios']['central']['direction_etp'])
        self.assertEqual(framework['pilotage']['programme']['coordination_etp'],deployment['scenarios']['central']['coordination_etp'])
        programme=framework['pilotage']['programme']
        programme_cost=(programme['direction_jh']*programme['tarif_direction_eur_jh']+
                        programme['coordination_jh']*programme['tarif_coordination_eur_jh'])
        for option in self.study.baseline['options']:
            if option['mode']=='Make':
                funded=next(line['amount'] for line in option['funding_ledger'] if line['id']=='programme')
                self.assertAlmostEqual(programme_cost,funded,places=2)
        self.assertEqual(programme['direction_jh'],programme['direction_jh_par_mois']*programme['duree_mois'])
        self.assertEqual(programme['coordination_jh'],programme['coordination_jh_par_mois']*programme['duree_mois'])
        self.assertEqual(framework['pilotage']['programme']['choix'],deployment['justifications_centrales']['programme'])
        for option in framework['tariffs']:
            self.assertTrue(all(price['method'] for price in option['prices']))
            source=read(ROOT/f"source/chiffrage/chiffrage-{option['key']}.yaml")['maintenance']['activites']
            self.assertEqual([(row['id'],row['taux_pct']) for row in framework['workload']['maintenance_ia'][option['key']]],
                             [(row['activite'],row['gain_ia_pct']) for row in source])
        labels=self.study.ui['essential']['framework']['other_rows']
        self.assertEqual(set(labels),{row['key'] for row in framework['other']})
        self.assertTrue(all(row['method'] and labels[row['key']]['effect'] for row in framework['other']))
        self.assertNotIn('make',framework['workload'])
        self.assertEqual(framework['workload']['method']['metamodel_ref'],'source/fondamentaux.yaml#estimation_model')

    def test_framework_accompaniment_status_follows_executed_funding(self):
        from unittest.mock import patch
        import study_app
        original=study_app.read
        deployment_path=ROOT/'source/deploiement-groupe.yaml'
        deployment=original(deployment_path)
        baseline={row['key']:{key:value for key,value in row.items() if key!='status'}
                  for row in self.study.content['framework']['other']}
        for removed in (False,True):
            source=deepcopy(deployment)
            source['substitution']['accompagnement_retire']=removed
            with self.subTest(accompagnement_retire=removed),patch.object(
                    study_app,'read',side_effect=lambda path: deepcopy(source) if path==deployment_path else original(path)):
                rows=self.study._framework_content(self.study.content['stacks'],self.study.content['calibration'])['other']
            self.assertEqual({row['key']:{key:value for key,value in row.items() if key!='status'} for row in rows},baseline)
            for row in rows:
                expected='replaced' if row['key']=='accompagnement_make' else 'retained'
                self.assertEqual(row['status'],expected)

    def test_application_status_stays_with_results_and_has_one_source(self):
        from evaluation_status import load_status, status_notice
        essential=self.study.ui['essential']
        expected=status_notice('core')
        self.assertEqual(essential['core_method']['notice'],expected)
        self.assertNotIn('status',essential['model_workload'])
        actual=essential['application_framework']['economic']['status']
        self.assertEqual({key:actual[key] for key in expected},expected)
        self.assertEqual(actual['source'],load_status('core')['active_source'])
        self.assertEqual(essential['core_results']['status'],expected)
        gross=next(row for row in essential['model_workload']['stages'] if row['id']=='gross')
        self.assertNotEqual(gross['producer'],load_status('core')['producer'])
        self.assertEqual(load_status('core')['calibration_status'],'partially_estimated')

    def test_qualification_documents_remain_separate_from_public_economic_inputs(self):
        full=self.study.content
        compact=self.study.bootstrap(essential=True)['content']
        self.assertNotIn('core_qualification',full)
        self.assertNotIn('core_qualification',compact)
        matrix=full['market']['instruction']
        public=compact['market_method']['instruction']
        self.assertEqual(public['summary'],matrix['summary'])
        self.assertEqual(public['progress'],matrix['progress'])
        self.assertNotIn('rows',public)
        self.assertEqual(len(matrix['rows']),matrix['summary']['capabilities']*matrix['summary']['products'])

    def test_study_content_rejects_inconsistent_market_normalization(self):
        from unittest.mock import patch
        import study_app
        original=study_app.read
        market_path=ROOT/'source/references-couts-integration.yaml'
        broken=deepcopy(original(market_path))
        entry=next(row for row in broken['references'] if row['normalisation_2026']['min_eur'] is not None)
        entry['normalisation_2026']['min_eur']+=12345
        with patch.object(study_app,'read',side_effect=lambda path:deepcopy(broken) if path==market_path else original(path)):
            with self.assertRaises(AssertionError): self.study._content()

    def test_market_method_uses_the_same_six_axes_as_the_fiches(self):
        compact=self.study.bootstrap(essential=True)['content']['market_method']
        frame=self.study.content['market']['reperes_build_core']['cadre_comparaison']
        self.assertEqual(compact['axes'],[{key:axis[key] for key in ('id','titre','bc_refs','cible_flow','essai')}
                                          for axis in frame['axes']])
        self.assertEqual(len(compact['axes']),6)

    def test_public_cost_vocabulary_uses_core_system_and_annual_label(self):
        notions=self.study.glossary['notions']
        rows={row['key']:row for row in self.study.ui['composable']['rows']}
        self.assertEqual(rows['core_lifecycle']['label'],notions['core_lifecycle']['libelle'])
        self.assertEqual(rows['core_lifecycle']['annual_label'],notions['maintenance_core']['libelle'])
        self.assertEqual(next(row for row in self.study.ui['essential']['model_rows'] if row['key']=='grouped_buy')['title'],notions['grouped_buy']['libelle'])
        self.assertIn(notions['grouped_buy']['libelle'],self.study.ui['essential']['model_reading']['costs_note'])
        def strings(value):
            if isinstance(value,str): yield value
            elif isinstance(value,dict):
                for item in value.values(): yield from strings(item)
            elif isinstance(value,list):
                for item in value: yield from strings(item)
        public_text=list(strings(self.study.ui['essential']))+list(strings(self.study.ui['composable']))
        stale=re.compile(r'\bCore\b(?! System)|\bcycle (?:de vie|du Core)\b|Offres Microsoft/K3 et SAP|offres Microsoft/K3 et SAP|offre Microsoft/K3 ou SAP')
        self.assertEqual([text for text in public_text if stale.search(text)],[])

    def test_shared_caption_change_flows_to_public_views_without_economic_change(self):
        from content_model import resolve_text_tree
        from validate_stacks import read, ROOT
        glossary=deepcopy(self.study.glossary)
        glossary['notions']['maintenance_core']['libelle']='Entretien du produit générique'
        glossary['notions']['core_system']['libelle']='Noyau métier'
        glossary['notions']['programme_flow']['libelle']='Programme de transformation'
        from architecture_model import load_architecture, hydrate_architecture
        from fundamentals_model import load_fundamentals, hydrate_fundamentals
        architecture=load_architecture(glossary)
        fundamentals=load_fundamentals(glossary,architecture,self.study.data['options'])
        ui=resolve_text_tree(hydrate_fundamentals(hydrate_architecture(read(ROOT/'config/application.yaml'),architecture),fundamentals),glossary)
        self.assertEqual(ui['essential']['model_rows'][2]['title'],'Entretien du produit générique')
        self.assertEqual(ui['essential']['proofs']['core_care']['title'],'Entretien du produit générique')
        self.assertEqual(ui['composable']['rows'][0]['annual_label'],'Entretien du produit générique')
        scope=next(chapter for chapter in ui['essential']['model_reading']['chapters'] if chapter['id']=='scope')
        self.assertIn('Noyau métier',scope['lead'])
        self.assertIn('Programme de transformation',ui['essential']['model_map']['program_scope'])
        self.assertIn('Noyau métier',ui['essential']['choices'][0]['text'])
        self.assertEqual(self.study.baseline,self.study.simulate(self.study.parameters))

    def test_decision_requires_balanced_options_and_explicit_unknowns(self):
        from validate_stacks import read, ROOT
        from jsonschema import ValidationError
        decision=read(ROOT/'source/decision-make-buy.yaml')
        self.study.validate_decision(decision)
        bad=deepcopy(decision)
        del bad['criteres'][0]['options']['sap']['contrepartie']
        with self.assertRaises(ValidationError): self.study.validate_decision(bad)
        bad=deepcopy(decision);bad['mandat'][0]['valeur']=0
        with self.assertRaises(ValidationError): self.study.validate_decision(bad)
        bad=deepcopy(decision);bad['options'][1]['id']=bad['options'][0]['id']
        with self.assertRaises(ValueError): self.study.validate_decision(bad)
        bad=deepcopy(decision);bad['preuves'][0]['source']='source/absent.yaml'
        with self.assertRaises(ScenarioError): self.study.validate_decision(bad)

    def test_sponsor_bridge_preserves_documented_offer_and_reconciles(self):
        economic={o['stack']:o for o in self.study.economic['options']}
        for row in self.study.content['sponsor']['bridge']:
            e=economic[row['stack']];d=e['detail_integration']
            self.assertEqual(row['offer'],d['base_rfi'])
            self.assertAlmostEqual(row['offer']+row['conditional']+row['other'],e['synthese_eur_ht']['integration'],places=2)
            self.assertAlmostEqual(row['share'],row['conditional']/row['total'])
            self.assertEqual(row['conditional'],round(d['complements_flow']+d['prestations_estimees']+d['pilotage'],2))

    def test_calendar_example_uses_engine_without_mutating_reference(self):
        before=deepcopy(self.study.parameters)
        c=self.study.content['sponsor']['calendar']
        self.assertIsNotNone(c)
        changed=deepcopy(before);changed['options'][c['stack']]['build_mois']=c['months_after']
        option=next(o for o in self.study.simulate(changed)['options'] if o['stack']==c['stack'])
        self.assertEqual(c['after'],option['horizons'][-1])
        self.assertLess(c['after']['service_years'],c['before']['service_years'])
        self.assertLess(c['after']['totals']['total'],c['before']['totals']['total'])
        self.assertEqual(self.study.parameters,before)

    def test_baseline_matches_existing_engine_at_ten_years(self):
        expected=project(self.study.data,10)
        for a,b in zip(self.study.baseline['options'],expected['options']):
            self.assertEqual(a['horizons'][-1]['totals'],b['totaux_eur_ht'])
            self.assertEqual(a['annual'][:10],b['annees'])

    def test_projection_reaches_fifteen_years_without_changing_comparison_buttons(self):
        projected=project(self.study.data)
        self.assertEqual(self.study.ui['horizons'],[3,5,7,10])
        for option,source in zip(self.study.baseline['options'],projected['options']):
            self.assertEqual([row['annee'] for row in option['annual']],list(range(1,16)))
            self.assertEqual(option['annual'],source['annees'])
            self.assertEqual(round(sum(row['total'] for row in option['annual']),2),source['totaux_eur_ht']['total'])
            self.assertGreater(option['annual'][-1]['mco_run'],0)

    def test_all_horizons_and_remaining_are_reconciled(self):
        for option in self.study.baseline['options']:
            self.assertEqual([y['annee'] for y in option['annual']],list(range(1,16)))
            for year in option['annual']:
                self.assertAlmostEqual(year['total'],sum(year[k] for k in ('build','integration','mco_run')),places=1)
            self.assertEqual([h['years'] for h in option['horizons']],[3,5,7,10])
            for h in option['horizons']:
                paid=sum(phase_expense(r['amount'],r['start'],r['end']-r['start'],0,h['years']*12) for r in option['funding_ledger'])
                self.assertAlmostEqual(h['remaining']+paid,sum(r['amount'] for r in option['funding_ledger']),places=2)
                self.assertAlmostEqual(sum(h['responsibilities'].values()),h['totals']['total'],places=2)
                for phase in ('build','integration','mco_run','total'):
                    self.assertEqual(h['totals'][phase],round(sum(y[phase] for y in option['annual'][:h['years']]),2))

    def test_short_horizons_do_not_imply_delivered_make(self):
        for o in self.study.baseline['options'][:3]:
            self.assertEqual(o['horizons'][0]['service_years'],0)
            self.assertEqual(o['horizons'][1]['service_years'],0)
            self.assertAlmostEqual(o['horizons'][2]['service_years'],6/12)
            self.assertGreater(o['horizons'][0]['remaining'],0)

    def test_bonus_changes_sap_counterpoint_only(self):
        self.p['common']['bonus_continuite_pct']=0
        result=self.study.simulate(self.p)
        self.assertNotEqual(result['anchor'],self.study.baseline['anchor'])
        self.assertEqual(result['options'],self.study.baseline['options'])

    def test_sap_budget_propagates_to_make_anchor(self):
        self.p['options']['sap']['integration']+=100_000
        result=self.study.simulate(self.p)
        self.assertEqual(result['options'][0],self.study.baseline['options'][0])
        self.assertAlmostEqual(result['anchor']['budget_apres_bonus_eur_ht']-self.study.baseline['anchor']['budget_apres_bonus_eur_ht'],90000)
        self.assertEqual(result['options'][3],self.study.baseline['options'][3])

    def test_sap_budget_below_counterpoint_exclusions_keeps_all_options_calculable(self):
        exclusions=self.study.data['sensibilite_finance_sap']
        threshold=exclusions['retrait_indicatif_eur_ht']+exclusions['complements_generiques_exclus_ancre_make_eur_ht']
        original=deepcopy(self.study.baseline)
        for budget in (0,1_000_000,round(threshold-.01,2),threshold):
            with self.subTest(budget=budget):
                p=deepcopy(self.p);p['options']['sap']['integration']=budget
                result=self.study.simulate(p)
                self.assertEqual(result['parameters'],p)
                self.assertEqual(len(result['options']),5)
                self.assertEqual(result['options'][:4],original['options'][:4])
                self.assertEqual(result['options'][4]['integration'],budget)
                expected=None if budget<threshold else 0
                for key in ('ancre_avant_bonus_eur_ht','reduction_eur_ht','budget_apres_bonus_eur_ht'):
                    self.assertEqual(result['anchor'][key],expected)
                self.assertTrue(all(h['totals']['total']>=0 for o in result['options'] for h in o['horizons']))
        self.assertEqual(self.study.baseline,original)

    def test_buy_duration_does_not_change_autonomous_make(self):
        self.p['options']['microsoft']['integration_mois']=42
        result=self.study.simulate(self.p)
        self.assertEqual(result['make_integration_months'],30)
        for actual,reference in zip(result['options'][:3],self.study.baseline['options'][:3]):
            self.assertEqual(actual,reference)
        self.assertNotEqual(result['options'][3]['annual'],self.study.baseline['options'][3]['annual'])

    def test_documented_editor_prices_are_not_indexed_twice(self):
        self.p['common']['inflation_licences']=.15
        result=self.study.simulate(self.p)
        for a,b in zip(result['options'],self.study.baseline['options']): self.assertEqual(a['editor_prices'],b['editor_prices'])
        self.assertEqual(result['options'][3]['annual'][0]['mco_run'],self.study.baseline['options'][3]['annual'][0]['mco_run'])

    def test_service_change_does_not_affect_unserved_horizons(self):
        self.p['options']['java-spring']['services_core']+=100_000
        a=self.study.simulate(self.p)['options'][0];b=self.study.baseline['options'][0]
        self.assertEqual(a['horizons'][0]['totals'],b['horizons'][0]['totals']);self.assertGreater(a['horizons'][0]['remaining'],b['horizons'][0]['remaining']);self.assertGreater(a['horizons'][-1]['totals']['mco_run'],b['horizons'][-1]['totals']['mco_run'])

    def test_no_scenario_mutates_reference(self):
        before=json.dumps(self.study.data,sort_keys=True)
        self.p['options']['java-spring']['build']+=100000
        self.study.simulate(self.p)
        self.assertEqual(before,json.dumps(self.study.data,sort_keys=True))
        self.assertNotEqual(self.study.parameters,self.p)

    def test_invalid_inputs(self):
        for value in (math.nan,math.inf,-1,True,'10',None,51):
            with self.subTest(value=value):
                p=deepcopy(self.p);p['common']['bonus_continuite_pct']=value
                with self.assertRaises(ScenarioError):self.study.simulate(p)
        p=deepcopy(self.p);p['options']['java-spring']['editor_prices']=0
        with self.assertRaises(ScenarioError):self.study.simulate(p)
        with self.assertRaises(ScenarioError):self.study.simulate(self.p,'other-version')

    def test_document_allowlist(self):
        for value in ('../AGENTS.md','source/../../AGENTS.md','.git/config','tools/serve_study_app.py'):
            with self.subTest(value=value):
                with self.assertRaises(ScenarioError):self.study.document_path(value)
        self.assertTrue(self.study.document_path('source/faq-sponsors.md').is_file())



if __name__=='__main__':unittest.main(verbosity=2)
