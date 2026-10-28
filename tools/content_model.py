"""Resolve declared vocabulary placeholders before publishing presentation data."""
import re

PLACEHOLDER=re.compile(r'\{\{([^{}]+)\}\}')
PUBLIC_NOTIONS=(
    'core_system','flow_core_system','programme_flow','plateforme_beaumanoir',
    'supply_chain_management','maintenance_core','mco_run','mco_client',
    'grouped_buy','socle_technique_cloud','operations_support',
    'integrer_deployer','exploiter_evoluer',
)
PUBLIC_VIEWS=('concepts','complexite_core_system','evaluation_marche','se_projeter','parametres_modele')
RETIRED_PUBLIC_CAPTIONS=(
    'Offres Microsoft/K3 et SAP','Flow Core System','Run & MCO',
    'iPaaS et licences techniques','cycle de vie du Core',
)

def resolve_text_tree(value, glossary, variables=None, path='$'):
    variables=variables or {}
    def walk(item, location):
        if isinstance(item,str):
            def substitute(match):
                key=match.group(1)
                if key in variables:return str(variables[key])
                parts=key.split('.')
                if len(parts) in (2,3) and parts[0]=='notion' and (len(parts)==2 or parts[2]=='court'):
                    field='forme_courte' if len(parts)==3 else 'libelle'
                    term=glossary.get('notions',{}).get(parts[1],{})
                    if field in term:return str(term[field])
                elif len(parts)==2 and parts[0]=='vue':
                    view=glossary.get('vues',{}).get(parts[1],{})
                    if 'libelle' in view:return str(view['libelle'])
                raise ValueError(f'ERR_CONTENT_PARAM:{location}:{key}')
            result=PLACEHOLDER.sub(substitute,item)
            if '{{' in result or '}}' in result:
                raise ValueError(f'ERR_CONTENT_PARAM:{location}:unresolved')
            return result
        if isinstance(item,list):return [walk(child,f'{location}[{index}]') for index,child in enumerate(item)]
        if isinstance(item,dict):return {key:walk(child,f'{location}.{key}') for key,child in item.items()}
        return item
    return walk(value,path)

def validate_glossary_literals(value, glossary, path='$'):
    """Reject copied public captions, including those embedded in explanatory prose."""
    labels={term['libelle'] for term in glossary['notions'].values() if 'libelle' in term}
    protected=[glossary['notions'][key]['libelle'] for key in PUBLIC_NOTIONS if key in glossary.get('notions',{})]
    protected += [glossary['vues'][key]['libelle'] for key in PUBLIC_VIEWS if key in glossary.get('vues',{})]
    phrases=[(label,re.compile(r'(?<!\w)'+re.escape(label)+r'(?!\w)',re.I)) for label in protected+list(RETIRED_PUBLIC_CAPTIONS)]
    def walk(item, location):
        if isinstance(item,str):
            if '.modes[' in location or '.glossary_links.' in location:
                return
            if item in labels:
                raise ValueError(f'ERR_CONTENT_LITERAL:{location}:{item}')
            prose=PLACEHOLDER.sub('',item)
            for label,pattern in phrases:
                if pattern.search(prose):
                    raise ValueError(f'ERR_CONTENT_LITERAL:{location}:{label}')
        elif isinstance(item,list):
            for index,child in enumerate(item):walk(child,f'{location}[{index}]')
        elif isinstance(item,dict):
            for key,child in item.items():walk(child,f'{location}.{key}')
    walk(value,path)
