"""Render the canonical glossary as Markdown; all visible content comes from YAML."""
import argparse
import json
import os
from pathlib import Path
from validate_stacks import ROOT, read

SOURCE=ROOT/'source/glossaire.yaml'
OUTPUT=ROOT/'source/glossaire.md'

def render():
    model=read(SOURCE);doc=model['document']
    esc=lambda value:str(value).replace('|','\\|').replace('\n',' ')
    lines=['# '+doc['titre'],'',doc['introduction'],'','> '+doc['avertissement'],'',
           '| '+' | '.join(doc['colonnes'])+' |','| '+' | '.join('---' for _ in doc['colonnes'])+' |']
    for term in model['notions'].values():
        ref,_,anchor=term['source_ref'].partition('#')
        relative=Path(os.path.relpath(ROOT/ref,OUTPUT.parent)).as_posix()
        link='['+esc(ref)+']('+relative+('#'+anchor if anchor else '')+')'
        lines.append('| '+' | '.join([esc(term['libelle']),esc(term.get('forme_courte','')),esc(term['definition']+(' '+term['dans_etude'] if term.get('dans_etude') else '')),link,esc(', '.join(term.get('synonymes_historiques',[])))])+' |')
    for key,title in [('options','titre_options'),('vues','titre_vues')]:
        lines+=['','## '+doc[title],'']
        lines+=['- '+item['libelle'] for item in model[key].values()]
    return '\n'.join(lines)+'\n'

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    content=render()
    if args.check: assert OUTPUT.read_text(encoding='utf-8')==content,'ERR_GLOSSARY_STALE'
    else: OUTPUT.write_text(content,encoding='utf-8')
    print(json.dumps(dict(path=str(OUTPUT),notions=len(read(SOURCE)['notions'])),ensure_ascii=False))
