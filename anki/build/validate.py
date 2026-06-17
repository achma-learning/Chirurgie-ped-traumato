import zipfile, sqlite3, json, os, re, tempfile, html
import os
APKG=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"Pediatrie_Orthopedie_Traumatologie_Enfant.apkg")
d=tempfile.mkdtemp()
z=zipfile.ZipFile(APKG); z.extractall(d)
print("apkg members:", z.namelist()[:6], "...", len(z.namelist()), "total")
# media manifest
media=json.load(open(os.path.join(d,"media")))
print("media entries:", len(media))
# which db
db = "collection.anki21" if os.path.exists(os.path.join(d,"collection.anki21")) else "collection.anki2"
con=sqlite3.connect(os.path.join(d,db)); cur=con.cursor()
nnotes=cur.execute("select count(*) from notes").fetchone()[0]
ncards=cur.execute("select count(*) from cards").fetchone()[0]
print("DB:",db,"| notes:",nnotes,"| cards:",ncards)
# referenced images in notes
flds=[r[0] for r in cur.execute("select flds from notes").fetchall()]
refs=set()
for f in flds:
    refs.update(re.findall(r'src="([^"]+)"', f))
present=set(media.values())
missing=[r for r in refs if r not in present]
print("distinct img refs in notes:", len(refs), "| missing from media:", len(missing))
print("media files all extracted:", all(os.path.exists(os.path.join(d,k)) for k in media))
# field sanity: any empty front?
empty=sum(1 for f in flds if not f.split('\x1f')[0].strip())
print("notes with empty first field:", empty)
# unbalanced cloze check
cl=[f for f in flds if "{{c" in f]
bad=sum(1 for f in cl if f.count("{{c")!=f.count("}}"))
print("cloze notes:",len(cl),"| unbalanced:",bad)
