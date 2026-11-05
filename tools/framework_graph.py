"""Project the canonical model and team interactions, without extra relations."""
from copy import deepcopy
from validate_stacks import ROOT, read

SOURCE='config/schema-modele.yaml'


def dependencies():
    return {SOURCE,'tools/framework_graph.py'}


def build_graph(model, organisation, settings=None):
    settings=deepcopy(settings if settings is not None else read(ROOT/SOURCE))
    def require(value,message):
        if not value:raise ValueError('ERR_FRAMEWORK_GRAPH: '+message)
    require(set(settings)=={'version','labels','profiles','aria','domain_colors'} and settings['version']==1,'Settings contract')
    require(all(isinstance(v,str) and v.strip() for v in settings['labels'].values()),'Empty label')
    require(all(isinstance(v,str) and v.strip() for v in settings['aria'].values()),'Empty accessibility label')
    require(set(settings['domain_colors'])=={d['id'] for d in model['domains']},'Domain colour scope')
    domains=[dict(d,color=settings['domain_colors'][d['id']]) for d in model['domains']]
    require(all(isinstance(d['color'],str) and len(d['color'])==7 and d['color'].startswith('#') and all(c in '0123456789abcdefABCDEF' for c in d['color'][1:]) for d in domains),'Invalid domain colour')
    domain_by_id={d['id']:d for d in domains}
    require(all(o['domain_ref'] in domain_by_id for o in model['objects']),'Unknown object domain')
    objects=[dict(id=o['id'],label=o['label'],domain_ref=o['domain_ref'],owner=o['owner'],attributes=list(o['attributes']),description=o.get('description',''),kind='object',color=domain_by_id[o['domain_ref']]['color'],href='') for o in model['objects']]
    ids={n['id'] for n in objects}
    require(len(ids)==len(objects),'Duplicate model object')
    relations=deepcopy(model['relations'])
    require(len({r['id'] for r in relations})==len(relations),'Duplicate relation')
    require(all(r['source'] in ids and r['target'] in ids for r in relations),'Unknown relation endpoint')
    profiles=settings['profiles']
    require(len({p['id'] for p in profiles})==len(profiles),'Duplicate profile')
    require(all(set(p)=={'id','label','description','kind','object_refs'} for p in profiles),'Profile contract')
    for p in profiles:
        require(p['kind'] in {'model','teams','rules'},'Unknown profile kind')
        require(len(p['object_refs'])==len(set(p['object_refs'])) and set(p['object_refs'])<=ids,'Unknown profile object')
    mode_labels={m['id']:m for m in organisation['interaction_modes']}
    type_labels={t['id']:t for t in organisation['team_types']}
    team_nodes=[dict(id=t['id'],label=t['label'],owner=type_labels[t['type']]['label'],attributes=[],
                     description=t['mission'],kind='team',color=type_labels[t['type']]['color'],href='#equipes-produit?option=java-spring&focus='+t['id'],boundary=t['boundary'],responsibilities=deepcopy(t['responsibilities'])) for t in organisation['teams']]
    board=organisation['governance']
    team_nodes.append(dict(id=board['id'],label=board['label'],owner=settings['labels']['governance'],attributes=[],description=board['mission'],kind='governance',color='#E7E9ED',href='#gouvernance-delivery'))
    # No decision arrows are invented for the board. It has no TT interaction.
    team_edges=[dict(id=r['id'],source=r['source'],target=r['target'],label=mode_labels[r['mode']]['label'],meaning=r['object'],cardinality='',mode=r['mode'],phases=list(r['phases']),exit_criterion=r['exit_criterion'],status=r['status']) for r in organisation['interactions']]
    rules=[dict(id='rule:'+r['id'],label=r['title'],owner=r['kind'],attributes=list(r['variables']),description=r['note'],expression=r['expression'],variables=deepcopy(r['variables']),unit=r['unit'],kind='rule',color='#E7E0F2',href='') for r in model['rules']]
    implementations=list({i['path']:dict(id='implementation:'+i['path'],label=i['path'].removeprefix('tools/'),owner=i['path'],attributes=[],description=settings['labels']['implementation_note'],kind='implementation',color='#FFF0DB',href='') for i in model['implementations']}.values())
    rule_ids={r['id'] for r in model['rules']}
    implemented=[r for i in model['implementations'] for r in i['rules']]
    require(len(implemented)==len(set(implemented)) and set(implemented)==rule_ids,'Rule implementation contract')
    rule_edges=[dict(id='exec:'+r,source='rule:'+r,target='implementation:'+i['path'],label=settings['labels']['implemented_by'],meaning=settings['labels']['implementation_note'],cardinality='many-to-one') for i in model['implementations'] for r in i['rules']]
    return dict(source='source/fondamentaux.yaml#estimation_model',labels=settings['labels'],aria=settings['aria'],profiles=profiles,
                domains=domains,objects=objects,relations=[dict(r,label=r.get('label',r['id']),display_label=r.get('label',r['cardinality'])) for r in relations],teams=team_nodes,interactions=team_edges,
                rules=[*rules,*implementations],rule_relations=rule_edges,phases=deepcopy(organisation['phases']))
