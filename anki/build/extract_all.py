import glob, re, os, json
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))          # anki/build/
REPO = os.path.dirname(os.path.dirname(HERE))              # repo root
os.chdir(REPO)                                            # so 'FRACTURES MS/...' resolves

DECOR = {'icon_close.png','logo.png','logo-header.png'}
DECOR_PAT = re.compile(r'(/template/|/sprite/|/bootstrap/|banner|warning_bar|loading|spinner)', re.I)
IMG_EXT = re.compile(r'\.(jpe?g|png|gif|bmp)$', re.I)

def clean(s):
    s = s.replace('﻿','').replace('\xa0',' ').replace('•','- ').replace('\t',' ')
    s = re.sub(r'[ ]{2,}',' ', s)
    s = re.sub(r' *\n *','\n', s)
    s = re.sub(r'\n{3,}','\n\n', s)
    return s.strip()

def resolve_img(src, basedir):
    if not src: return None
    s = src.split('?')[0].replace('\\','/').strip()
    if s.startswith('http') or s.startswith('data:'): return None
    base = os.path.basename(s).lower()
    if base in DECOR or DECOR_PAT.search(s): return None
    if not IMG_EXT.search(s): return None
    p = os.path.normpath(os.path.join(basedir, s))
    return p if os.path.exists(p) else None

def popup_imgs(div, basedir):
    out=[]
    if not div: return out
    for img in div.find_all('img'):
        r = resolve_img(img.get('src',''), basedir)
        if r and r not in out: out.append(r)
    return out

def strip_prefix(txt, kind):
    # remove leading "Réponse N" / "Commentaire N" / "Réponse :" labels
    txt = re.sub(r'^\s*(R[ée]ponse|Commentaire)\s*:?\s*\d*\s*:?\s*\n?', '', txt, flags=re.I)
    return clean(txt)

def clean_q(txt, labels):
    for lbl in sorted(labels, key=len, reverse=True):
        if lbl: txt = txt.replace(lbl, ' ')
    txt = re.sub(r'\b(R\d+|C\d+|Figure\s*\d+|fig\s*\d+|PA\s*\++|AP\s*\++|R[ée]f\.?)\b',' ',txt,flags=re.I)
    txt = re.sub(r'\(\s*\)','',txt)
    txt = re.sub(r'\s*\?(\s*\?)+','?',txt)
    txt = re.sub(r'[ ]{2,}',' ',txt).strip(' .\n')
    return txt

def parse_case(path):
    soup = BeautifulSoup(open(path,encoding='utf-8',errors='replace').read(),'html.parser')
    for t in soup(['script','style']): t.decompose()
    basedir = os.path.dirname(path)
    main = soup.find('div',class_=lambda c:c and 'whiteback' in c) or soup
    titres = [clean(h.get_text(' ')) for h in main.select('h3.titre-page')]
    region = titres[0] if titres else ''
    casenum = titres[1] if len(titres)>1 else ''
    # link label -> target div id (capture BEFORE detaching popups)
    label2tgt={}; vfig_ids=[]
    for a in main.find_all('a',href=True):
        m=re.search(r"showDiv\('([^']+)'\)",a['href'])
        if not m: continue
        lbl=clean(a.get_text()); tgt=m.group(1)
        if re.search(r'fig',lbl,re.I): vfig_ids.append(tgt)
        if lbl and lbl not in label2tgt: label2tgt[lbl]=tgt
    # vignette: first substantial <p> not a question
    vign=''
    for p in main.find_all('p'):
        txt=clean(p.get_text(' '))
        if len(txt)>45 and not re.match(r'^\d+\s*\.',txt) and not re.match(r'^R[ée]f',txt):
            vign=txt; break
    vign = re.sub(r'\s*\(fig[^)]*\)\s*$','',vign).strip()
    # questions
    labels=set(label2tgt.keys())|{'Réf'}
    qtexts={}
    for el in main.find_all(['p','li']):
        txt=clean(el.get_text(' '))
        m=re.match(r'^(\d+)\s*\.\s*(.+)',txt)
        if m:
            n=int(m.group(1)); qt=clean_q(m.group(2),labels)
            if n not in qtexts or len(qt)>len(qtexts[n]): qtexts[n]=qt
    # capture popup refs then DETACH every id'd div (fixes unclosed-div nesting in MI)
    popups = {d['id']:d for d in soup.find_all('div',id=True)}
    for d in list(popups.values()):
        try: d.extract()
        except Exception: pass
    vfigs=[]
    for tid in vfig_ids:
        for im in popup_imgs(popups.get(tid), basedir):
            if im not in vfigs: vfigs.append(im)
    qa=[]
    for n in sorted(qtexts):
        rt=label2tgt.get(f'R{n}'); ct=label2tgt.get(f'C{n}')
        rdiv=popups.get(rt); cdiv=popups.get(ct)
        rtext = strip_prefix(clean(rdiv.get_text('\n')),'r') if rdiv else ''
        ctext = strip_prefix(clean(cdiv.get_text('\n')),'c') if cdiv else ''
        rtext = re.sub(r'\n?\s*fig\s*\d+\s*$','',rtext,flags=re.I).strip()
        qa.append(dict(n=n, q=qtexts[n], answer=rtext, comment=ctext,
                       answer_imgs=popup_imgs(rdiv,basedir)))
    return dict(file=path, region=region, casenum=casenum,
                vignette=vign, vignette_imgs=vfigs, qa=qa)

cases=[]
for sec,label in [('FRACTURES MS','MS'),('FRACTURES MI','MI')]:
    files=sorted([p for p in glob.glob(f'{sec}/cas_clinique/cas*.html') if re.search(r'cas\d+\.html',p)],
                 key=lambda p:int(re.search(r'cas(\d+)',p).group(1)))
    for f in files:
        c=parse_case(f); c['section']=label
        c['id']=label+'_'+re.search(r'(cas\d+)',f).group(1)
        cases.append(c)

json.dump(cases, open(os.path.join(HERE,'cases.json'),'w'), ensure_ascii=False, indent=1)
# stats
nq=sum(len(c['qa']) for c in cases)
nqa=sum(1 for c in cases for q in c['qa'] if q['answer'])
nimg=sum(len(c['vignette_imgs']) for c in cases)+sum(len(q['answer_imgs']) for c in cases for q in c['qa'])
print(f"Cases: {len(cases)} | total Q: {nq} | Q with answer: {nqa} | images referenced: {nimg}")
print("\nPer-case summary:")
for c in cases:
    print(f"  {c['id']:10s} {c['region'][:10]:10s} Q={len(c['qa'])} ans={sum(1 for q in c['qa'] if q['answer'])} vimg={len(c['vignette_imgs'])} | {c['vignette'][:55]}")
