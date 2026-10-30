"""Compile derived volumes and validate the small current funding contracts."""
from copy import deepcopy
import math
from validate_stacks import ROOT, read
from model_context import model_memo

RESPONSIBILITIES = ('core_lifecycle','integration_client','run','mco_client','client_evolutions','grouped_buy')


def fields(value, required, optional=(), path=''):
    """Close editable input contracts before compiling their derived values."""
    assert isinstance(value,dict), ('Expected mapping',path)
    missing=set(required)-set(value);unknown=set(value)-set(required)-set(optional)
    assert not missing and not unknown, ('Funding fields',path,'missing',sorted(missing),'unknown',sorted(unknown))


def activity_refs(values, catalogue, path):
    assert isinstance(values,list) and all(isinstance(value,str) for value in values), ('Activity list',path)
    assert len(values)==len(set(values)), ('Duplicate activity',path)
    assert set(values)<=catalogue, ('Unknown activity',path,sorted(set(values)-catalogue))
    return set(values)


def validate_group_contract(group, integration):
    """Check executable Group inputs against their activity owner and current ledger."""
    fields(group, {'version','date','statut','objet','prix','perimetre','substitution','deploiement',
                   'pilotage','core','transition','scenarios','justifications_centrales','preuves',
                   'exclusions_preservees','perimetre_ref','calendrier_autonome'}, path='group')
    sections={
        'perimetre': {'domaine','poles_candidats','precision','repartition_usagers_par_unite',
                     'precision_usagers','recette','migration','formation'},
        'substitution': {'activites_retirees','activites_conservees','accompagnement_retire',
                         'preparation_retiree','justification'},
        'deploiement': {'roles_pct','origine_roles','coordination_technique_pct','convention','contenu',
                       'exclusions','limite','cartographie'},
        'pilotage': {'jours_par_etp_mois','tarif_direction_eur_jh','tarif_coordination_eur_jh',
                    'statut_tarifs','justification','distinct_de','preuve_limite'},
        'core': {'activite','debut_mois','hypothese_contractuelle','pas_de_double_compte','evolutions',
                 'services_client','taux_pilotage_ref'},
        'transition': {'nature_cout_ref','stabilisation_mois','infrastructure_annuelle_refs',
                       'infrastructure_debut_mois','infrastructure_fin','justification_infrastructure',
                       'services_partages','debut_services_partages','services_variables',
                       'debut_services_variables','limite_variables','pas_de_double_compte',
                       'evolutions_client','fin'},
    }
    for section,expected in sections.items():fields(group[section],expected,path='group/'+section)
    ids=[row['id'] for row in integration['activites']]
    assert len(ids)==len(set(ids)), 'Duplicate integration catalogue identity'
    catalogue=set(ids);substitution=group['substitution']
    retained=activity_refs(substitution['activites_conservees'],catalogue,'substitution/activites_conservees')
    removed=activity_refs(substitution['activites_retirees'],catalogue,'substitution/activites_retirees')
    assert retained.isdisjoint(removed), 'Integration activity retained and replaced'
    assert retained|removed==catalogue, ('Unclassified integration activities',sorted(catalogue-retained-removed))
    # The current Group packages replace training and go-live, not arbitrary common work.
    assert removed=={'INT-012','INT-013'}, 'Group deployment must replace INT-012 and INT-013'
    # These are descriptions of the ledger, not switches capable of restoring old budgets.
    for key in ('accompagnement_retire','preparation_retiree'):
        assert substitution[key] is True, ('Descriptive substitution contradicts executed funding',key)
    fields(group['scenarios'],{'resserre','central','renforce'},path='group/scenarios')
    required={'titre','duree_mois','interfaces','jh_par_interface','migration_jh_supplementaires',
              'deploiement_jh_par_unite','ouvertures_mois','direction_etp','coordination_etp','nature'}
    references={'corrections_core_par_an':'corrections_core_an',
                'releases_par_an':'campagnes_qualification_versions_an'}
    alternatives=set(references)|{key+'_ref' for key in references}
    for name,spec in group['scenarios'].items():
        fields(spec,required,alternatives,path='group/scenarios/'+name)
        for key,reference in references.items():
            assert (key in spec)!=(key+'_ref' in spec), ('Expected one value or reference',name,key)
            if key+'_ref' in spec:
                assert spec[key+'_ref']==reference, ('Incompatible volume reference',name,key)

def positive(value, zero=True):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or (value<0 if zero else value<=0):
        raise ValueError('Expected finite '+('non-negative' if zero else 'positive')+' number')

def annual_scenario_from(source):
    result=deepcopy(source);scope=result['perimetre'];vol=result['volumes']
    assert not {'demandes_n1_an','escalades_n3_an'} & vol.keys(), 'Derived volumes must not be editable'
    assert sum(scope['profils_utilisation'].values())==scope['utilisateurs_nominatifs'], 'User profiles'
    assert 0<=scope['utilisateurs_simultanes_pointe']<=scope['utilisateurs_nominatifs']
    assert 0<=vol['taux_escalade_n3_pct']<=100
    positive(vol['demandes_n1_par_utilisateur_an'])
    vol['demandes_n1_an']=scope['utilisateurs_nominatifs']*vol['demandes_n1_par_utilisateur_an']
    vol['escalades_n3_an']=vol['demandes_n1_an']*vol['taux_escalade_n3_pct']/100
    assert vol['contrats_flux_modifies_an']<=scope['contrats_flux']
    for k,v in vol.items():
        for n in (v.values() if isinstance(v,dict) else [v]):positive(n)
    return result

@model_memo
def annual_scenario():
    return annual_scenario_from(read(ROOT/'source/maintenance.yaml')['scenario_annuel'])

def validate_funding(config, group, scenario, integration=None):
    """Return independent compiled inputs; no caller can mutate the source cache."""
    validate_group_contract(group, integration if integration is not None else read(ROOT/'source/integration.yaml'))
    c=deepcopy(config);g=deepcopy(group)
    assert set(c)=={'version','date','statut','dependances','contrat','definitions','cartographie','classification_make','reception','relais_service_complet','hebergement_build','buy'}
    assert tuple(c['contrat']['responsabilites'])==RESPONSIBILITIES
    classes=c['classification_make']
    assert set(classes)=={f'MAI-{i:03d}' for i in range(1,10)}
    for aid,row in classes.items():
        expected=({'objet','prestation','decomposition','fixe_responsabilite','charges_responsabilite','preuve','condition'} if aid=='MAI-005' else
                  {'decomposition','core_generique','parametrage_metier','extensions_metier','preuve','montant_pendant_transition'} if aid=='MAI-009' else
                  {'objet','responsabilite','prestation','preuve'})
        assert set(row)==expected, ('Classification fields',aid)
        assert all(v is not None for v in row.values()), aid
        for key in ('responsabilite','fixe_responsabilite','charges_responsabilite','core_generique','parametrage_metier','extensions_metier'):
            if key in row:assert row[key] in RESPONSIBILITIES, (aid,key)
    assert classes['MAI-003']['responsabilite']=='core_lifecycle'
    assert classes['MAI-009']['core_generique']=='core_lifecycle'
    assert classes['MAI-009']['parametrage_metier']==classes['MAI-009']['extensions_metier']=='client_evolutions'
    assert classes['MAI-009']['montant_pendant_transition']==0
    for aid in ('MAI-001','MAI-002','MAI-004','MAI-006','MAI-007','MAI-008'):
        assert classes[aid]['responsabilite'] in ('run','mco_client'), aid
    assert classes['MAI-005']['fixe_responsabilite'] in ('run','mco_client')
    assert classes['MAI-005']['charges_responsabilite'] in ('run','mco_client')
    hosting=c['hebergement_build'];assert hosting['cas_central'] in ('sobre','central','soutenu')
    assert len({p['id'] for p in hosting['phases']})==len(hosting['phases'])
    assert abs(sum(p['part_duree'] for p in hosting['phases'])-1)<1e-9
    for phase in hosting['phases']:
        assert set(phase)=={'id','part_duree','contenu','couts_mensuels_eur_ht'}
        positive(phase['part_duree'],False)
        assert set(phase['couts_mensuels_eur_ht'])=={'sobre','central','soutenu'}
        for costs in phase['couts_mensuels_eur_ht'].values():
            assert set(costs)=={'calcul_runners','bases','stockage_sauvegardes','reseau_traces'}
            for v in costs.values():positive(v)
    assert g['perimetre_ref']=='source/maintenance.yaml#scenario_annuel/perimetre'
    # Context is read from its owner; unit count is derived, not a second assumption.
    scope=g['perimetre'];count=len(scope['poles_candidats'])
    assert count and len(set(scope['poles_candidats']))==count
    shares=scope['repartition_usagers_par_unite']
    assert len(shares)==count and abs(sum(shares)-1)<1e-9, 'Deployment shares'
    for v in shares:positive(v,False)
    scope['contexte']=deepcopy(scenario['perimetre']);scope['unites_deploiement']=count
    roles=g['deploiement']['roles_pct']
    assert set(roles)=={'developpement','integration','support_n3','support_n1'} and sum(roles.values())==100
    for v in roles.values():positive(v)
    assert 0<=g['deploiement']['coordination_technique_pct']<=100
    for v in g['pilotage'].values():
        if isinstance(v,(float,int)):positive(v)
    positive(g['transition']['stabilisation_mois'])
    shared=g['transition']['services_partages'];variable=g['transition']['services_variables']
    assert len(set(shared+variable))==len(shared+variable) and set(shared+variable)<=set(classes)
    for spec in g['scenarios'].values():
        for key in ('corrections_core_par_an','releases_par_an'):
            if key+'_ref' in spec:
                assert key not in spec, 'Value and reference compete'
                spec[key]=scenario['volumes'][spec.pop(key+'_ref')]
        positive(spec['duree_mois'],False)
        assert len(spec['deploiement_jh_par_unite'])==len(spec['ouvertures_mois'])==count
        assert spec['ouvertures_mois']==sorted(spec['ouvertures_mois'])
        assert all(0<=x+g['transition']['stabilisation_mois']<=spec['duree_mois'] for x in spec['ouvertures_mois'])
        for key in ('interfaces','jh_par_interface','migration_jh_supplementaires','direction_etp','coordination_etp','corrections_core_par_an','releases_par_an'):
            positive(spec[key])
        for v in spec['deploiement_jh_par_unite']:positive(v)
    return c,g

@model_memo
def funding_inputs():
    return validate_funding(read(ROOT/'source/modele-composable.yaml'),read(ROOT/'source/deploiement-groupe.yaml'),annual_scenario())

@model_memo
def buy_selection_inputs():
    source=read(ROOT/'source/selection-buy.yaml')
    positive(source['duree_mois'],False)
    assert source['duree_mois']<=24
    rows=source['travaux']
    assert len({r['id'] for r in rows})==len(rows)
    for row in rows:
        positive(row['jh']);positive(row['tarif_eur_ht_jh'])
    positive(source['preparation_reaffectee_eur'])
    source['budget_eur']=round(sum(r['jh']*r['tarif_eur_ht_jh'] for r in rows),2)
    return source
