"""Build candidate scope, without adopting or modifying the economic model."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'tools'),str(ROOT/'tmp/model-deps')]
import yaml
from estimation_calculation import formula,rounded
from retained_core import value_units
from model_context import model_session

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def build():
    audit=load(ROOT/'audits/2026-11-02-revue-perimetre-scenarios/results.json')
    oldpolicy=load(ROOT/'audits/2026-11-02-audit-politiques-allocation/results.json')
    units=[]
    for f in sorted(OUT.glob('scope-*.json')):
        u=load(f);u['basis_path']='audits/2026-10-30-chiffrage-complet/iteration-07/cosmic-'+u['basis']+'.json'
        if u['basis']=='controls':
            inherited=[]
            for p in oldpolicy['processes']:
                row=dict(p);row['id']='policy-'+p['id'];row['capabilities']=['BC-008'];row['scenario_refs']=['seasonal-order-backlog','redistribute-protected-stock'];row['trigger']=p['label']+' sur commande explicite.'
                row['scope_reason']=row['scope_reason'].replace('Les compteurs de consommation et réservations restent dans Stock.','Les réservations individuelles restent dans Stock. Les compteurs collectifs sont financés ici.')
                inherited.append(row)
            u['processes']=inherited+u['processes']
        basis=load(ROOT/u['basis_path']);u['benchmark']={k:basis[k] for k in ('hours_per_CFP','factor','day_hours')}
        u['baseline_CFP']=basis['CFP'];u['removed_process_ids']=[p['id'] for p in basis['processes']];u['kept_process_ids']=[]
        u['CFP']=sum(len(p[k]) for p in u['processes'] for k in ('E','R','W','X'))
        u['raw_jh']=formula('cosmic_effort',CFP=u['CFP'],**u['benchmark']);u['rounding_jh']=10;u['proposal_jh']=rounded(u['raw_jh'],10)
        assert len({p['id'] for p in u['processes']})==len(u['processes'])
        for p in u['processes']:
            assert set(p['scenario_refs'])<={s['id'] for s in audit['scenarios']}
            assert p['E'] and (p['X'] or p['W'])
            for k in ('E','R','W','X'):assert len(set(p[k]))==len(p[k])
        units.append(u)
    source=yaml.safe_load((ROOT/'source/estimations-core-retenues.yaml').read_text(encoding='utf-8'));active={u['id']:u for u in source['units']}
    inputs=['source/estimations-core-retenues.yaml','source/calibration-couts.yaml','audits/2026-11-02-revue-perimetre-scenarios/results.json','audits/2026-11-02-audit-politiques-allocation/results.json','audits/2026-11-02-proposition-perimetre-complete/closure.json']
    inputs += [str(f.relative_to(ROOT)).replace('\\','/') for f in OUT.glob('scope-*.json')]
    inputs += [u['basis_path'] for u in units]
    inputs += [str(Path(__file__).relative_to(ROOT)).replace('\\','/')]
    fingerprints={p:sha(ROOT/p) for p in inputs}
    for u in units:
        u.update(recipe='scenario_scope_revision_v1',status='proposal_not_adopted',baseline_jh=active[u['id']]['total_jh'],unit_id=u['id'],inputs_sha256=fingerprints)
        u['delta_jh']=u['proposal_jh']-u['baseline_jh'];u['supersedes_policy_revision']=u['basis']=='controls'
        save(OUT/(u['id']+'.json'),u)
    changed={u['id']:u for u in units};summary=[]
    for u in source['units']:
        v=changed.get(u['id']);summary.append(dict(id=u['id'],label=u['label'],baseline_jh=u['total_jh'],proposal_jh=v['proposal_jh'] if v else u['total_jh'],CFP=v['CFP'] if v else None,decision='scope_recount' if v else 'retained_with_bounded_scope'))
    save(OUT/'summary.json',dict(status='proposal_not_adopted',units=summary,baseline_jh=sum(u['baseline_jh'] for u in summary),proposal_jh=sum(u['proposal_jh'] for u in summary),assumptions='20 h/CFP, 7 h/JH. Comptage prévisionnel des fonctions. Les montants ne sont pas des devis ni un rendement observé. Pas de marge générale.',inputs_sha256=fingerprints))
    from gross_evaluations import project_unit_revision
    from validate_stacks import read
    with model_session():
        tooling=read(ROOT/'source/calibration-couts.yaml')['couts_communs']['outillage_realisation_eur_par_jh']
        valued={u['id']:u for u in value_units('java-spring',[],tooling)}
        for row in summary:
            row['baseline_cost_eur_ht']=valued[row['id']]['cost_eur_ht']
            row['proposal_cost_eur_ht']=project_unit_revision(changed[row['id']],valued[row['id']])['cost_eur_ht'] if row['id'] in changed else row['baseline_cost_eur_ht']
    total=sum(u['proposal_jh'] for u in summary);cost=sum(u['proposal_cost_eur_ht'] for u in summary)
    sensitivities={str(h):sum(rounded(formula('cosmic_effort',CFP=u['CFP'],hours_per_CFP=h,factor=1,day_hours=7),10) for u in units)+sum(u['baseline_jh'] for u in summary if u['id'] not in changed) for h in (15,20,25)}
    save(OUT/'summary.json',dict(status='proposal_not_adopted',units=summary,baseline_jh=sum(u['baseline_jh'] for u in summary),proposal_jh=total,
        baseline_cost_eur_ht=sum(u['baseline_cost_eur_ht'] for u in summary),proposal_cost_eur_ht=cost,sensitivity_total_jh=sensitivities,
        benchmark=dict(hours_per_CFP=20,day_hours=7,factor=1),process_count=sum(len(u['processes']) for u in units),inputs_sha256=fingerprints))
    closure=load(OUT/'closure.json')
    lines=['# Proposition de charge après revue des scénarios','',
        f'**Proposition de construction : {total:,} JH et {cost:,.0f} euros HT**, contre 5 950 JH et 3 749 300 euros HT adoptés. Le complément proposé est de 1 080 JH et 679 890 euros HT. Les simulations et les budgets continuent à utiliser les décisions adoptées.','',
        'Cinq lots sont remplacés sur leur périmètre entier. Les anciens processus sont retirés avant le nouveau comptage. Les six autres montants sont conservés sous les bornes fonctionnelles précisées ci-dessous. La proposition à 610 JH pour politiques, éligibilité et devenir remplace celle à 430 JH. Aucun des deux montants ne s’ajoute aux 50 JH adoptés.','',
        '## Charges proposées','',
        '| Lot | JH adoptés | JH proposés | Euros HT proposés |','| --- | ---: | ---: | ---: |']
    for row in summary:lines.append(f"| {row['label']} | {row['baseline_jh']} | {row['proposal_jh']} | {row['proposal_cost_eur_ht']:.0f} |")
    lines+=['','Les coûts utilisent les mêmes proportions de rôles, tarifs et outillage que le lot actuel, avec une répartition entière des nouveaux JH. Ils incluent les activités projet déjà retenues, pas seulement le développement. Aucun directeur de programme ni Office FLOW supplémentaire n’est ajouté ici.','',
        '## Pourquoi le chiffrage change','',
        'Le comptage prévisionnel distingue 123 demandes et résultats métier dans les cinq lots. COSMIC compte chaque groupe de données une fois par type de mouvement et par processus. Une marque, une société, un prestataire ou un type de traitement ne multiplie pas un même service. Le périmètre détaillé remplace les 69 anciens processus de ces lots. Les étapes internes d’un algorithme ne sont pas déclarées comme des commandes externes supplémentaires.','',
        'La formule reste **CFP × 20 h/CFP ÷ 7 h/JH**, puis arrondi à la dizaine de JH par lot. Les 20 h/CFP sont la référence historique de l’étude, non une productivité observée sur FLOW. Ce sont des besoins prévisionnels proposés, non une mesure COSMIC certifiée. Les algorithmes, l’ergonomie et les garanties de performance ne se dimensionnent pas par leurs seuls échanges de données.','',
        'Les anciens COCOMO et les quatre colonnes OSS restent les preuves du périmètre antérieur. Les petits analogues de règle, réservation, qualité ou calendrier ne couvrent pas le périmètre complet révisé. Leur moyenne ne justifierait pas le nouveau montant. Faute de panier de code équivalent établi, la proposition retient le comptage fonctionnel explicite pour ces cinq lots et conserve les hypothèses COCOMO des six autres. Il ne s’agit pas d’une nouvelle estimation COCOMO intégrée du Core.','',
        '## Fonctions comptées par lot','']
    for u in units:
        lines+=['### '+active[u['id']]['label'],'',u['assessment'],'',f"{u['baseline_CFP']} → **{u['CFP']} CFP**, soit **{u['proposal_jh']} JH** proposés.",'','| Fonction sur demande ou événement explicite | Capacités | CFP |','| --- | --- | ---: |']
        for row in u['processes']:lines.append('| '+row['label']+' | '+', '.join(row['capabilities'])+' | '+str(sum(len(row[k]) for k in ('E','R','W','X')))+' |')
        lines+=['']
    lines+=['## Financements et bornes des six autres lots','']
    for id,text in closure['retained_unit_bounds'].items():lines+=['### '+active[id]['label'],'',text,'']
    lines+=['## Traitement des quatorze écarts','',
       '| Écart | Traitement dans la proposition |','| --- | --- |']
    for f in closure['findings']:lines.append('| '+f['id']+' '+f['title']+' | '+', '.join(f['unit_refs'])+' |')
    lines+=['','Les critères d’acceptation du précédent audit restent à vérifier sur les livraisons. Leur rattachement et le choix de financement sont explicités dans [closure.json](closure.json). Pour les ateliers et les garanties communes, conserver un montant sous ces hypothèses ne démontre pas encore qu’il suffira.','',
       '## Sensibilité et travail restant','',
       'À périmètre constant, modifier uniquement le rendement des cinq lots recomptés donne '+', '.join(h+' h/CFP : '+str(v)+' JH pour le Core' for h,v in sensitivities.items())+'. Il ne s’agit pas d’un intervalle de confiance.','']
    lines+=['- '+v for v in closure['remaining_inputs']]
    lines+=['','La construction des outils de configuration et des contrats génériques est dans le Core. Le paramétrage des politiques réelles, les interfaces et les adaptations propres aux sociétés du Groupe restent dans l’intégration. Les fonctionnalités des produits Microsoft et SAP et leur inclusion contractuelle doivent être examinées séparément. Ces JH Make ne sont pas appliqués aux deux options Buy.','',
      '## Preuves et reproduction','',
      '- [Synthèse calculée et prix](summary.json).',
      '- [Rattachement des écarts et bornes](closure.json).',
      '- [Script de préparation](prepare.py).',
      '- [Audit des 88 capacités et scénarios](../2026-11-02-revue-perimetre-scenarios/audit.md).','',
      'Les fichiers `scope-*.json` portent les besoins proposés. Les cinq preuves par unité conservent les échanges E/R/W/X, les processus remplacés et les empreintes des entrées. Reproduction : `python audits/2026-11-02-proposition-perimetre-complete/prepare.py`. La projection de la page recompte les mêmes mouvements, contrôle la base et valorise avec les prix courants, sans adopter la proposition.','']
    (OUT/'audit.md').write_text('\n'.join(lines).replace('7,030','7 030'),encoding='utf-8')
    print(json.dumps(dict(jh=total,cost_eur_ht=cost,sensitivity=sensitivities),ensure_ascii=False))

if __name__=='__main__':build()
