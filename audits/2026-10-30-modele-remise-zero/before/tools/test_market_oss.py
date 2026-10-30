"""Contract checks for comparable product fiches and the OSS reconstruction."""

from copy import deepcopy
import unittest

from market_oss import enrich_market_products
from validate_stacks import ROOT, read


class MarketOSSStudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = read(ROOT / 'source/references-couts-integration.yaml')['reperes_build_core']
        cls.capabilities = {item['id'] for item in read(ROOT / 'source/grille-complexite.yaml')['blocs']}

    def test_one_nominal_effort_is_derived_without_market_price(self):
        enriched = enrich_market_products(self.raw, self.capabilities)
        oss = enriched['etude_oss']
        calculation = oss['calcul_cocomo']
        source = self.raw['etude_oss']['calcul_cocomo']
        method = self.raw['etude_oss']['methode']
        components = self.raw['etude_oss']['mesure']['composants']
        selected = {
            product: components[product][variant]['pncloc']
            for product, variant in source['selections'].items()
        }
        months = sum(
            method['coefficient_a'] * (pncloc / 1000) ** method['exposant_nominal']
            for pncloc in selected.values()
        )
        self.assertEqual(calculation['pncloc_par_composant'], selected)
        self.assertEqual(calculation['pncloc_total'], sum(selected.values()))
        self.assertAlmostEqual(calculation['mois_personne'], months)
        self.assertEqual(calculation['jh'], round(months * method['heures_mois_personne'] / method['heures_jh']))
        self.assertEqual(sum(calculation['jh_par_composant'].values()), calculation['jh'])
        self.assertEqual(enriched['fiches_produit']['erpnext']['code']['pncloc'], calculation['pncloc_total'])
        self.assertEqual(enriched['fiches_produit']['erpnext']['code']['effort_jh'], calculation['jh'])
        for product in ('microsoft', 'sap'):
            self.assertIsNone(enriched['fiches_produit'][product]['code']['pncloc'])
            self.assertIsNone(enriched['fiches_produit'][product]['code']['effort_jh'])
        for product in ('odoo-community', 'tryton', 'axelor-open-suite'):
            self.assertGreater(enriched['fiches_produit'][product]['code']['pncloc'], 0)
            self.assertIsNone(enriched['fiches_produit'][product]['code']['effort_jh'])
        self.assertIsNone(oss['prix_observe_eur_ht'])
        self.assertIsNone(oss['prix_retraite_flow_eur_2026'])
        self.assertEqual(set(source), {'selections'})
        self.assertNotIn('scenarios', oss)

    def test_invalid_scope_and_price_cannot_enter_market_reading(self):
        for mutate in (
            lambda x: x['etude_oss'].update(prix_observe_eur_ht=1),
            lambda x: x['cadre_comparaison']['axes'][0]['bc_refs'].append('BC-074'),
            lambda x: x['etude_oss']['mesure']['composants']['insights']['v3'].update(pncloc=1),
            lambda x: x['etude_oss']['calcul_cocomo']['selections'].update(frappe='unknown'),
            lambda x: x['etude_oss']['calcul_cocomo'].update(complement_flow_jh=7500),
            lambda x: x['fiches_produit']['sap']['evaluations']['transactions'].update(statut_offre='couvert'),
            lambda x: x['fiches_produit']['microsoft']['code'].update(pncloc=1000),
            lambda x: x['fiches_produit']['erpnext']['code'].update(effort_jh=100),
            lambda x: x['fiches_produit']['tryton']['code'].update(effort_jh=100),
            lambda x: x['candidats_a_etudier'][0].update(id='erpnext'),
        ):
            broken = deepcopy(self.raw)
            mutate(broken)
            with self.assertRaisesRegex(ValueError, 'ERR_MARKET_OSS'):
                enrich_market_products(broken, self.capabilities)

    def test_architecture_and_comparison_keep_verifiable_evidence(self):
        enriched = enrich_market_products(self.raw, self.capabilities)
        oss = enriched['etude_oss']
        self.assertEqual({v['id'] for v in oss['mesure']['versions']},
                         {'frappe', 'erpnext', 'insights'})
        self.assertEqual(oss['mesure']['sous_ensembles']['automation_flow']['parent'], 'frappe')
        self.assertGreaterEqual(len(oss['architecture']['points_chauds']), 3)
        axis_ids = {axis['id'] for axis in enriched['cadre_comparaison']['axes']}
        self.assertGreaterEqual(len(axis_ids), 3)
        self.assertEqual(set(enriched['fiches_produit']),
                         {'erpnext', 'odoo-community', 'tryton', 'axelor-open-suite', 'microsoft', 'sap'})
        for fiche in enriched['fiches_produit'].values():
            self.assertEqual(set(fiche['evaluations']), axis_ids)
        self.assertEqual({axis['id'] for axis in oss['comparaison']['axes']}, axis_ids)
        self.assertEqual(set(oss['comparaison']['axes'][0]['produits']), set(enriched['fiches_produit']))
        broken = deepcopy(self.raw)
        broken['etude_oss']['architecture']['points_chauds'][0]['preuve_ref'] = 'sources/missing-proof.md'
        with self.assertRaisesRegex(ValueError, 'ERR_MARKET_OSS'):
            enrich_market_products(broken, self.capabilities)

    def test_deployment_references_keep_entity_scope_and_unknowns(self):
        enriched = enrich_market_products(self.raw, self.capabilities)
        fiches = enriched['fiches_produit']
        self.assertEqual({key: len(fiches[key]['references_deploiement']) for key in
                          ('erpnext', 'odoo-community', 'axelor-open-suite')},
                         {'erpnext': 2, 'odoo-community': 3, 'axelor-open-suite': 2})
        for key in ('tryton', 'microsoft', 'sap'):
            self.assertIsNone(fiches[key]['references_deploiement'])
        aurora = fiches['odoo-community']['references_deploiement'][0]
        self.assertEqual(aurora['edition_deploiement'], 'Odoo Community')
        self.assertIn('Workforce Management', aurora['limite_flow'])
        for fiche in fiches.values():
            for reference in fiche['references_deploiement'] or []:
                self.assertGreaterEqual(len(reference['preuves']), 2)
                self.assertTrue(reference['entite_equipee'])
                self.assertTrue(reference['limite_flow'])
        broken = deepcopy(self.raw)
        broken['fiches_produit']['erpnext']['references_deploiement'][0]['preuves'][0] = 'http://example.com'
        with self.assertRaisesRegex(ValueError, 'ERR_MARKET_OSS'):
            enrich_market_products(broken, self.capabilities)

    def test_singularities_compare_all_products_and_commercial_contexts(self):
        enriched = enrich_market_products(self.raw, self.capabilities)
        profiles = enriched['cadre_comparaison']['singularites']['produits']
        self.assertEqual(set(profiles), set(enriched['fiches_produit']))
        self.assertEqual({key for profile in profiles.values() for key in profile['commerce']},
                         {'retail', 'ecommerce', 'wholesale'})
        self.assertEqual(profiles['sap']['commerce']['retail']['statut'], 'partiel')
        self.assertEqual(profiles['odoo-community']['commerce']['ecommerce']['statut'], 'hors_perimetre')
        broken = deepcopy(self.raw)
        broken['cadre_comparaison']['singularites']['produits']['sap']['charge']['repere_observe'] = 0
        with self.assertRaisesRegex(ValueError, 'ERR_MARKET_OSS'):
            enrich_market_products(broken, self.capabilities)


if __name__ == '__main__':
    unittest.main()
