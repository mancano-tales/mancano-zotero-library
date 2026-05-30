"""
Diagnóstico atualizado da biblioteca Zotero.

- Lê o .bak (cópia estável feita pelo próprio Zotero) em modo read-only via URI.
- Não precisa fechar o Zotero nem copiar nada.
- Roda as mesmas consultas do relatório anterior (09/05/2026) pra comparação.

Uso:
    python diagnose_v2.py [path_para_bak]
    # default: ~/Zotero/zotero.sqlite.bak
"""
import sqlite3
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime

# ---------- config ----------------------------------------------------------
BAK_DB = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(r"~/Zotero/zotero.sqlite.bak")
PROJECT_ROOT = r"C:\Users\Mancano\Documents\MancanoSync\mancano-zotero-library"
REPORT_DATE = datetime.now().strftime("%Y-%m-%d")
REPORT = os.path.join(PROJECT_ROOT, "diagnostics", f"{REPORT_DATE}_relatorio.md")

# ---------- conexão ---------------------------------------------------------
bak_mtime = datetime.fromtimestamp(os.path.getmtime(BAK_DB)).strftime("%Y-%m-%d %H:%M")
print(f"[1] Lendo .bak em modo read-only via URI: {BAK_DB}")
print(f"    Timestamp do .bak: {bak_mtime}")

uri = f"file:{BAK_DB}?mode=ro"
con = sqlite3.connect(uri, uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()

def q(sql, params=()):
    return cur.execute(sql, params).fetchall()
def q1(sql, params=()):
    r = cur.execute(sql, params).fetchone()
    return r[0] if r else None
def field_id(name):
    return q1("SELECT fieldID FROM fields WHERE fieldName=?", (name,))
def itemtype_id(name):
    return q1("SELECT itemTypeID FROM itemTypes WHERE typeName=?", (name,))

NOTE_ID = itemtype_id("note")
ATT_ID  = itemtype_id("attachment")
ANN_ID  = itemtype_id("annotation")
JART_ID = itemtype_id("journalArticle")
BOOK_ID = itemtype_id("book")
EXCLUDE_NON_BIB = f"i.itemTypeID NOT IN ({NOTE_ID},{ATT_ID},{ANN_ID})"
TRASH_FILTER = "AND i.itemID NOT IN (SELECT itemID FROM deletedItems)"

TITLE_FID = field_id("title")
DATE_FID  = field_id("date")
DOI_FID   = field_id("DOI")
ISBN_FID  = field_id("ISBN")
PUB_FID   = field_id("publicationTitle")
PUBLISHER_FID = field_id("publisher")
ABS_FID   = field_id("abstractNote")

# ---------- 1. visão geral --------------------------------------------------
n_items_bib = q1(f"SELECT COUNT(*) FROM items i WHERE {EXCLUDE_NON_BIB} {TRASH_FILTER}")
n_attach = q1(f"SELECT COUNT(*) FROM items i WHERE i.itemTypeID={ATT_ID} {TRASH_FILTER}")
n_notes  = q1(f"SELECT COUNT(*) FROM items i WHERE i.itemTypeID={NOTE_ID} {TRASH_FILTER}")
n_trash  = q1("SELECT COUNT(*) FROM deletedItems")
n_colls  = q1("SELECT COUNT(*) FROM collections")
n_tags   = q1("SELECT COUNT(*) FROM tags")

type_dist = q(f"""
SELECT t.typeName, COUNT(*) n
FROM items i JOIN itemTypes t ON t.itemTypeID=i.itemTypeID
WHERE {EXCLUDE_NON_BIB} {TRASH_FILTER}
GROUP BY t.typeName ORDER BY n DESC
""")

# ---------- 2. metadados faltantes ------------------------------------------
def items_missing_field(fid):
    return q1(f"""
    SELECT COUNT(*) FROM items i
    WHERE {EXCLUDE_NON_BIB} {TRASH_FILTER}
      AND i.itemID NOT IN (SELECT itemID FROM itemData WHERE fieldID=?)
    """, (fid,))

n_no_title = items_missing_field(TITLE_FID)
n_no_date  = items_missing_field(DATE_FID)
n_no_abs   = items_missing_field(ABS_FID)
n_no_creator = q1(f"""
SELECT COUNT(*) FROM items i
WHERE {EXCLUDE_NON_BIB} {TRASH_FILTER}
  AND i.itemID NOT IN (SELECT itemID FROM itemCreators)
""")

n_art_no_pub = q1(f"""SELECT COUNT(*) FROM items i WHERE i.itemTypeID={JART_ID} {TRASH_FILTER}
  AND i.itemID NOT IN (SELECT itemID FROM itemData WHERE fieldID=?)""", (PUB_FID,))
n_art_no_doi = q1(f"""SELECT COUNT(*) FROM items i WHERE i.itemTypeID={JART_ID} {TRASH_FILTER}
  AND i.itemID NOT IN (SELECT itemID FROM itemData WHERE fieldID=?)""", (DOI_FID,))
n_book_no_isbn = q1(f"""SELECT COUNT(*) FROM items i WHERE i.itemTypeID={BOOK_ID} {TRASH_FILTER}
  AND i.itemID NOT IN (SELECT itemID FROM itemData WHERE fieldID=?)""", (ISBN_FID,))
n_book_no_publisher = q1(f"""SELECT COUNT(*) FROM items i WHERE i.itemTypeID={BOOK_ID} {TRASH_FILTER}
  AND i.itemID NOT IN (SELECT itemID FROM itemData WHERE fieldID=?)""", (PUBLISHER_FID,))

# ---------- 3. duplicatas ---------------------------------------------------
def value_of(fid):
    return f"""
    SELECT i.itemID, iv.value
    FROM items i
    JOIN itemData id ON id.itemID=i.itemID AND id.fieldID={fid}
    JOIN itemDataValues iv ON iv.valueID=id.valueID
    WHERE {EXCLUDE_NON_BIB} {TRASH_FILTER}
    """

doi_groups = defaultdict(list)
for row in q(value_of(DOI_FID)):
    doi = (row["value"] or "").strip().lower()
    if doi: doi_groups[doi].append(row["itemID"])
doi_dups = {k:v for k,v in doi_groups.items() if len(v) > 1}

isbn_groups = defaultdict(list)
for row in q(value_of(ISBN_FID)):
    isbn = (row["value"] or "").strip()
    if isbn: isbn_groups[isbn].append(row["itemID"])
isbn_dups = {k:v for k,v in isbn_groups.items() if len(v) > 1}

def norm(s):
    s = (s or "").lower()
    s = re.sub(r"[^\w\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

titles = {r["itemID"]: r["value"] for r in q(value_of(TITLE_FID))}
dates  = {r["itemID"]: r["value"] for r in q(value_of(DATE_FID))}
ty_groups = defaultdict(list)
for iid, t in titles.items():
    if not t: continue
    year_match = re.search(r"\b(1[89]\d{2}|20\d{2})\b", dates.get(iid, "") or "")
    year = year_match.group(0) if year_match else "?"
    key = (norm(t)[:80], year)
    ty_groups[key].append(iid)
ty_dups = {k:v for k,v in ty_groups.items() if len(v) > 1}

# ---------- 4. anexos -------------------------------------------------------
n_orphan_att = q1(f"""
SELECT COUNT(*) FROM itemAttachments ia
JOIN items i ON i.itemID=ia.itemID
WHERE ia.parentItemID IS NULL {TRASH_FILTER}
""")
n_items_no_att = q1(f"""
SELECT COUNT(*) FROM items i
WHERE {EXCLUDE_NON_BIB} {TRASH_FILTER}
  AND i.itemID NOT IN (SELECT parentItemID FROM itemAttachments WHERE parentItemID IS NOT NULL)
""")
content_types = q("""
SELECT COALESCE(ia.contentType,'') ct, COUNT(*) n
FROM itemAttachments ia
JOIN items i ON i.itemID=ia.itemID
WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
GROUP BY ct ORDER BY n DESC
""")

# ---------- 5. coleções -----------------------------------------------------
n_unfiled = q1(f"""
SELECT COUNT(*) FROM items i
WHERE {EXCLUDE_NON_BIB} {TRASH_FILTER}
  AND i.itemID NOT IN (SELECT itemID FROM collectionItems)
""")
empty_colls = q("""
SELECT c.collectionName FROM collections c
LEFT JOIN collectionItems ci ON ci.collectionID=c.collectionID
LEFT JOIN collections cc ON cc.parentCollectionID=c.collectionID
WHERE ci.itemID IS NULL AND cc.collectionID IS NULL
ORDER BY c.collectionName
""")
top_colls = q("""
SELECT c.collectionName, COUNT(ci.itemID) n
FROM collections c LEFT JOIN collectionItems ci ON ci.collectionID=c.collectionID
GROUP BY c.collectionID ORDER BY n DESC LIMIT 15
""")
root_colls = q("""
SELECT c.collectionID, c.collectionName,
       (SELECT COUNT(*) FROM collectionItems WHERE collectionID=c.collectionID) AS n_items,
       (SELECT COUNT(*) FROM collections WHERE parentCollectionID=c.collectionID) AS n_subs
FROM collections c
WHERE c.parentCollectionID IS NULL
ORDER BY c.collectionName
""")

# ---------- 6. tags ---------------------------------------------------------
tag_usage = q("""
SELECT t.name, COUNT(it.itemID) n
FROM tags t LEFT JOIN itemTags it ON it.tagID=t.tagID
GROUP BY t.tagID
""")
n_tag_once = sum(1 for _,n in tag_usage if n <= 1)
case_groups = defaultdict(set)
for name, _ in tag_usage:
    case_groups[name.lower()].add(name)
case_variants = {k:sorted(v) for k,v in case_groups.items() if len(v) > 1}
top_tags = sorted(tag_usage, key=lambda x: -x[1])[:25]
namespace_tags = [(n, c) for n, c in tag_usage if ':' in n]

# ---------- 7. write report -------------------------------------------------
os.makedirs(os.path.dirname(REPORT), exist_ok=True)

lines = []
def w(s=""): lines.append(s)

w(f"# Diagnóstico Zotero — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
w()
w(f"**Fonte**: `{BAK_DB}` (lido em modo read-only)  ")
w(f"**Timestamp do .bak**: {bak_mtime}")
w()

w("## 1. Visão geral")
w()
w(f"- **Itens bibliográficos** (excl. anexos/notas/lixeira): **{n_items_bib:,}**")
w(f"- **Anexos**: **{n_attach:,}**")
w(f"- **Notas**: **{n_notes:,}**")
w(f"- **Itens na lixeira**: **{n_trash:,}**")
w(f"- **Coleções**: **{n_colls:,}**")
w(f"- **Tags distintas**: **{n_tags:,}**")
w()
w("### Distribuição por tipo de item")
w()
w("| Tipo | Quantidade |")
w("|------|-----------:|")
for r in type_dist:
    w(f"| {r['typeName']} | {r['n']:,} |")
w()

w("## 2. Top-level (raiz da biblioteca)")
w()
w("| Coleção | Itens diretos | Subpastas |")
w("|---------|---------------:|----------:|")
for r in root_colls:
    w(f"| {r['collectionName']} | {r['n_items']:,} | {r['n_subs']} |")
w()

w("## 3. Metadados incompletos")
w()
w("| Problema | Itens afetados |")
w("|----------|---------------:|")
w(f"| Sem título | {n_no_title} |")
w(f"| Sem nenhum autor/creator | {n_no_creator} |")
w(f"| Sem data/ano | {n_no_date} |")
w(f"| Artigos sem `publicationTitle` | {n_art_no_pub} |")
w(f"| Artigos sem DOI | {n_art_no_doi} |")
w(f"| Livros sem ISBN | {n_book_no_isbn} |")
w(f"| Livros sem editora | {n_book_no_publisher} |")
w(f"| Sem resumo (abstractNote) | {n_no_abs} |")
w()

w("## 4. Duplicatas")
w()
w(f"- **Grupos por DOI**: {len(doi_dups)}")
w(f"- **Grupos por ISBN**: {len(isbn_dups)}")
w(f"- **Grupos por título+ano**: {len(ty_dups)}")
w()
if doi_dups:
    w("### Top 10 grupos por DOI (mais cópias)")
    w()
    w("| DOI | # cópias | itemIDs |")
    w("|-----|---------:|---------|")
    for doi, ids in sorted(doi_dups.items(), key=lambda x: -len(x[1]))[:10]:
        w(f"| `{doi}` | {len(ids)} | {','.join(map(str,ids))} |")
    w()
if isbn_dups:
    w("### Top 10 grupos por ISBN")
    w()
    w("| ISBN | # cópias | itemIDs |")
    w("|------|---------:|---------|")
    for isbn, ids in sorted(isbn_dups.items(), key=lambda x: -len(x[1]))[:10]:
        w(f"| `{isbn}` | {len(ids)} | {','.join(map(str,ids))} |")
    w()

w("## 5. Anexos")
w()
w(f"- **Itens sem nenhum anexo**: {n_items_no_att}")
w(f"- **Anexos órfãos** (sem item-pai): {n_orphan_att}")
w()
w("| contentType | n |")
w("|-------------|---:|")
for r in content_types:
    ct = r["ct"] or "_(vazio)_"
    w(f"| {ct} | {r['n']:,} |")
w()

w("## 6. Coleções")
w()
w(f"- **Itens fora de qualquer coleção** (\"Unfiled\"): {n_unfiled}")
w(f"- **Coleções vazias**: {len(empty_colls)}")
w()
w("### Top 15 por tamanho")
w("| Coleção | Itens |")
w("|---------|------:|")
for r in top_colls:
    w(f"| {r['collectionName']} | {r['n']:,} |")
w()

w("## 7. Tags")
w()
w(f"- **Tags usadas 1x ou menos**: {n_tag_once}")
w(f"- **Tags com variantes de caixa**: {len(case_variants)}")
w(f"- **Tags com namespace `prefixo:`** (do nosso vocabulário): {len(namespace_tags)}")
w()
if case_variants:
    w("### Variantes de caixa")
    w("| Forma normalizada | Variantes |")
    w("|-------------------|-----------|")
    for k, vs in sorted(case_variants.items()):
        w(f"| `{k}` | {' / '.join(f'`{x}`' for x in vs)} |")
    w()
w("### Top 25 tags")
w("| Tag | n |")
w("|-----|---:|")
for name, n in top_tags:
    w(f"| {name} | {n} |")
w()
if namespace_tags:
    w("### Tags com namespace (vocabulário novo)")
    w("| Tag | n |")
    w("|-----|---:|")
    for n, c in sorted(namespace_tags, key=lambda x: -x[1]):
        w(f"| {n} | {c} |")
    w()

w("## 8. Resumo executivo (comparar com baseline 09/05/2026)")
w()
w("| Categoria | 09/05/2026 (baseline) | Atual |")
w("|-----------|----------------------:|------:|")
w(f"| Itens bibliográficos | 2,337 | {n_items_bib:,} |")
w(f"| Anexos | 2,417 | {n_attach:,} |")
w(f"| Notas | 525 | {n_notes:,} |")
w(f"| Coleções | 186 | {n_colls:,} |")
w(f"| Tags | 578 | {n_tags:,} |")
w(f"| Duplicatas DOI | 59 | {len(doi_dups)} |")
w(f"| Duplicatas ISBN | 43 | {len(isbn_dups)} |")
w(f"| Duplicatas título+ano | 99 | {len(ty_dups)} |")
w(f"| Sem autor | 288 | {n_no_creator} |")
w(f"| Sem ano | 345 | {n_no_date} |")
w(f"| Sem título | 3 | {n_no_title} |")
w(f"| Artigos sem DOI | 274 | {n_art_no_doi} |")
w(f"| Livros sem ISBN | 98 | {n_book_no_isbn} |")
w(f"| Itens sem anexo | 398 | {n_items_no_att} |")
w(f"| Anexos órfãos | 241 | {n_orphan_att} |")
w(f"| Itens fora de coleção | 157 | {n_unfiled} |")
w(f"| Coleções vazias | 16 | {len(empty_colls)} |")
w(f"| Tags com variantes de caixa | 14 | {len(case_variants)} |")
w(f"| Tags <=1x | 476 | {n_tag_once} |")

with open(REPORT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"[2] Relatório: {REPORT}")
print(f"    {len(lines)} linhas")

print()
print("=== RESUMO RÁPIDO ===")
print(f"Itens biblio: {n_items_bib}  Anexos: {n_attach}  Notas: {n_notes}  Lixeira: {n_trash}")
print(f"Coleções: {n_colls} (vazias: {len(empty_colls)})  Tags: {n_tags}  Tags<=1x: {n_tag_once}  Variantes caixa: {len(case_variants)}")
print(f"Sem título: {n_no_title}  Sem autor: {n_no_creator}  Sem data: {n_no_date}")
print(f"Dups DOI: {len(doi_dups)}  Dups ISBN: {len(isbn_dups)}  Dups título+ano: {len(ty_dups)}")
print(f"Anexos órfãos: {n_orphan_att}  Itens sem anexo: {n_items_no_att}  Sem coleção: {n_unfiled}")
print(f"Tags com namespace: {len(namespace_tags)}")
con.close()
