import glob, re, os, json
from bs4 import BeautifulSoup
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
os.chdir(REPO)
def readf(path):
    b=open(path,'rb').read()
    for enc in ('utf-8-sig','utf-8'):
        try: return b.decode(enc)
        except: pass
    return b.decode('cp1252',errors='replace')
def clean(s):
    s=s.replace('﻿','').replace('\xa0',' ').replace('•','- ').replace('\t',' ')
    s=re.sub(r'[ ]{2,}',' ',s); s=re.sub(r' *\n *','\n',s); s=re.sub(r'\n{3,}','\n\n',s)
    return s.strip()
NAVJUNK=re.compile(r'^(Scroll|Cas clinique.*|Epaule|Bras|Coude|Avant-bras|Poignet|Cas Clinique.*|Boiteries.*|Aigues|Chroniques|Fractures spécifiques.*|Fracture en .*|Fracture plastique|Fracture décollement.*|Ossification du.*|Informations à.*|[Pp]articularités.*|[Pp]rise en cha.*|immobilisation du.*|Service de traumato.*|Réalisation.*|Rapporteur.*|Président.*|Le Genou|La Hanche|La Cheville|fig\d+.*)$',re.I)
pages={}
files=glob.glob('FRACTURES MS/prerequis/*.html')+glob.glob('FRACTURES MI/prerequis/*.html')+ \
      ['FRACTURES MS/resume/resume.html','FRACTURES MI/resume/resume.html',
       'FRACTURES MS/introduction/introduction.html','FRACTURES MI/introduction/introduction.html']
for f in files:
    if not os.path.exists(f): continue
    soup=BeautifulSoup(readf(f),'html.parser')
    for t in soup(['script','style']): t.decompose()
    main=soup.find('div',class_=lambda c:c and 'whiteback' in c) or soup.find('body') or soup
    lines=[clean(l) for l in main.get_text('\n').split('\n') if clean(l)]
    lines=[l for l in lines if not NAVJUNK.match(l) and len(l)>1]
    pages[f]='\n'.join(lines)
json.dump(pages,open(os.path.join(HERE,'prereq.json'),'w'),ensure_ascii=False,indent=1)
print("Pages:",len(pages),"| total chars:",sum(len(v) for v in pages.values()))
# dump the two resume pages fully (the goldmine)
for f in ['FRACTURES MI/resume/resume.html']:
    print('\n'+'#'*70+'\n# '+f+'\n'+'#'*70)
    print(pages[f][:4500])
