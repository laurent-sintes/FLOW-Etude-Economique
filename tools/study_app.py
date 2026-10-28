"""Read-only study adapter and scenario evaluation using the existing economic engine."""
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
from jsonschema import Draft202012Validator

from calculate_costs import valuation
from content_model import resolve_text_tree, validate_glossary_literals
from project_investment import prepare, project, core_service_costs, phase_expense
from validate_stacks import ROOT, read
from business_calibration import active_doc, validate as validate_business_calibration
from buy_qualification import validate as validate_buy, integration_paths, coverage_sources
from business_map import build as build_business_map
from sponsor_reading import build as build_sponsor_reading
from composable_costs import RESPONSIBILITIES
from model_context import scoped_model, model_memo, CURRENT
from study_snapshot import pack_content, unpack_content
from market_oss import enrich_market_products
from analyze_cost_references import validate_market_references
from evaluation_status import status_notice
from core_qualification import validate as validate_core_qualification, summarize as summarize_core_qualification
from market_instruction import build_market_instruction
from core_method import hydrate_core_method, hydrate_market_method, hydrate_net_method, hydrate_run_method, hydrate_levers_method
from architecture_model import load_architecture, hydrate_architecture, validate_economic_links, SOURCE as ARCHITECTURE_SOURCE
from fundamentals_model import load_fundamentals, hydrate_fundamentals, SOURCE as FUNDAMENTALS_SOURCE
from framework_vision import hydrate_framework_vision
from framework_parameters import hydrate_framework_parameters
from application_framework import hydrate_application_framework
from economic_reading import build_economic_evaluations


class ScenarioError(ValueError):
    def __init__(self, code, field=None):
        self.code, self.field = code, field
        super().__init__(code)


class Study:
    @scoped_model
    def __init__(self):
        self.economic = valuation()
        self.data = prepare(self.economic)
        self.glossary = self.data['glossaire']
        architecture = load_architecture(self.glossary)
        self.architecture = resolve_text_tree(architecture, self.glossary, path=ARCHITECTURE_SOURCE)
        fundamentals = load_fundamentals(self.glossary, architecture, self.data['options'])
        self.fundamentals = resolve_text_tree(fundamentals, self.glossary, path=FUNDAMENTALS_SOURCE)
        raw_ui=hydrate_fundamentals(hydrate_architecture(hydrate_market_method(hydrate_core_method(read(ROOT/'config/application.yaml'))), architecture), fundamentals)
        raw_ui=hydrate_levers_method(hydrate_run_method(hydrate_net_method(raw_ui)))
        raw_ui=hydrate_application_framework(raw_ui)
        raw_ui=hydrate_framework_vision(raw_ui, self.glossary)
        raw_ui['essential']['core_results']['status'] = status_notice(raw_ui['essential']['core_results'].pop('status_ref'))
        validate_glossary_literals(raw_ui,self.glossary,path='config/application.yaml')
        self.ui = resolve_text_tree(raw_ui, self.glossary, path='config/application.yaml')
        from model_inputs import buy_selection_inputs
        self.ui['buy_selection_migration']['preparation_eur']=buy_selection_inputs()['preparation_reaffectee_eur']
        self.validate_ui(self.ui)
        if any(t['id'] not in self.glossary['notions'] or not t['matches'] for t in self.ui['glossary_links']['terms']):
            raise ValueError('ERR_GLOSSARY_LINK')
        self.horizons = self.ui['horizons']
        assert self.horizons == sorted(set(self.horizons))
        assert all(isinstance(h, int) and 0 < h <= self.data['scenario']['horizon_ans'] for h in self.horizons)
        self.options = {o['stack']: o for o in self.data['options']}
        self.parameters = self._defaults()
        self.files = self._files()
        # Model identity follows calculation inputs, not an unrelated Markdown edit.
        self.version = hashlib.sha256(json.dumps({k:self.data[k] for k in ('options','taux','scenario')},sort_keys=True).encode()).hexdigest()
        self.baseline = self.simulate(self.parameters)
        validate_economic_links(architecture, self.baseline)
        self.release_documents = None
        self.content = self._content()
        self.edition = dict(mode='current',date=self.data['scenario']['date'])
        self.source_digests = {str(p):h for p,h in CURRENT.get().digests.items()}

    @classmethod
    def from_release(cls, bundle):
        from study_snapshot import validate_bundle, engine_revision
        payload=validate_bundle(bundle)['payload']
        if payload['engine_revision']!=engine_revision():
            raise ValueError('Engine changed: validate and publish the draft before serving this release')
        self=cls.__new__(cls)
        for key in ('data','economic','ui','baseline','parameters','version','architecture','fundamentals'):
            setattr(self,key,deepcopy(payload[key]))
        self.glossary=self.data['glossaire'];self.horizons=self.ui['horizons']
        self.options={o['stack']:o for o in self.data['options']}
        self.content=unpack_content(payload['content'])
        self.files=set(payload['documents']);self.release_documents=payload['documents']
        self.edition=dict(mode='release',date=bundle['created_at'],id=bundle['sha256'][:12])
        if self.simulation_contract()!=payload['simulation_contract']:
            raise ValueError('Incompatible release parameter schema')
        return self

    @staticmethod
    def validate_ui(ui):
        # Catch malformed inline YAML prose (notably unquoted commas) before serving.
        groups = [(ui['nav'], {'id','label','icon'}),
                  (ui['documents'], {'path','title','description'})]
        common = {'key','label','unit','min','max','step','scale','help','source'}
        groups += [(ui['parameters']['common'], common),
                   (ui['parameters']['option'], common | {'modes'})]
        for rows, keys in groups:
            for row in rows:
                if not isinstance(row, dict) or set(row) != keys or any(v is None for v in row.values()):
                    raise ValueError(f'Invalid application metadata: {row}')

    def _files(self):
        manifest=read(ROOT/'config/publication.yaml')
        assert manifest['version']==1
        paths=manifest['documents']
        assert all(isinstance(p,str) for p in paths) and len(paths)==len(set(paths))
        files=set(paths)|set(self.data['empreintes'])
        for path in files:
            file=(ROOT/path).resolve()
            assert file.is_relative_to(ROOT.resolve()) and file.is_file(), ('Missing publication document',path)
        return files

    def _defaults(self):
        result = {'common': {'bonus_continuite_pct': self.data['bonus_continuite_make']['taux_pct'],
            'inflation_tjm': self.data['taux']['tjm_ingenierie'], 'inflation_cloud': self.data['taux']['cloud'],
            'inflation_licences': self.data['taux']['licences_logiciels']}, 'options': {}}
        for slug, o in self.options.items():
            a = {k: o['base_annuelle'][k] for k in ('hebergement','ipaas','licences_complementaires')}
            if o['mode'] == 'Make':
                a.update(build=o['build'], build_mois=o['build_mois'], services_core=o['ventilation_services']['core'],
                         services_integration=o['ventilation_services']['integration'])
            else:
                a.update(integration=o['integration'], integration_mois=o['integration_mois'],
                         services_grouped=o['base_annuelle']['services_mco'])
            result['options'][slug] = a
        return result

    def validate(self, parameters):
        if not isinstance(parameters, dict) or set(parameters) != {'common','options'}:
            raise ScenarioError('unknown_parameter')
        if not isinstance(parameters['options'], dict) or set(parameters['options']) != set(self.options):
            raise ScenarioError('unknown_parameter')
        def group(actual, specs, prefix):
            if not isinstance(actual, dict) or set(actual) != {s['key'] for s in specs}:
                raise ScenarioError('unknown_parameter', prefix)
            for spec in specs:
                v = actual[spec['key']]
                if isinstance(v, bool) or not isinstance(v, (float,int)) or not math.isfinite(v) or not spec['min']*spec['scale'] <= v <= spec['max']*spec['scale']:
                    raise ScenarioError('invalid_number', prefix+'.'+spec['key'])
        group(parameters['common'], self.ui['parameters']['common'], 'common')
        for slug, o in self.options.items():
            group(parameters['options'][slug], [s for s in self.ui['parameters']['option'] if o['mode'] in s['modes']], 'options.'+slug)

    def simulate(self, parameters, version=None):
        if version is not None and version != self.version: raise ScenarioError('version')
        self.validate(parameters)
        d = deepcopy(self.data)
        common = parameters['common']
        d['taux'] = dict(tjm_ingenierie=common['inflation_tjm'], cloud=common['inflation_cloud'], licences_logiciels=common['inflation_licences'])
        duration = next(o['integration_mois'] for o in d['options'] if o['mode']=='Make')
        anchor = parameters['options']['sap']['integration']-d['sensibilite_finance_sap']['retrait_indicatif_eur_ht']-d['sensibilite_finance_sap']['complements_generiques_exclus_ancre_make_eur_ht']
        if anchor < 0: raise ScenarioError('invalid_anchor','options.sap.integration')
        integration = round(anchor*(1-common['bonus_continuite_pct']/100),2)
        d['bonus_continuite_make'] = dict(taux_pct=common['bonus_continuite_pct'],ancre_avant_bonus_eur_ht=anchor,
            reduction_eur_ht=round(anchor-integration,2),budget_apres_bonus_eur_ht=integration)
        d['scenario']['integration_make']['bonus_continuite_build_pct'] = common['bonus_continuite_pct']
        for o in d['options']:
            p = parameters['options'][o['stack']]
            if o['mode'] == 'Make':
                o.update(build=p['build'],build_mois=p['build_mois'],integration_mois=duration)
                o['ventilation_services'] = dict(core=p['services_core'],integration=p['services_integration'],groupes=0)
                o['base_annuelle']['services_mco'] = p['services_core']+p['services_integration']
            else:
                o.update(integration=p['integration'],integration_mois=p['integration_mois'])
                o['base_annuelle']['services_mco'] = p['services_grouped']
                o['ventilation_services'] = dict(core=None,integration=None,groupes=p['services_grouped'])
            for key in ('hebergement','ipaas','licences_complementaires'): o['base_annuelle'][key] = p[key]
            if o['build_mois']+o.get('selection_mois',0)+o['integration_mois'] > d['scenario']['horizon_ans']*12:
                raise ScenarioError('invalid_duration','options.'+o['stack'])
        projected = project(d)
        output = []
        for o, r in zip(d['options'], projected['options']):
            b, i = o['build_mois']+o.get('selection_mois',0), o['integration_mois']
            end = b+i
            horizons = []
            for horizon in self.horizons:
                months = horizon*12
                annual = r['annees'][:horizon]
                totals = {key:round(sum(y[key] for y in annual),2) for key in ('build','integration','mco_run','total')}
                horizons.append(dict(years=horizon,totals=totals,
                    cost_natures={key:round(sum(y['cost_natures'][key] for y in annual),2) for key in annual[0]['cost_natures']},
                    responsibilities={key:round(sum(y['responsibilities'][key] for y in annual),2) for key in RESPONSIBILITIES},
                    service_years=max(0,months-end)/12,
                    build_progress=min(months/b,1) if b else None,
                    integration_progress=max(0,min((months-b)/i,1)),
                    remaining=round(sum(max(0,line['amount']-phase_expense(line['amount'],line['start'],line['end']-line['start'],0,months)) for line in r['financements_initiaux']),2),
                    stage='stage_build' if months < b else 'stage_integration' if months < end else 'stage_service'))
            output.append(dict(stack=o['stack'],name=o['nom'],mode=o['mode'],horizons=horizons,annual=r['annees'],
                service_start_month=end,build=o['build'],integration=o['integration'],annual_base=o['base_annuelle'],
                selection_buy=o.get('selection_buy',0),selection_months=o.get('selection_mois',0),
                initial_months=b,obtention=o['build']+o.get('selection_buy',0),
                editor_prices=o['prix_abonnements'],services=o['ventilation_services'],
                funding_ledger=r['financements_initiaux'],annual_services=r['services_composables'],
                annual_responsibilities={key:round(r['services_composables'].get(key,0)+(sum(o['base_annuelle'][k] for k in ('hebergement','ipaas','licences_complementaires')) if key=='run' else 0)+(o['prix_abonnements'][0] if key=='grouped_buy' and o['prix_abonnements'] else 0),2) for key in RESPONSIBILITIES},
                initial_responsibilities={key:round(sum(line['amount'] for line in r['financements_initiaux'] if line['responsibility']==key),2) for key in RESPONSIBILITIES},
                hosting_build=round(sum(line['amount'] for line in r['financements_initiaux'] if line['id'].startswith('hebergement_build/')),2)))
        return dict(model_version=getattr(self,'version',None),parameters=deepcopy(parameters),options=output,
            anchor=d['bonus_continuite_make'],make_integration_months=duration)

    def _content(self):
        reading = resolve_text_tree(read(ROOT/'source/lecture-comparative.yaml'), self.glossary)
        complexity = self._complexity_grid()
        market = resolve_text_tree(read(ROOT/'source/references-couts-integration.yaml'), self.glossary)
        validate_market_references(market)
        market['reperes_build_core'] = enrich_market_products(
            market['reperes_build_core'], {row['id'] for row in complexity['rows']})
        market['instruction'] = build_market_instruction(market)
        economics = {o['stack']:o for o in self.economic['options']}
        stacks = {}
        for slug,o in self.options.items():
            stack = read(ROOT/f'source/stacks/{slug}.yaml')
            costs = active_doc(slug)
            rows = costs['core']
            stacks[slug] = dict(model=stack,features=rows,economic=economics[slug],pricing=costs['integration']['prix_rfi'],
                architecture=self._architecture(stack,slug,reading['architecture']))
            stacks[slug]['economic_reading']=self._annual_reading(slug,economics[slug],reading['economique'])
        content = dict(scope=resolve_text_tree(self.data['explications']['perimetre_compare'],self.glossary),
            stacks=stacks,reading=reading,calibration=read(ROOT/'source/calibration-couts.yaml'),
            market=market,
            guide=self._synvance_guide(),complexity=complexity,sponsor=self._sponsor_summary(),business=self._business_summary(),integration_paths=self._integration_paths(),buy_review=self._buy_review(),faq=self._faq())
        content['business_map'] = build_business_map(content['complexity'],content['business'],content['buy_review'],content['integration_paths'],content['scope'])
        content['journey'] = build_sponsor_reading(content,self.baseline,self.glossary,self.document_path)
        content['framework'] = self._framework_content(stacks,content['calibration'])
        content['core_qualification'] = dict(document=validate_core_qualification(), summary=summarize_core_qualification())
        content['economic_evaluations'] = build_economic_evaluations(self.baseline, content, self.glossary, self.document_path)
        return content

    def _framework_content(self, stacks, calibration):
        inflation=read(ROOT/'source/inflation.yaml')['categories']
        deployment=read(ROOT/'source/deploiement-groupe.yaml')
        maintenance_names={row['id']:row['nom'] for row in read(ROOT/'source/maintenance.yaml')['activites']}
        programme=deployment['scenarios']['central']
        days_per_month=deployment['pilotage']['jours_par_etp_mois']
        programme_jh={role:programme[role+'_etp']*days_per_month for role in ('direction','coordination')}
        specs={item['key']:item for item in self.ui['parameters']['common']}
        inflation_keys={'tjm_ingenierie':'inflation_tjm','cloud':'inflation_cloud','licences_logiciels':'inflation_licences'}
        rates=[dict(key=key,label=specs[param]['label'],value=self.parameters['common'][param],
                    influence=specs[param]['help'],method=inflation[key]['justification'],
                    limit=inflation[key]['limites'],source=specs[param]['source'])
               for key,param in inflation_keys.items()]
        tariffs=[]
        support=[]
        for slug,option in self.options.items():
            stack=stacks[slug]['model']['interventions']
            support.append(stack['tarifs']['support_utilisateur'])
            tariffs.append(dict(key=slug,name=option['nom'],mode=option['mode'],
                prices=[dict(key=key,value=value['reference'],method=value['justification'],
                             source=f'source/stacks/{slug}.yaml#interventions/tarifs/{key}')
                        for key,value in stack['tarifs'].items() if key in ('expert','qa','architecte')],
                activities={key:value['tarif'] for key,value in stack['activites'].items()},
                rule=stack['regle'],limit=stack['limites']))
        if any(item!=support[0] for item in support[1:]):
            raise ValueError('ERR_COMMON_SUPPORT_RATE')
        common=calibration['couts_communs']
        other=[dict(key='outillage_realisation',value=common['outillage_realisation_eur_par_jh'],unit='daily',
                    method=common['justification_outillage'])]
        other.extend(dict(key='cloud_'+key,value=value,unit='annual',method=common['justification_cloud'])
                     for key,value in common['cloud_make_annuel'].items())
        other.extend([dict(key='ipaas_make_microsoft',value=common['ipaas_make_microsoft_annuel'],unit='annual',
                           method=common['justification_ipaas']),
                      dict(key='ipaas_sap',value=common['ipaas_sap_annuel'],unit='annual',
                           method=common['justification_ipaas_sap']),
                      dict(key='outillage_support',value=common['outillage_support_annuel'],unit='annual',
                           method=common['justification_support'])])
        other.extend(dict(key='capacite_buy_'+slug,value=value,unit='annual',method=common['justification_capacite'])
                     for slug,value in common['capacite_buy_supplementaire_annuel'].items())
        other.extend([dict(key='power_platform',value=common['power_platform_supplementaire_annuel'],unit='annual',
                           method=common['justification_power']),
                      dict(key='accompagnement_make',value=common['accompagnement_applicatif_make_jh'],unit='jh',
                           method=common['justification_accompagnement'])])
        for row in other:
            # The composable journal replaces this legacy allowance with deployment activities.
            # Descriptive source fields cannot reintroduce it into the executed financing.
            row['status']='replaced' if row['key']=='accompagnement_make' else 'retained'
        result = dict(inflation=rates,tariffs=tariffs,
            support=dict(value=support[0]['reference'],method=support[0]['justification']),
            frontend=dict(value=stacks['java-spring']['model']['interventions']['tarifs']['expert']['reference'],
                          method=calibration['calibration']['frontend']),
            other=other,
            pilotage=dict(rates=calibration['pilotage'],
                          deployment_pct=deployment['deploiement']['coordination_technique_pct'],
                          deployment_method=deployment['deploiement']['convention'],
                          programme=dict(direction_etp=deployment['scenarios']['central']['direction_etp'],
                                         coordination_etp=deployment['scenarios']['central']['coordination_etp'],
                                         direction_jh=programme_jh['direction']*programme['duree_mois'],
                                         coordination_jh=programme_jh['coordination']*programme['duree_mois'],
                                         direction_jh_par_mois=programme_jh['direction'],
                                         coordination_jh_par_mois=programme_jh['coordination'],
                                         duree_mois=deployment['scenarios']['central']['duree_mois'],
                                         jours_par_etp_mois=deployment['pilotage']['jours_par_etp_mois'],
                                         tarif_direction_eur_jh=deployment['pilotage']['tarif_direction_eur_jh'],
                                         tarif_coordination_eur_jh=deployment['pilotage']['tarif_coordination_eur_jh'],
                                         choix=deployment['justifications_centrales']['programme'],
                                         scenario=deployment['scenarios']['central']['nature'],
                                         justification=deployment['pilotage']['justification'],
                                         distinction=deployment['pilotage']['distinct_de'])),
            workload=dict(method=read(ROOT/'source/recalibration-metier.yaml')['methode'],
                          valuation=calibration['calibration']['definition_jh'],
                          ia=calibration['ia'],
                          maintenance_ia={slug:[dict(id=row['activite'],label=maintenance_names[row['activite']],
                                                     taux_pct=row['gain_ia_pct'],traitement=row['traitement'])
                                                for row in read(ROOT/f'source/chiffrage/chiffrage-{slug}.yaml')['maintenance']['activites']]
                                          for slug in self.options}))
        return hydrate_framework_parameters(result, stacks, calibration, self.ui, self.files)

    def _faq(self):
        faq=resolve_text_tree(read(ROOT/'source/faq-sponsors.yaml'),self.glossary)
        categories=[c['id'] for c in faq['categories']]
        ids=[q['id'] for q in faq['questions']]
        if len(set(categories))!=len(categories) or len(set(ids))!=len(ids):
            raise ValueError('ERR_FAQ_ID')
        pages=set(self.ui['pages'])
        roots=dict(reference=self.baseline,exclusions=self.data['sensibilite_finance_sap'],
                   options={o['stack']:o for o in self.baseline['options']})
        for q in faq['questions']:
            if (q['category'] not in categories or not isinstance(q['title'],str) or not isinstance(q['answer'],str)
                    or not q['title'] or not q['answer'] or not q['sources']
                    or not all(isinstance(p,str) for p in q['paragraphs'])):
                raise ValueError('ERR_FAQ_CONTENT')
            for link in q.get('links',[]):
                if link['route'].split('?')[0] not in pages: raise ValueError('ERR_FAQ_ROUTE')
            for source in q['sources']: self.document_path(source['path'])
            for figure in q.get('figures',[]):
                if figure['format'] not in ('money','annual_money','percent','months'):
                    raise ValueError('ERR_FAQ_FORMAT')
                try:
                    value=roots
                    for key in figure['binding'].split('.'):
                        value=value[int(key)] if isinstance(value,list) else value[key]
                except (KeyError,IndexError,ValueError,TypeError) as error:
                    raise ValueError('ERR_FAQ_BINDING:'+figure['binding']) from error
                if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
                    raise ValueError('ERR_FAQ_NUMBER')
                figure['value']=value
        return faq

    def _buy_review(self):
        model=validate_business_calibration();d=validate_buy(model)
        grid={b['id']:b for b in self._complexity_grid()['rows']}
        d['revues']=[dict(**row,name=grid[row['bloc']]['capacite']['nom'] if row['bloc'] in grid else model['transverse']['nom'],
                        coverage=model['couvertures'][row['couverture_ref']]) for row in d['revues']]
        d['coverage_sources'] = coverage_sources(model)
        for source in d['sources'].values():
            if not source['reference'].startswith('https://'):self.document_path(source['reference'])
        return d

    def _integration_paths(self):
        import re
        d,catalog=integration_paths()
        scenarios={s['id']:s for s in catalog['scenarios']};paths={p['id']:p for p in catalog['paths']}
        caps={r['capacite']['id']:r['capacite']['nom'] for r in self._complexity_grid()['rows']}
        def plain_source(s):
            return {k:re.sub(r'\[([^]]+)\]\([^)]+\)',r'\1',v) if isinstance(v,str) else v for k,v in s.items()}
        d['scenarios']=[dict(**row,source=plain_source(scenarios[row['scenario']]),paths=[plain_source(paths[p]) for p in row['parcours']],
                            names=[caps[c] for c in row['capacites']]) for row in d['scenarios']]
        return d

    def _synvance_guide(self):
        guide=read(ROOT/'source/parcours-synvance.yaml')
        Draft202012Validator(read(ROOT/'source/schema-parcours-synvance.yaml')).validate(guide)
        pieces={p['id']:p for p in guide['pieces']}
        if len(pieces)!=len(guide['pieces']): raise ValueError('ERR_GUIDE_DUPLICATE_PIECE')
        steps={s['id'] for s in guide['etapes']}
        if len(steps)!=len(guide['etapes']): raise ValueError('ERR_GUIDE_DUPLICATE_STEP')
        for path in guide['dependances']+[p['path'] for p in pieces.values()]: self.document_path(path)
        for step in guide['etapes']:
            if not set(step['preuves'])<=pieces.keys(): raise ValueError('ERR_GUIDE_PROOF')
            if not set(step['notions'])<=self.glossary['notions'].keys(): raise ValueError('ERR_GUIDE_TERM')
        if not all(s['route'] in self.ui['pages'] for s in guide['suite']):
            raise ValueError('ERR_GUIDE_ROUTE')
        return guide

    def _business_summary(self):
        model=validate_business_calibration()
        grid=self._complexity_grid()
        indexed={b['bloc']:b for b in model['blocs']}
        economics={o['stack']:o for o in self.economic['options']}
        calculated={s:{f['feature']:f for f in e['features']} for s,e in economics.items()}
        rows=[]
        for row in grid['rows']:
            b=indexed[row['id']]
            rows.append(dict(id=row['id'],capacite_id=row['capacite_id'],name=row['capacite']['nom'],path=[h['nom'] for h in row['hierarchie']],
                scenario=b['scenario'],frontiere=b['frontiere'],reuse=b['reemploi'],review=b['hypothese'],stacks=b['stacks']))
        t=model['transverse']
        rows.append(dict(id=t['id'],capacite_id=None,name=t['nom'],path=[],scenario=t['frontiere'],frontiere=t['frontiere'],reuse=[],review=model['methode']['buy'],stacks=t['stacks']))
        for row in rows:
            row['stacks']={s:dict(**a,work=model['lots'][a['travaux_ref']],coverage=model['couvertures'][a['couverture_ref']],valuation=calculated[s][row['id']]) for s,a in row['stacks'].items()}
        return dict(rows=rows,method=model['methode'],labels=resolve_text_tree(model['lecture'],self.glossary),sources=coverage_sources(model))

    def _sponsor_summary(self):
        content=read(ROOT/'source/synthese-sponsor.yaml')
        decision=read(ROOT/'source/decision-make-buy.yaml')
        self.validate_decision(decision)
        for option in decision['options']:
            name=self.glossary
            for key in option['nom_ref'].split('.'): name=name[key]
            option['nom']=name
        bridge=[]
        for option in self.economic['options']:
            slug=option['stack']
            if self.options[slug]['mode']!='Buy': continue
            d=option['detail_integration']
            conditional=round(d['complements_flow']+d['prestations_estimees']+d['pilotage'],2)
            other=round(d['preparation']+d['support_microsoft_premiere_annee'],2)
            total=option['synthese_eur_ht']['integration']
            if abs(d['base_rfi']+conditional+other-total)>0.02: raise ValueError('ERR_SPONSOR_BRIDGE')
            bridge.append(dict(stack=slug,name=self.glossary['options'][slug]['libelle'],
                offer=d['base_rfi'],conditional=conditional,other=other,total=total,
                share=conditional/total if total else None))
        trial=deepcopy(self.parameters)
        slug=decision['test_calendrier']['option']
        trial['options'][slug]['build_mois']+=decision['test_calendrier']['prolongation_mois']
        calendar=None
        try:
            projected=self.simulate(trial)
        except ScenarioError:
            pass
        else:
            before=next(o for o in self.baseline['options'] if o['stack']==slug)
            after=next(o for o in projected['options'] if o['stack']==slug)
            calendar=dict(stack=slug,name=before['name'],months_before=self.parameters['options'][slug]['build_mois'],
                months_after=trial['options'][slug]['build_mois'],before=before['horizons'][-1],after=after['horizons'][-1])
        horizons=[]
        for years in self.horizons:
            rows=[]
            for option in self.baseline['options']:
                h=next(h for h in option['horizons'] if h['years']==years)
                rows.append(dict(stack=option['stack'],name=option['name'],mode=option['mode'],
                                 service_start_month=option['service_start_month'],
                                 total=h['totals']['total'],remaining=h['remaining'],
                                 service_years=h['service_years'],stage=h['stage']))
            reference=min((o for o in rows if o['mode']=='Make'),key=lambda o:(o['total'],o['stack']))
            comparisons=[dict(buy=o['stack'],buy_name=o['name'],delta=round(reference['total']-o['total'],2),
                              make_service_years=reference['service_years'],buy_service_years=o['service_years'])
                         for o in rows if o['mode']=='Buy']
            horizons.append(dict(years=years,rows=rows,make_reference=reference['stack'],make_name=reference['name'],comparisons=comparisons))
        return dict(**content,horizons=horizons,decision=decision,bridge=bridge,calendar=calendar)

    def validate_decision(self, decision):
        Draft202012Validator(read(ROOT/'source/schema-decision-make-buy.yaml')).validate(decision)
        for group in ('options','criteres','benefices','mandat','preuves'):
            ids=[row['id'] for row in decision[group]]
            if len(ids)!=len(set(ids)): raise ValueError('ERR_DECISION_DUPLICATE:'+group)
        for row in decision['criteres']+decision['preuves']:
            self.document_path(row['source'])
        for option in decision['options']:
            name=self.glossary
            for key in option['nom_ref'].split('.'): name=name[key]
            if not isinstance(name,str): raise ValueError('ERR_DECISION_NAME')

    @staticmethod
    @model_memo
    def _complexity_grid():
        from validate_complexity_grid import validate
        grid,snapshot,method=validate()
        nodes={n['id']:n for n in snapshot['nodes']}
        def plain(value):
            import re
            return re.sub(r'\[([^]]+)\]\([^)]+\)',r'\1',value or '')
        def node(i):
            n=nodes[i];f=n['fields']
            return dict(id=i,kind=n['kind'],nom=f['name'],definition=plain(f.get('definition')),
                        perimetre=plain(f.get('scope')),comparaisons=f.get('market_comparisons',[]))
        rows=[]
        for block in grid['blocs']:
            rows.append(dict(**block,capacite=node(block['capacite_id']),hierarchie=[node(i) for i in block['chemin'][:3]],
                             variantes=[node(i) for i in block['variantes_source']]))
        order={n['id']:i for i,n in enumerate(snapshot['nodes'])}
        rows.sort(key=lambda r:tuple(order[i] for i in r['chemin']))
        return dict(rows=rows,method=method,reprise=grid['reprise'],source=grid['dependances']['cartographie'],
                    changed_fields=len(snapshot['relecture']['champs_modifies']))

    @staticmethod
    def _architecture(stack,slug,spec):
        assigned=[]; layers=[]
        for layer in spec['layers']:
            groups=[]
            for category in layer['categories']:
                items=[dict(x,facet=False) for x in stack['elements'] if x['couche'] in category['couches']]
                assigned.extend(x['id'] for x in items)
                if layer['id']=='frontend':
                    for facet in spec['facettes_frontend'].get(slug,[]):
                        source=next(x for x in stack['elements'] if x['id']==facet['ref'])
                        items.append(dict(source,nom=facet['nom'],description=facet['description'],facet=True))
                if items: groups.append(dict(category,items=items))
            layers.append(dict(layer,groups=groups))
        if sorted(assigned)!=sorted(x['id'] for x in stack['elements']):
            raise ValueError('ERR_ARCHITECTURE_COVERAGE:'+slug)
        return layers

    @staticmethod
    def _annual_reading(slug,economic,spec):
        """Assign existing priced work to responsibilities; never prorate a bundle."""
        annual=economic['maintenance_annuelle'][0]
        pieces=annual['postes_eur_ht']
        catalog={a['id']:a for a in read(ROOT/'source/maintenance.yaml')['activites']}
        prices=read(ROOT/f'source/maintenance/maintenance-{slug}.yaml')['valorisation_annuelle']['postes']
        result={b['id']:dict(b,items=[]) for b in spec['buckets']}
        make=economic['strategie']=='make'
        core_costs=core_service_costs(slug,read(ROOT/'source/calibration-couts.yaml')) if make else {}
        def add(bucket,key,name,amount,source):
            if amount: result[bucket]['items'].append(dict(id=key,nom=name,montant=round(amount,2),source=source))
        assigned=[]
        for bucket in spec['buckets']:
            for key in bucket['pieces']:
                assigned.append(key)
                add(bucket['id'],key,spec['pieces_titres'][key],pieces[key],'source/calibration-couts.yaml' if key!='licences_rfi' else f'source/maintenance/maintenance-{slug}.yaml')
        if sorted(assigned)!=sorted(set(pieces)-{'forfaits_rfi','prestations_estimees'}):
            raise ValueError('ERR_ANNUAL_PIECES')
        estimated=0
        for row in economic['maintenance_activites']:
            bucket=spec['activites'][row['activite']]
            if row['traitement']=='estimation':
                cost=row['cout_diagnostique_eur_ht']; estimated+=cost
                name=catalog[row['activite']]['nom']
                source='source/recalibration-metier.yaml' if row['activite'] in {'MAI-003','MAI-004','MAI-006','MAI-009'} else f'source/chiffrage/chiffrage-{slug}.yaml'
                if make and row['activite']==spec['evolutions_activite']:
                    core=round(core_costs[row['activite']],2)
                    if core>cost: raise ValueError('ERR_CORE_EVOLUTIONS')
                    add(spec['evolutions_core_bucket'],row['activite']+'/core',spec['evolutions_core_titre'],core,source)
                    cost=round(cost-core,2); name=spec['evolutions_integration_titre']
                add(bucket,row['activite'],name,cost,source)
        # Preserve priced additions: Make expertise uplift or Buy FLOW maintenance.
        extra=round(pieces['prestations_estimees']-estimated,2)
        if extra < -0.02: raise ValueError('ERR_ANNUAL_ESTIMATES')
        complement=spec['complements']['make' if make else 'buy']
        add(complement['bucket'],'complements',complement['titre'],extra,f'source/chiffrage/chiffrage-{slug}.yaml' if make else 'source/recalibration-metier.yaml')
        priced=0
        for p in prices:
            if p['id'] in spec['forfaits']:
                mapped=spec['forfaits'][p['id']]; cost=p['montants_documentes_eur_ht'][0]['montant']; priced+=cost
                add(mapped['bucket'],p['id'],mapped['titre'],cost,f'source/maintenance/maintenance-{slug}.yaml')
        if abs(priced-pieces['forfaits_rfi'])>0.01: raise ValueError('ERR_ANNUAL_BUNDLES')
        for bucket in result.values(): bucket['total']=round(sum(i['montant'] for i in bucket['items']),2)
        if abs(sum(b['total'] for b in result.values())-annual['total_eur_ht'])>0.02:
            raise ValueError('ERR_ANNUAL_RECONCILIATION')
        return dict(buckets=result,total=annual['total_eur_ht'])

    def bootstrap(self, compact=False, essential=False):
        content={'complexity':self._essential_complexity(),'framework':self.content['framework'],
                 'market_method':self._essential_market_method(),
                 'core_evaluation':self._essential_core_evaluation()} if essential else pack_content(self.content) if compact else self.content
        return dict(ui=self.ui,glossary=self.glossary,baseline=self.baseline,content=content,
                    edition=self.edition,
                    model_version=self.version,simulation_contract=self.simulation_contract(),date=self.data['scenario']['date'])

    def _essential_complexity(self):
        grid=self.content['complexity']
        return dict(axes={key:dict(titre=value['titre'],niveaux=value['niveaux']) for key,value in grid['method']['axes'].items()},
            rows=[dict(id=row['id'],capacite_id=row['capacite_id'],name=row['capacite']['nom'],
                       path=[item['nom'] for item in row['hierarchie'][1:]],complexite=row['complexite'],
                       fonctions=row['fonctions'],frontiere=row['frontiere'],
                       source='source/grille-complexite.yaml#'+row['id']) for row in grid['rows']])

    def _essential_market_method(self):
        frame=self.content['market']['reperes_build_core']['cadre_comparaison']
        return dict(introduction=frame['introduction'],
                    instruction={key:deepcopy(self.content['market']['instruction'][key])
                                 for key in ('interpretation','summary','progress','source_ref','status_labels')},
                    axes=[{key:axis[key] for key in ('id','titre','bc_refs','cible_flow','essai')}
                          for axis in frame['axes']])

    def _essential_core_evaluation(self):
        baseline={row['stack']:row for row in self.baseline['options']}
        results=[]
        for row in self.economic['options']:
            slug=row['stack']
            is_make=row['strategie']=='make'
            ranges=None
            if is_make:
                features=self.content['stacks'][slug]['features']
                ranges={case:sum(sum(feature['plages_jh'][case].values()) for feature in features)
                        for case in ('bas','central','haut')}
                assert ranges['central']==row['jh']['core_avant_ia']
            uncertainty=(dict(down=round(100*(ranges['central']-ranges['bas'])/ranges['central'],1),
                              up=round(100*(ranges['haut']-ranges['central'])/ranges['central'],1))
                         if is_make else None)
            assert abs(row['synthese_eur_ht']['build_core']-baseline[slug]['build'])<0.01
            results.append(dict(stack=slug,name=baseline[slug]['name'],mode=baseline[slug]['mode'],
                                ranges_jh=ranges,uncertainty_pct=uncertainty,
                                build_eur_ht=row['synthese_eur_ht']['build_core']))
        return results

    def simulation_contract(self):
        # Defaults and bounds may evolve; current server validation still applies.
        # Bump the explicit semantic version if a parameter changes its meaning.
        specs={group:[{key:s[key] for key in ('key','unit','scale','modes') if key in s}
                      for s in sorted(rows,key=lambda s:s['key'])]
               for group,rows in self.ui['parameters'].items()}
        contract=dict(version=self.ui['simulation_contract_version'],parameters=specs,
                      options={slug:o['mode'] for slug,o in self.options.items()})
        return hashlib.sha256(json.dumps(contract,sort_keys=True).encode()).hexdigest()

    def document_path(self, value):
        path = value.split('#')[0]
        if path not in self.files: raise ScenarioError('missing_document')
        resolved = (ROOT/path).resolve()
        frozen=self.release_documents and path in self.release_documents and 'text' in self.release_documents[path]
        if not resolved.is_relative_to(ROOT.resolve()) or (not frozen and not resolved.is_file()): raise ScenarioError('missing_document')
        return resolved

    def document_bytes(self, value):
        file=self.document_path(value); path=file.relative_to(ROOT).as_posix()
        if self.release_documents is not None:
            saved=self.release_documents[path]
            if 'text' in saved: return saved['text'].encode('utf-8')
            raw=file.read_bytes()
            if hashlib.sha256(raw).hexdigest()!=saved['sha256']:
                raise ScenarioError('changed_document')
            return raw
        return file.read_bytes()
