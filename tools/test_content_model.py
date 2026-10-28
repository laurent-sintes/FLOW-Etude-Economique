"""Presentation references must resolve deterministically and fail at their source."""
import unittest

from content_model import resolve_text_tree, validate_glossary_literals


class ContentModelTests(unittest.TestCase):
    glossary={'notions':{'core_system':{'libelle':'Core System','forme_courte':'Core'},
                         'grouped_buy':{'libelle':'Droits d’usage et services associés'}},
              'vues':{'synthese':{'libelle':'Synthèse'},'se_projeter':{'libelle':'Se projeter'}}}

    def test_valid_references_and_explicit_data_variables(self):
        source={'title':'{{notion.core_system}}','body':['{{vue.synthese}}','{{notion.core_system.court}} : {{amount}}']}
        self.assertEqual(resolve_text_tree(source,self.glossary,{'amount':42},path='config/example.yaml'),
                         {'title':'Core System','body':['Synthèse','Core : 42']})

    def test_invalid_reference_reports_its_location(self):
        for reference in ('{{notion.missing}}','{{notion.core_system.definition}}',
                          '{{vue.synthese.court}}','{{amount}}','{{notion.core_system'):
            with self.subTest(reference=reference),self.assertRaisesRegex(ValueError,'config/example.yaml.title'):
                resolve_text_tree({'title':reference},self.glossary,path='config/example.yaml')

    def test_copied_caption_is_rejected_but_mode_identifier_is_allowed(self):
        with self.assertRaisesRegex(ValueError,'config/example.yaml.title'):
            validate_glossary_literals({'title':'Core System'},self.glossary,path='config/example.yaml')
        validate_glossary_literals({'parameters':{'modes':['Core System']},
                                    'glossary_links':{'matches':['Core System']}},
                                   self.glossary,path='config/example.yaml')

    def test_public_caption_in_prose_and_retired_name_are_rejected(self):
        for value in ('Le Core System est adapté.','Les Offres Microsoft/K3 et SAP sont groupées.',
                      'Voir Se projeter pour le calendrier.','iPaaS et licences techniques'):
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,'ERR_CONTENT_LITERAL:config/example.yaml.body'):
                validate_glossary_literals({'body':value},self.glossary,path='config/example.yaml')
        validate_glossary_literals({'body':'Le {{notion.core_system}} est adapté dans {{vue.se_projeter}}.'},
                                   self.glossary,path='config/example.yaml')


if __name__=='__main__': unittest.main()
