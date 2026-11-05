"""Independent arithmetic and traceability audit, without changing decisions."""
from decimal import Decimal, ROUND_HALF_UP
import argparse
import json
from pathlib import Path


def audit(study):
    checks = []
    def check(id, condition, detail):
        checks.append(dict(id=id, passed=bool(condition), detail=detail))
    def cents(value):
        return Decimal(str(value)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
    units = next(o for o in study.economic['options'] if o['stack']=='java-spring')['core_units']
    for unit in units:
        days = sum(Decimal(str(r['jh'])) for r in unit['roles'])
        labour = sum(Decimal(str(r['jh'])) * Decimal(str(r['rate_eur_jh'])) for r in unit['roles'])
        check('roles/'+unit['id'], days==Decimal(str(unit['total_jh'])), 'Somme indépendante des JH par rôle.')
        check('price/'+unit['id'], cents(labour+Decimal(str(unit['tooling_eur_ht'])))==cents(unit['cost_eur_ht']), 'JH par rôle × tarif, puis outillage du lot.')
    options=[]
    for option in study.baseline['options']:
        ledger=option['funding_ledger']
        check('unique-ledger/'+option['stack'], len(ledger)==len({r['id'] for r in ledger}), 'Identifiant unique par financement et séquence.')
        for row in option['annual']:
            year=row['annee']
            total=cents(row['total'])
            check(f'annual/{option["stack"]}/{year}',
                  cents(sum(Decimal(str(row[k])) for k in ('build','integration','mco_run')))==total and
                  cents(sum(Decimal(str(v)) for v in row['cost_natures'].values()))==total and
                  cents(sum(Decimal(str(v)) for v in row['responsibilities'].values()))==total,
                  'Annuité rapprochée indépendamment par agrégats, natures et responsabilités.')
        for horizon in option['horizons']:
            years=horizon['years']
            accumulated=sum(Decimal(str(r['total'])) for r in option['annual'] if r['annee']<=years)
            check(f'horizon/{option["stack"]}/{years}', cents(accumulated)==cents(horizon['totals']['total']), 'Cumul indépendant des annuités de la fenêtre.')
        options.append(dict(stack=option['stack'],ledger_rows=len(ledger),years=len(option['annual']),horizons=[h['years'] for h in option['horizons']]))
    org=study.content['delivery_organisation'];phases=[]
    for phase in org['reading']['phases']:
        allocations=[b for b in phase['buckets'] if b['team_ref'] not in (None,'governance')]
        unallocated=next(b for b in phase['buckets'] if b['team_ref'] is None)
        governance=next(b for b in phase['buckets'] if b['team_ref']=='governance')
        for field in ('jh','cost_eur_ht'):
            values=[Decimal(str(b[field])) for b in phase['buckets'] if b[field] is not None]
            expected=phase['totals'][field]
            check('partition/'+phase['id']+'/'+field,not values if expected is None else abs(sum(values)-Decimal(str(expected)))<=Decimal('.00000001'), 'Équipes + gouvernance + reliquat. Une charge exclue reste non évaluée.')
        phases.append(dict(id=phase['id'],total=phase['totals'],assigned={k:(float(sum(Decimal(str(b[k])) for b in allocations if b[k] is not None)) if any(b[k] is not None for b in allocations) else None) for k in ('jh','cost_eur_ht')},governance={k:governance[k] for k in ('jh','cost_eur_ht')},unallocated={k:unallocated[k] for k in ('jh','cost_eur_ht')}))
    pieces=org['work_catalog']['allocations']
    for record in org['reading']['records']:
        parts=[p for p in pieces if p['record_ref']==record['id']]
        for field in ('jh','cost_eur_ht'):
            values=[Decimal(str(p[field])) for p in parts if p[field] is not None]
            expected=record[field]
            check('contribution-source/'+record['id']+'/'+field, not values if expected is None else bool(values) and abs(sum(values)-Decimal(str(expected)))<=Decimal('.00000001'), 'Somme indépendante des contributions et du reliquat par mesure source.')
        for role in record['roles']:
            allocated=[r for p in parts for r in p['roles'] if r['id']==role['id']]
            check('contribution-role/'+record['id']+'/'+role['id'],abs(sum(Decimal(str(r['jh'])) for r in allocated)-Decimal(str(role['jh'])))<=Decimal('.00000001') and all(r.get('rate_eur_jh')==role.get('rate_eur_jh') for r in allocated), 'Conservation indépendante des JH et du tarif de chaque rôle.')
    for cell in org['allocation_table']['rows']:
        actor='governance' if cell['owner_kind']=='governance' else cell['team_ref']
        cell_parts=[p for p in pieces if p['phase']==cell['phase_ref'] and p['team_ref']==actor]
        for field in ('jh','cost_eur_ht'):
            values=[p[field] for p in cell_parts if p[field] is not None]
            expected=sum(Decimal(str(v)) for v in values) if values else None
            actual=cell[field]
            check('allocation/'+cell['id']+'/'+field,
                  (actual is None and expected is None) or (actual is not None and expected is not None and abs(Decimal(str(actual))-expected)<=Decimal('.00000001')),
                  'Cellule de ventilation rapprochée de ses travaux et financements sources.')
    for row in org['reading']['records']:
        if row['roles']:
            check('record-roles/'+row['id'],abs(sum(Decimal(str(r['jh'])) for r in row['roles'])-Decimal(str(row['jh'])))<=Decimal('.00000001'), 'Conservation de la charge du travail par ses rôles.')
    return dict(status='passed' if all(c['passed'] for c in checks) else 'failed',model_revision=study.model_revision,
                checks=checks,options=options,core_jh=sum(u['total_jh'] for u in units),phases=phases,
                meaning='Contrôles arithmétiques et structurels. Les hypothèses de périmètre, de productivité et de capacité demandent une qualification métier distincte.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    from study_app import Study
    report=audit(Study())
    raw=json.dumps(report,ensure_ascii=False,indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(raw,encoding='utf-8')
    print(json.dumps(dict(status=report['status'],checks=len(report['checks']),failed=[c for c in report['checks'] if not c['passed']],core_jh=report['core_jh'],phases=report['phases']),ensure_ascii=False))
    return int(report['status']!='passed')


if __name__=='__main__':
    raise SystemExit(main())
