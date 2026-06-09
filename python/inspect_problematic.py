"""
inspect_problematic.py — gera dossier dos itens problemáticos.

Inspeciona:
  1. Os itens sem título (queried via fieldID).
  2. Os itens da coleção "Problematic - No author" (criada pelo user em 30/05/2026).

Lê o .bak em modo read-only (não toca o banco vivo).
Output: diagnostics/<YYYY-MM-DD>_problematic_inspect.md

Uso:
    python inspect_problematic.py [path_para_bak]
"""
import sqlite3, os, sys
from collections import defaultdict
from datetime import datetime

BAK_DB = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(r"~/Zotero/zotero.sqlite.bak")
PROJECT_ROOT = r"C:\Users\Mancano\Documents\MancanoSync\mancano-zotero-library"
REPORT_DATE = datetime.now().strftime("%Y-%m-%d")
OUT = os.path.join(PROJECT_ROOT, "diagnostics", f"{REPORT_DATE}_problematic_inspect.md")

uri = f"file:{BAK_DB}?mode=ro"
con = sqlite3.connect(uri, uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()

def q(sql, params=()): return cur.execute(sql, params).fetchall()
def q1(sql, params=()):
    r = cur.execute(sql, params).fetchone()
    return r[0] if r else None
def field_id(name): return q1("SELECT fieldID FROM fields WHERE fieldName=?", (name,))
def itemtype_id(name): return q1("SELECT itemTypeID FROM itemTypes WHERE typeName=?", (name,))

NOTE_ID, ATT_ID, ANN_ID = itemtype_id("note"), itemtype_id("attachment"), itemtype_id("annotation")
TITLE_FID = field_id("title")

def get_item_fields(item_id):
    rows = q("""
    SELECT f.fieldName, iv.value
    FROM itemData id JOIN fields f ON f.fieldID=id.fieldID
    JOIN itemDataValues iv ON iv.valueID=id.valueID
    WHERE id.itemID=?""", (item_id,))
    return {r["fieldName"]: r["value"] for r in rows}

def get_creators(item_id):
    rows = q("""
    SELECT c.firstName, c.lastName, c.fieldMode, ct.creatorType
    FROM itemCreators ic
    JOIN creators c ON c.creatorID=ic.creatorID
    JOIN creatorTypes ct ON ct.creatorTypeID=ic.creatorTypeID
    WHERE ic.itemID=?
    ORDER BY ic.orderIndex""", (item_id,))
    return [dict(r) for r in rows]

def get_collections(item_id):
    rows = q("""SELECT c.collectionName FROM collectionItems ci
                JOIN collections c ON c.collectionID=ci.collectionID
                WHERE ci.itemID=?""", (item_id,))
    return [r["collectionName"] for r in rows]

def get_item_type(item_id):
    return q1("""SELECT t.typeName FROM items i JOIN itemTypes t ON t.itemTypeID=i.itemTypeID
                 WHERE i.itemID=?""", (item_id,))

def get_attachments(item_id):
    rows = q("""
    SELECT i.itemID, ia.contentType, ia.path, ia.linkMode,
           (SELECT iv.value FROM itemData id JOIN itemDataValues iv ON iv.valueID=id.valueID
            JOIN fields f ON f.fieldID=id.fieldID WHERE id.itemID=i.itemID AND f.fieldName='title') as title
    FROM itemAttachments ia
    JOIN items i ON i.itemID=ia.itemID
    WHERE ia.parentItemID=?""", (item_id,))
    return [dict(r) for r in rows]

def is_in_trash(item_id):
    return q1("SELECT 1 FROM deletedItems WHERE itemID=?", (item_id,)) is not None

# ---- coleta -------------------------------------------------------------------
no_title_ids = [r["itemID"] for r in q(f"""
SELECT i.itemID FROM items i
WHERE i.itemTypeID NOT IN ({NOTE_ID},{ATT_ID},{ANN_ID})
  AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
  AND i.itemID NOT IN (SELECT itemID FROM itemData WHERE fieldID=?)""", (TITLE_FID,))]

coll_id = q1("SELECT collectionID FROM collections WHERE collectionName='Problematic - No author'")
prob_ids = []
if coll_id:
    prob_ids = [r["itemID"] for r in q("SELECT itemID FROM collectionItems WHERE collectionID=?", (coll_id,))]
prob_ids = [iid for iid in prob_ids if not is_in_trash(iid)
            and get_item_type(iid) not in (None, "note", "attachment", "annotation")]

def dossier(item_id):
    return {
        "id": item_id, "type": get_item_type(item_id),
        "fields": get_item_fields(item_id), "creators": get_creators(item_id),
        "collections": get_collections(item_id), "attachments": get_attachments(item_id),
    }

# ---- gera markdown ------------------------------------------------------------
lines = [f"# Inspeção: sem título + 'Problematic - No author' — {REPORT_DATE}", "",
         f"Fonte: `{BAK_DB}` (read-only via URI)", ""]
def w(s=""): lines.append(s)

w("## 1. Itens sem título")
w()
w(f"Total: **{len(no_title_ids)}** item(ns).")
w()
for iid in no_title_ids:
    d = dossier(iid)
    w(f"### itemID `{iid}` — tipo: `{d['type']}`")
    w()
    w(f"- **Coleções**: {d['collections'] or '_(nenhuma)_'}")
    w(f"- **Anexos**: {len(d['attachments'])}")
    for a in d["attachments"]:
        w(f"  - `{a['title'] or '(sem título)'}` — `{a['contentType'] or 'sem tipo'}` — path: `{a['path'] or '(none)'}`")
    if d["creators"]:
        ppl = "; ".join(f"{c['lastName'] or ''}, {c['firstName'] or ''}".strip(', ') for c in d["creators"])
        w(f"- **Creators**: {ppl}")
    w()
    w("**Campos:**")
    w()
    w("| Campo | Valor |")
    w("|-------|-------|")
    for k, v in d["fields"].items():
        vshort = (v or "")[:200].replace("\n", " ").replace("|", "\\|")
        w(f"| `{k}` | {vshort} |")
    w()

w()
w("---")
w()
w(f"## 2. Coleção 'Problematic - No author' ({len(prob_ids)} itens)")
w()

by_type = defaultdict(list)
for iid in prob_ids: by_type[get_item_type(iid)].append(iid)
w("### Distribuição por tipo")
w()
w("| Tipo | n |")
w("|------|--:|")
for t, ids in sorted(by_type.items(), key=lambda x: -len(x[1])):
    w(f"| {t} | {len(ids)} |")
w()

w("### Tabela compacta")
w()
w("| id | tipo | título (60c) | data | URL/DOI | anexo? | outras coleções |")
w("|---:|------|--------------|------|---------|:------:|------------------|")
for iid in sorted(prob_ids):
    d = dossier(iid)
    f = d["fields"]
    title = (f.get("title") or "_(sem título)_")[:60].replace("|", "\\|").replace("\n"," ")
    date = f.get("date", "")
    iden = (f.get("DOI") or f.get("url","")[:60]).replace("|","\\|")
    att  = "✓" if d["attachments"] else "✗"
    other_colls = [c for c in d["collections"] if c != "Problematic - No author"]
    oc = ", ".join(other_colls[:3]).replace("|","\\|")
    if len(other_colls) > 3: oc += f" (+{len(other_colls)-3})"
    w(f"| {iid} | {d['type']} | {title} | {date} | {iden} | {att} | {oc} |")
w()

w("### Detalhe item-a-item")
w()
for iid in sorted(prob_ids):
    d = dossier(iid)
    f = d["fields"]
    title = f.get("title", "_(sem título)_")
    w(f"#### `{iid}` [{d['type']}] {title[:100]}")
    w()
    w(f"- **Data:** {f.get('date','—')}")
    if f.get("DOI"): w(f"- **DOI:** {f['DOI']}")
    if f.get("ISBN"): w(f"- **ISBN:** {f['ISBN']}")
    if f.get("url"):  w(f"- **URL:** {f['url']}")
    if f.get("publicationTitle"): w(f"- **Journal:** {f['publicationTitle']}")
    if f.get("publisher"): w(f"- **Publisher:** {f['publisher']}")
    if d["collections"]: w(f"- **Coleções:** {', '.join(d['collections'])}")
    for a in d["attachments"]:
        w(f"- **Anexo:** `{a['title'] or 'sem nome'}` ({a['contentType']})")
    if f.get("abstractNote"):
        ab = f["abstractNote"][:300].replace("\n"," ")
        w(f"- **Abstract:** {ab}...")
    w()

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh: fh.write("\n".join(lines))
print(f"OK — {OUT} ({len(lines)} linhas)")
print(f"Sem título: {len(no_title_ids)}  |  Problematic: {len(prob_ids)}")
con.close()
