"""Frozen reading of existing economic evaluations; no new budget calculation."""
from copy import deepcopy
from decimal import Decimal

from jsonschema import Draft202012Validator

from project_investment import financing_period, phase_expense, subscription_expense
from content_model import resolve_text_tree, validate_glossary_literals
from validate_stacks import ROOT, read


SOURCE = 'source/lecture-evaluations-economiques.yaml'
ERROR = 'ERR_ECONOMIC_READING'
ANNUAL_KEYS = ('services_mco', 'hebergement', 'ipaas', 'licences_complementaires', 'offre_editeur')


def _object(fields):
    return dict(type='object', properties=fields, required=list(fields), additionalProperties=False)


TEXT = dict(type='string', minLength=1, pattern=r'\S')
LINK = _object(dict(path=TEXT, label=TEXT))
LINKS = dict(type='array', minItems=1, items=LINK)
SECTION = dict(title=TEXT, lead=TEXT, caption=TEXT, note=TEXT, sources=LINKS)
SPONSOR = _object(dict(
    **{key:TEXT for key in ('cumulative', 'comparison_note', 'completion', 'completion_note', 'completion_detail', 'initial_ledger', 'subscriptions', 'insight', 'insight_text', 'compare_parts', 'compare_parts_note', 'acquisition', 'difference', 'reference_option', 'funding_and_annual', 'annual_base', 'projected_year', 'annual_pair_note', 'budgets_detail', 'scope_title', 'scope_short', 'trajectory', 'trajectory_note', 'annual_parts', 'determinant_title', 'determinant_note', 'lots', 'users')},
    difference_labels=_object({key:TEXT for key in ('higher','lower','equal')}),
    stages=_object({key:TEXT for key in ('before_service','partial_service','full_service')}),
    drivers=_object({key:TEXT for key in ('java-spring','microsoft','sap')}),
    determinants=dict(type='array', minItems=4, maxItems=4, items=_object(dict(id=dict(enum=['calendar','core','offers','service']),title=TEXT,status=TEXT,text=TEXT))),
    scope_rows=dict(type='array', minItems=3, maxItems=3, items=_object(dict(id=dict(enum=['priced','unpriced','sap']),title=TEXT,text=TEXT,action=TEXT))),
    decision=_object(dict(title=TEXT,intro=TEXT,items=dict(type='array',minItems=3,items=TEXT),budget=TEXT,href=dict(const='#capacite-realisation?view=gates&focus=delivery-readiness-gate-dispositif'),link=TEXT)),
))
SCHEMA = _object(dict(
    sponsor=SPONSOR,
    version=dict(const=1), id=dict(const='economic-evaluations'), navigation_label=TEXT,
    intro=_object(dict(title=TEXT, text=TEXT)),
    labels=_object({key:TEXT for key in ('option', 'budget', 'duration', 'months', 'source',
                                       'price_convention', 'annual_item', 'annual_total',
                                       'not_applicable', 'annual_sources', 'choose_option', 'choose_capacity', 'nature',
                                       'jh_before', 'jh_unit', 'amount', 'period', 'month_prefix', 'total',
                                       'core_work', 'core_coordination', 'core_total', 'capacity', 'transverse')}),
    sections=_object(dict(
        core=_object(dict(title=TEXT, lead=TEXT, caption=TEXT, note=TEXT, capacity_note=TEXT,
                          links=dict(type='array', minItems=1, items=_object(dict(
                              href=dict(enum=['#parametres', '#cartographie', '#modele?section=scope', '#complexite']), label=TEXT))))),
        selection=_object(SECTION),
        integration=_object(dict(**SECTION, detail_title=TEXT, detail_note=TEXT,
            ledger_labels=_object({key:TEXT for key in ('travaux_communs','coordination_commune','deploiements',
                'coordination_deploiements','programme','MAI-005/reception','MAI-006/reception','integration_initiale')}),
            explanations=_object({key:TEXT for key in ('Make', 'microsoft', 'sap')}))),
        annual=_object(dict(**SECTION, detail_title=TEXT, detail_note=TEXT, rows=dict(type='array', minItems=5, maxItems=5,
            items=_object(dict(id=dict(enum=list(ANNUAL_KEYS)), label=TEXT, explanation=TEXT))))),
        limits=_object(dict(title=TEXT, lead=TEXT)),
    )),
    links=dict(type='array', minItems=1, items=_object(dict(href=dict(enum=['#parametres', '#se-projeter', '#comparer', '#conditions-realisation', '#capacite-realisation']), label=TEXT))),
))


def _require(condition, reason):
    if not condition:
        raise ValueError(f'{ERROR}:{reason}')


def compile_economic_evaluations(baseline, content, editorial, glossary, document_path, inputs, projection_data):
    """Compile a frozen reading using the single funding and projection engine."""
    errors = sorted(Draft202012Validator(SCHEMA).iter_errors(editorial), key=lambda error:str(error.path))
    if errors:
        error = errors[0]
        raise ValueError(f'{ERROR}:{list(error.path)}:{error.message}')
    _require([row['id'] for row in editorial['sections']['annual']['rows']] == list(ANNUAL_KEYS), 'annual row contract')
    _require(len({row['href'] for row in editorial['links']}) == len(editorial['links']), 'duplicate reading link')
    _require([row['id'] for row in editorial['sponsor']['determinants']] == ['calendar','core','offers','service'], 'sponsor determinant contract')
    _require([row['id'] for row in editorial['sponsor']['scope_rows']] == ['priced','unpriced','sap'], 'sponsor scope contract')
    validate_glossary_literals(editorial, glossary, path=SOURCE)
    text = resolve_text_tree(editorial, glossary, path=SOURCE)
    for section in text['sections'].values():
        for link in section.get('sources', []):
            document_path(link['path'])

    options = []
    capacities = {row['id']:row['capacite'] for row in content['complexity']['rows']}
    identifiers = [option['stack'] for option in baseline['options']]
    _require(len(identifiers) == len(set(identifiers)), 'duplicate option')
    _require(set(identifiers) == set(content['stacks']), 'inconsistent option coverage')
    for option in baseline['options']:
        slug, mode = option['stack'], option['mode']
        _require(mode in ('Make', 'Buy'), f'unknown mode:{slug}')
        integration_source = ('source/deploiement-groupe.yaml' if mode == 'Make'
                              else f'source/chiffrage/chiffrage-{slug}.yaml#/integration')
        annual_source = f'source/chiffrage/chiffrage-{slug}.yaml#/maintenance'
        document_path(integration_source)
        document_path(annual_source)
        selection = None
        if mode == 'Buy':
            selection = dict(budget_eur_ht=option['selection_buy'], months=option['selection_months'],
                             source='source/selection-buy.yaml')
            document_path(selection['source'])
        duration = (baseline['make_integration_months'] if mode == 'Make'
                    else baseline['parameters']['options'][slug]['integration_mois'])
        ledger = [line for line in option['funding_ledger'] if line['phase'] == 'integration']
        ledger_total = sum((Decimal(str(line['amount'])) for line in ledger), Decimal(0))
        _require(abs(ledger_total - Decimal(str(option['integration']))) < Decimal('0.005'), f'integration ownership:{slug}')

        prices = option['editor_prices']
        _require(bool(prices) == (mode == 'Buy'), f'editor price sequence:{slug}')
        annual_items = {key:deepcopy(option['annual_base'][key]) for key in ANNUAL_KEYS[:-1]}
        annual_items['offre_editeur'] = prices[0] if prices else None
        total = content['stacks'][slug]['economic_reading']['total']
        # Reconcile already calculated amounts; the published total remains the owner.
        parts_total = sum((Decimal(str(value)) for value in annual_items.values() if value is not None), Decimal(0))
        _require(abs(parts_total - Decimal(str(total))) < Decimal('0.005'), f'annual ownership:{slug}')
        core = None
        if mode == 'Make':
            stack = content['stacks'][slug]
            features=[dict(id=r['id'],name=r['capacite']['nom'],definition=r['capacite']['definition'],
                justification=r['frontiere'],charges={},amount=None) for r in content['complexity']['rows']]
            natures={}
            units = deepcopy(stack['economic']['core_units'])
            total_jh = sum(natures.values()) + sum(u['total_jh'] for u in units)
            _require(total_jh == stack['economic']['jh']['core_avant_ia'], f'core charge ownership:{slug}')
            for feature in features:
                feature['retained_unit'] = next((u['id'] for u in units if feature['id'] in {c['id'] for c in u['capabilities']}), None)
            core = dict(natures=natures, units=units, features=features, total_jh=total_jh,
                        amounts=deepcopy(stack['economic']['detail_build']), total_eur_ht=option['build'])
            _require(abs(sum(Decimal(str(value)) for value in core['amounts'].values()) -
                         Decimal(str(option['build']))) < Decimal('0.005'), f'core cost ownership:{slug}')
        detail = []
        for line in ledger:
            _require(line['id'] in text['sections']['integration']['ledger_labels'], f'integration label:{line["id"]}')
            detail.append(dict(id=line['id'], label=text['sections']['integration']['ledger_labels'][line['id']],
                               amount=line['amount'], start=line['start'], end=line['end']))
        offer_bridge = deepcopy(content['stacks'][slug]['economic']['detail_integration']) if mode == 'Buy' else None
        if offer_bridge is not None:
            _require(abs(sum(Decimal(str(value)) for value in offer_bridge.values()) -
                         Decimal(str(option['integration']))) < Decimal('0.005'), f'offer bridge ownership:{slug}')
        spending_bridge = []
        for horizon in option['horizons']:
            # The existing journal and its cent-conserving spread remain the owners.
            transition = sum((Decimal(str(phase_expense(line['amount'], line['start'],
                line['end']-line['start'], 0, horizon['years']*12)))
                for line in option['funding_ledger'] if line['phase'] == 'mco_run'), Decimal(0))
            other = Decimal(str(horizon['totals']['mco_run']))
            _require(Decimal(0) <= transition <= other, f'transition ownership:{slug}')
            spending_bridge.append(dict(years=horizon['years'], transition_eur_ht=float(transition),
                                        recurring_eur_ht=float(other-transition)))
        end = option['service_start_month']
        _require(all(line['end'] <= end for line in option['funding_ledger']), f'completion journal:{slug}')
        initial = sum((Decimal(str(line['amount'])) for line in option['funding_ledger']), Decimal(0))
        subscriptions = (subscription_expense(prices, baseline['parameters']['common']['inflation_licences'],
                         option['selection_months'], 0, end) if prices else 0)
        completion = dict(month=end, initial_eur_ht=float(initial), subscriptions_eur_ht=subscriptions,
                          total_eur_ht=float(initial+Decimal(str(subscriptions))))
        stages = [dict(year=row['annee'], stage='full_service' if (row['annee']-1)*12 >= end else
                       'before_service' if row['annee']*12 <= end else 'partial_service') for row in option['annual']]
        breakdown = deepcopy(list(content['stacks'][slug]['economic_reading']['buckets'].values()))
        _require(abs(sum(Decimal(str(group['total'])) for group in breakdown)-Decimal(str(total))) < Decimal('0.005'),
                 f'annual detail ownership:{slug}')
        options.append(dict(stack=slug, name=option['name'], mode=mode, selection=selection, core=core,
            integration=dict(budget_eur_ht=option['integration'], months=duration, source=integration_source, detail=detail, offer_bridge=offer_bridge),
            spending_bridge=spending_bridge, service_completion=completion,
            annual=dict(projected_stages=stages, items=annual_items, total_eur_ht=total, source=annual_source, breakdown=breakdown,
                        service_allocation=deepcopy(option['services']))))

    reference = next(option for option in baseline['options'] if option['stack']=='java-spring')
    for option in options:
        original = next(row for row in baseline['options'] if row['stack']==option['stack'])
        differences = []
        for horizon in original['horizons']:
            reference_total = next(h['totals']['total'] for h in reference['horizons'] if h['years']==horizon['years'])
            difference = Decimal(str(horizon['totals']['total']))-Decimal(str(reference_total))
            differences.append(dict(years=horizon['years'], difference_eur_ht=float(difference),
                amount_eur_ht=float(abs(difference)), direction='higher' if difference>0 else 'lower' if difference<0 else 'equal'))
        option['comparison'] = dict(reference='java-spring', horizons=differences)

    price_source = 'source/calibration-couts.yaml#convention/prix'
    document_path(price_source)
    return dict(model_version=baseline['model_version'], editorial=text, options=options,
                drivers=dict(perimeter=deepcopy(inputs['volumes']['perimetre']),
                             annual_volumes=deepcopy(inputs['volumes']['volumes'])),
                price_convention=dict(text=content['calibration']['convention']['prix'], source=price_source),
                periods=compile_reading_periods(baseline,projection_data))


def build_economic_evaluations(baseline, content, glossary, document_path, inputs, projection_data):
    """Compile once during Study loading; endpoints serve the frozen result only."""
    document_path(SOURCE)
    return compile_economic_evaluations(baseline, content, read(ROOT / SOURCE), glossary, document_path, inputs, projection_data)


def compile_reading_periods(baseline, projection_data):
    """1–15 years from each milestone. No repricing or restart of indexation."""
    output=[]
    originals={row['stack']:row for row in projection_data['options']}
    for option in baseline['options']:
        source=deepcopy(originals[option['stack']])
        # The adopted budgets, service parts and journal already own the amounts.
        ledger=option['funding_ledger']; parts=option['annual_services']
        anchors={'project':0,'core':option['initial_months'],'production':option['service_start_month']}
        periods=[]
        for anchor,start in anchors.items():
            annual=[]; horizons=[]
            for year in range(1,16):
                lo=start+(year-1)*12; hi=start+year*12
                row=financing_period(source,ledger,parts,projection_data['taux'],lo,hi)
                row.update(annee=year,start_month=lo,end_month=hi,
                    stage='full_service' if lo>=option['service_start_month'] else
                          'before_service' if hi<=option['service_start_month'] else 'partial_service')
                annual.append(row)
                totals={key:round(sum(r[key] for r in annual),2) for key in ('build','integration','mco_run','total')}
                transition=round(sum(phase_expense(line['amount'],line['start'],line['end']-line['start'],start,hi)
                                     for line in ledger if line['phase']=='mco_run'),2)
                remaining=round(sum(phase_expense(line['amount'],line['start'],line['end']-line['start'],hi,line['end'])
                                    for line in ledger if hi<line['end']),2)
                horizons.append(dict(years=year,start_month=start,end_month=hi,totals=totals,
                    service_years=max(0,hi-max(start,option['service_start_month']))/12,
                    remaining=remaining,transition_eur_ht=transition,
                    recurring_eur_ht=round(totals['mco_run']-transition,2),
                    stage='stage_build' if hi<option['initial_months'] else
                          'stage_integration' if hi<option['service_start_month'] else 'stage_service'))
            periods.append(dict(anchor=anchor,start_month=start,annual=annual,horizons=horizons))
        output.append(dict(stack=option['stack'],periods=periods))
    reference=next(row for row in output if row['stack']=='java-spring')
    for option in output:
        for period,ref_period in zip(option['periods'],reference['periods']):
            for horizon,ref_horizon in zip(period['horizons'],ref_period['horizons']):
                difference=round(horizon['totals']['total']-ref_horizon['totals']['total'],2)
                horizon['comparison']=dict(reference='java-spring',difference_eur_ht=difference,
                    amount_eur_ht=abs(difference),direction='higher' if difference>0 else 'lower' if difference<0 else 'equal')
    return output
