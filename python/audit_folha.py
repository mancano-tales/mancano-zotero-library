"""
audit_folha.py — audit detalhado dos itens da Folha de S.Paulo.

Lê o .bak em modo read-only e classifica os itens (busca ampla:
URL folha.uol.com.br OR publicationTitle "Folha" OR creator com "Folha") em buckets:

  ✅ OK humano       — creator humano + URL presente
  ✅ OK institucional — creator "Folha de S.Paulo" fm=1 + URL
  ❌ FIX fm=0        — creator Folha/de S.Paulo fm=0 → trocar pra fm=1
  ❌ FIX sem creator — URL Folha sem creator → adicionar institucional fm=1
  ⚠️ FIX sem URL     — claramente Folha (publicationTitle ou creator) mas sem URL → user adiciona manual
  ⚠️ FIX sem date    — sem data publicada (não bloqueante)

Saídas em diagnostics/:
  <YYYY-MM-DD>_folha_audit.md    — relatório markdown com listas
  <YYYY-MM-DD>_folha_audit.json  — dump estruturado pra alimentar Script N

Uso:
    python audit_folha.py [path_para_bak]
    # default: ~/Zotero/zotero.sqlite.bak
"""
import sqlite3, os, sys, json
from datetime import datetime

BAK_DB = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(r"~/Zotero/zotero.sqlite.bak")
PROJECT_ROOT = r"C:\Users\Mancano\Documents\MancanoSync\mancano-zotero-library"
REPORT_DATE = datetime.now().strftime("%Y-%m-%d")
OUT_MD = os.path.join(PROJECT_ROOT, "diagnostics", f"{REPORT_DATE}_folha_audit.md")
OUT_JSON = os.path.join(PROJECT_ROOT, "diagnostics", f"{REPORT_DATE}_folha_audit.json")

con = sqlite3.connect(f"file:{BAK_DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()

def q(s, p=()): return cur.execute(s, p).fetchall()
def q1(s, p=()):
    r = cur.execute(s, p).fetchone()
    return r[0] if r else None

def field_id(name): return q1("SELECT fieldID FROM fields WHERE fieldName=?", (name,))
def itemtype_id(name): return q1("SELECT itemTypeID FROM itemTypes WHERE typeName=?", (name,))

ATT_ID = itemtype_id("attachment")
NOTE_ID = itemtype_id("note")
ANN_ID = itemtype_id("annotation")
URL_FID = field_id("url")
TITLE_FID = field_id("title")
DATE_FID = field_id("date")
PUB_TITLE_FID = field_id("publicationTitle")

# Universo: união de 3 critérios
ids_url = {r["itemID"] for r in q(f"""
    SELECT i.itemID FROM items i
    JOIN itemData id ON id.itemID=i.itemID AND id.fieldID={URL_FID}
    JOIN itemDataValues iv ON iv.valueID=id.valueID
    WHERE i.itemTypeID NOT IN ({ATT_ID},{NOTE_ID},{ANN_ID})
      AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
      AND iv.value LIKE '%folha.uol.com.br%'
""")}

ids_pub = {r["itemID"] for r in q(f"""
    SELECT i.itemID FROM items i
    JOIN itemData id ON id.itemID=i.itemID AND id.fieldID={PUB_TITLE_FID}
    JOIN itemDataValues iv ON iv.valueID=id.valueID
    WHERE i.itemTypeID NOT IN ({ATT_ID},{NOTE_ID},{ANN_ID})
      AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
      AND iv.value LIKE '%Folha%'
""")}

ids_creator = {r["itemID"] for r in q("""
    SELECT DISTINCT ic.itemID FROM itemCreators ic
    JOIN creators cr ON cr.creatorID=ic.creatorID
    JOIN items i ON i.itemID=ic.itemID
    WHERE (cr.lastName LIKE '%Folha%' OR cr.firstName LIKE '%Folha%')
      AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
""")}

all_ids = sorted(ids_url | ids_pub | ids_creator)

def get_field(item_id, fid):
    return q1(f"""
        SELECT iv.value FROM itemData id JOIN itemDataValues iv ON iv.valueID=id.valueID
        WHERE id.itemID=? AND id.fieldID=?
    """, (item_id, fid))

def get_creators(item_id):
    return q("""
        SELECT cr.creatorID, cr.firstName, cr.lastName, cr.fieldMode, ct.creatorType, ic.orderIndex
        FROM itemCreators ic
        JOIN creators cr ON cr.creatorID=ic.creatorID
        JOIN creatorTypes ct ON ct.creatorTypeID=ic.creatorTypeID
        WHERE ic.itemID=?
        ORDER BY ic.orderIndex
    """, (item_id,))

def get_item_key(item_id):
    return q1("SELECT key FROM items WHERE itemID=?", (item_id,))

def get_type(item_id):
    return q1("""SELECT t.typeName FROM items i JOIN itemTypes t ON t.itemTypeID=i.itemTypeID
                 WHERE i.itemID=?""", (item_id,))

# Categorização
buckets = {
    "ok_humano": [],
    "ok_institucional": [],
    "fix_fm0": [],
    "fix_sem_creator": [],
    "fix_sem_url": [],
    "fix_sem_date": [],
}

for iid in all_ids:
    item_type = get_type(iid)
    title = get_field(iid, TITLE_FID) or ""
    url = get_field(iid, URL_FID) or ""
    date = get_field(iid, DATE_FID) or ""
    pub = get_field(iid, PUB_TITLE_FID) or ""
    creators = get_creators(iid)
    key = get_item_key(iid)

    has_url_folha = "folha.uol.com.br" in url.lower()
    has_pub_folha = "folha" in pub.lower()
    has_inst_folha_fm1 = any(c["fieldMode"] == 1 and "folha" in (c["lastName"] or "").lower() for c in creators)
    # detecção do bug fm=0: lastName="de S.Paulo" + firstName="Folha"
    has_buggy_fm0 = any(
        c["fieldMode"] == 0 and
        (c["lastName"] or "").strip() == "de S.Paulo" and
        (c["firstName"] or "").strip() == "Folha"
        for c in creators
    )
    has_any_creator = len(creators) > 0
    has_human_creator = any(
        c["fieldMode"] == 0 and (c["firstName"] or c["lastName"]) and
        not (
            (c["lastName"] or "").strip() == "de S.Paulo" and
            (c["firstName"] or "").strip() == "Folha"
        )
        for c in creators
    )

    base = {
        "id": iid,
        "key": key,
        "type": item_type,
        "title": title,
        "url": url,
        "date": date,
        "publicationTitle": pub,
        "creators": [
            {"firstName": c["firstName"], "lastName": c["lastName"],
             "fieldMode": c["fieldMode"], "creatorType": c["creatorType"]}
            for c in creators
        ],
    }

    # Bucket atribuição (ordem importa)
    if has_buggy_fm0:
        buckets["fix_fm0"].append(base); continue
    if has_url_folha and not has_any_creator:
        buckets["fix_sem_creator"].append(base); continue
    if (has_pub_folha or has_inst_folha_fm1) and not url:
        buckets["fix_sem_url"].append(base); continue
    if has_human_creator and url:
        if not date:
            buckets["fix_sem_date"].append(base)
        buckets["ok_humano"].append(base); continue
    if has_inst_folha_fm1 and url:
        if not date:
            buckets["fix_sem_date"].append(base)
        buckets["ok_institucional"].append(base); continue
    # fallback: tem URL mas creator esquisito ou tem pub mas URL — manda pra revisão
    buckets["fix_sem_url"].append(base)

con.close()

# Persist JSON
os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
with open(OUT_JSON, "w", encoding="utf-8") as fh:
    json.dump(buckets, fh, ensure_ascii=False, indent=2)

# Markdown report
lines = []
def w(s=""): lines.append(s)

w(f"# Audit Folha de S.Paulo — {REPORT_DATE}")
w()
w(f"Total inspecionado: **{len(all_ids)}** itens (URL Folha: {len(ids_url)}, pub Folha: {len(ids_pub)}, creator Folha: {len(ids_creator)})")
w()
w("## Distribuição")
w()
w("| Bucket | Quantidade | Ação |")
w("|--------|-----------:|------|")
w(f"| ✅ OK humano | {len(buckets['ok_humano'])} | nenhuma — jornalista nominal + URL ✓ |")
w(f"| ✅ OK institucional | {len(buckets['ok_institucional'])} | nenhuma — Folha de S.Paulo fm=1 + URL ✓ |")
w(f"| ❌ FIX fm=0 errado | {len(buckets['fix_fm0'])} | Script N: trocar pra fm=1 |")
w(f"| ❌ FIX sem creator | {len(buckets['fix_sem_creator'])} | Script N: adicionar Folha de S.Paulo fm=1 |")
w(f"| ⚠️ FIX sem URL | {len(buckets['fix_sem_url'])} | user adiciona URL manualmente |")
w(f"| ⚠️ FIX sem date (subset dos OK) | {len(buckets['fix_sem_date'])} | user revisa data |")
w()

def render_bucket(title, items, show_url=True, show_date=False, show_creators=True):
    w(f"## {title} ({len(items)})")
    w()
    if not items:
        w("_(vazio)_")
        w()
        return
    w("| id | key | tipo | título | creator(s) | URL | data |")
    w("|---:|-----|------|--------|------------|-----|------|")
    for it in items:
        title = (it["title"] or "(sem título)")[:60].replace("|", "/")
        creators_str = "; ".join(
            f"`{c['lastName']!r}/{c['firstName']!r}/fm={c['fieldMode']}`"
            for c in it["creators"]
        ) or "_SEM CREATOR_"
        url_s = (it["url"] or "")[:50]
        date_s = (it["date"] or "")[:10]
        w(f"| {it['id']} | [{it['key']}](zotero://select/library/items/{it['key']}) | {it['type']} | {title} | {creators_str} | {url_s} | {date_s} |")
    w()

render_bucket("❌ FIX fm=0 — trocar creator pra fieldMode=1", buckets["fix_fm0"])
render_bucket("❌ FIX sem creator — adicionar Folha de S.Paulo fm=1", buckets["fix_sem_creator"])
render_bucket("⚠️ FIX sem URL — user adiciona URL manualmente", buckets["fix_sem_url"])
render_bucket("⚠️ FIX sem date — user revisa data (subset)", buckets["fix_sem_date"])
render_bucket("✅ OK humano — jornalista nominal", buckets["ok_humano"])
render_bucket("✅ OK institucional — Folha de S.Paulo fm=1", buckets["ok_institucional"])

with open(OUT_MD, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))

print(f"Relatório: {OUT_MD}")
print(f"JSON:      {OUT_JSON}")
print()
print("=== RESUMO ===")
print(f"Total inspecionado:      {len(all_ids)}")
print(f"  ✅ OK humano:          {len(buckets['ok_humano'])}")
print(f"  ✅ OK institucional:   {len(buckets['ok_institucional'])}")
print(f"  ❌ FIX fm=0:           {len(buckets['fix_fm0'])}")
print(f"  ❌ FIX sem creator:    {len(buckets['fix_sem_creator'])}")
print(f"  ⚠️ FIX sem URL:        {len(buckets['fix_sem_url'])}")
print(f"  ⚠️ FIX sem date:       {len(buckets['fix_sem_date'])} (subset dos OK)")
