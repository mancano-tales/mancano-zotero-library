"""
Diagnóstico read-only da biblioteca Zotero.
Lê uma cópia .bak e gera relatorio_zotero.md
"""
import sqlite3
import sys
import os
from collections import Counter, defaultdict

DB = os.path.join(os.path.dirname(__file__), "zotero_readonly.sqlite")
OUT = os.path.join(os.path.dirname(__file__), "relatorio_zotero.md")

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()

def q(sql, params=()):
    return cur.execute(sql, params).fetchall()

def q1(sql, params=()):
    r = cur.execute(sql, params).fetchone()
    return r[0] if r else None

lines = []
def w(s=""):
    lines.append(s)

w("# Diagnóstico da Biblioteca Zotero")
w(f"\nBanco analisado: `{DB}`  ")
w("(cópia read-only de `zotero.sqlite.bak` — biblioteca ativa NÃO foi tocada)\n")

# ---------- 1. VISÃO GERAL ----------
w("## 1. Visão geral\n")

total_items = q1("""
    SELECT COUNT(*) FROM items i
    WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
      AND i.itemTypeID NOT IN (SELECT itemTypeID FROM itemTypes WHERE typeName IN ('attachment','note','annotation'))
""")
total_attachments = q1("SELECT COUNT(*) FROM itemAttachments WHERE itemID NOT IN (SELECT itemID FROM deletedItems)")
total_notes = q1("""SELECT COUNT(*) FROM items WHERE itemTypeID = (SELECT itemTypeID FROM itemTypes WHERE typeName='note')
                    AND itemID NOT IN (SELECT itemID FROM deletedItems)""")
total_trash = q1("SELECT COUNT(*) FROM deletedItems")
total_collections = q1("SELECT COUNT(*) FROM collections")
total_tags = q1("SELECT COUNT(*) FROM tags")

w(f"- **Itens bibliográficos** (excl. anexos/notas/lixeira): **{total_items:,}**")
w(f"- **Anexos** (PDFs, links, etc.): **{total_attachments:,}**")
w(f"- **Notas**: **{total_notes:,}**")
w(f"- **Itens na lixeira**: **{total_trash:,}**")
w(f"- **Coleções**: **{total_collections:,}**")
w(f"- **Tags distintas**: **{total_tags:,}**")
w()

# Por tipo
w("### Distribuição por tipo de item\n")
w("| Tipo | Quantidade |")
w("|------|-----------:|")
rows = q("""
    SELECT it.typeName, COUNT(*) as n
    FROM items i JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
    WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
      AND it.typeName NOT IN ('attachment','note','annotation')
    GROUP BY it.typeName ORDER BY n DESC
""")
for r in rows:
    w(f"| {r['typeName']} | {r['n']:,} |")
w()

# ---------- 2. METADADOS INCOMPLETOS ----------
w("## 2. Metadados incompletos\n")

# Helper: pegar fieldID por nome
def fid(name):
    return q1("SELECT fieldID FROM fields WHERE fieldName = ?", (name,))

FID_TITLE = fid("title")
FID_DATE = fid("date")
FID_DOI = fid("DOI")
FID_ISBN = fid("ISBN")
FID_PUB_TITLE = fid("publicationTitle")
FID_PUBLISHER = fid("publisher")
FID_ABSTRACT = fid("abstractNote")

# Itens sem título
no_title = q1(f"""
    SELECT COUNT(*) FROM items i
    WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
      AND i.itemTypeID NOT IN (SELECT itemTypeID FROM itemTypes WHERE typeName IN ('attachment','note','annotation'))
      AND i.itemID NOT IN (SELECT itemID FROM itemData WHERE fieldID = {FID_TITLE})
""")

# Itens sem autor (qualquer creator)
no_author = q1("""
    SELECT COUNT(*) FROM items i
    WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
      AND i.itemTypeID NOT IN (SELECT itemTypeID FROM itemTypes WHERE typeName IN ('attachment','note','annotation'))
      AND i.itemID NOT IN (SELECT itemID FROM itemCreators)
""")

# Itens sem ano
no_date = q1(f"""
    SELECT COUNT(*) FROM items i
    WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
      AND i.itemTypeID NOT IN (SELECT itemTypeID FROM itemTypes WHERE typeName IN ('attachment','note','annotation'))
      AND i.itemID NOT IN (SELECT itemID FROM itemData WHERE fieldID = {FID_DATE})
""")

# Artigos sem journal (publicationTitle)
no_pub = q1(f"""
    SELECT COUNT(*) FROM items i
    WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
      AND i.itemTypeID = (SELECT itemTypeID FROM itemTypes WHERE typeName='journalArticle')
      AND i.itemID NOT IN (SELECT itemID FROM itemData WHERE fieldID = {FID_PUB_TITLE})
""")

# Artigos sem DOI
no_doi_articles = q1(f"""
    SELECT COUNT(*) FROM items i
    WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
      AND i.itemTypeID = (SELECT itemTypeID FROM itemTypes WHERE typeName='journalArticle')
      AND i.itemID NOT IN (SELECT itemID FROM itemData WHERE fieldID = {FID_DOI})
""")

# Livros sem ISBN
no_isbn_books = q1(f"""
    SELECT COUNT(*) FROM items i
    WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
      AND i.itemTypeID = (SELECT itemTypeID FROM itemTypes WHERE typeName='book')
      AND i.itemID NOT IN (SELECT itemID FROM itemData WHERE fieldID = {FID_ISBN})
""")

# Livros sem editora
no_pub_books = q1(f"""
    SELECT COUNT(*) FROM items i
    WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
      AND i.itemTypeID = (SELECT itemTypeID FROM itemTypes WHERE typeName='book')
      AND i.itemID NOT IN (SELECT itemID FROM itemData WHERE fieldID = {FID_PUBLISHER})
""")

# Sem abstract
no_abs = q1(f"""
    SELECT COUNT(*) FROM items i
    WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
      AND i.itemTypeID NOT IN (SELECT itemTypeID FROM itemTypes WHERE typeName IN ('attachment','note','annotation'))
      AND i.itemID NOT IN (SELECT itemID FROM itemData WHERE fieldID = {FID_ABSTRACT})
""")

w("| Problema | Itens afetados |")
w("|----------|---------------:|")
w(f"| Sem título | {no_title:,} |")
w(f"| Sem nenhum autor/creator | {no_author:,} |")
w(f"| Sem data/ano | {no_date:,} |")
w(f"| Artigos sem `publicationTitle` (journal) | {no_pub:,} |")
w(f"| Artigos sem DOI | {no_doi_articles:,} |")
w(f"| Livros sem ISBN | {no_isbn_books:,} |")
w(f"| Livros sem editora | {no_pub_books:,} |")
w(f"| Sem resumo (abstractNote) | {no_abs:,} |")
w()

# ---------- 3. DUPLICATAS ----------
w("## 3. Duplicatas suspeitas\n")

# Por DOI
dup_doi = q(f"""
    SELECT idv.value as doi, COUNT(*) as n, GROUP_CONCAT(i.itemID) as ids
    FROM itemData id
    JOIN itemDataValues idv ON id.valueID = idv.valueID
    JOIN items i ON id.itemID = i.itemID
    WHERE id.fieldID = {FID_DOI}
      AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
    GROUP BY LOWER(TRIM(idv.value))
    HAVING n > 1
    ORDER BY n DESC
""")
w(f"### Por DOI: **{len(dup_doi)}** grupos duplicados\n")
if dup_doi:
    w("| DOI | # cópias | itemIDs |")
    w("|-----|---------:|---------|")
    for r in dup_doi[:20]:
        w(f"| `{r['doi']}` | {r['n']} | {r['ids']} |")
    if len(dup_doi) > 20:
        w(f"\n_…e mais {len(dup_doi)-20} grupos_\n")

# Por ISBN
dup_isbn = q(f"""
    SELECT idv.value as isbn, COUNT(*) as n, GROUP_CONCAT(i.itemID) as ids
    FROM itemData id
    JOIN itemDataValues idv ON id.valueID = idv.valueID
    JOIN items i ON id.itemID = i.itemID
    WHERE id.fieldID = {FID_ISBN}
      AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
    GROUP BY REPLACE(REPLACE(LOWER(TRIM(idv.value)),'-',''),' ','')
    HAVING n > 1
    ORDER BY n DESC
""")
w(f"\n### Por ISBN: **{len(dup_isbn)}** grupos duplicados\n")
if dup_isbn:
    w("| ISBN | # cópias | itemIDs |")
    w("|------|---------:|---------|")
    for r in dup_isbn[:20]:
        w(f"| `{r['isbn']}` | {r['n']} | {r['ids']} |")
    if len(dup_isbn) > 20:
        w(f"\n_…e mais {len(dup_isbn)-20} grupos_\n")

# Por título normalizado + ano
dup_title = q(f"""
    SELECT
        LOWER(TRIM(idv_t.value)) as titulo_norm,
        SUBSTR(idv_d.value, 1, 4) as ano,
        COUNT(*) as n,
        GROUP_CONCAT(i.itemID) as ids,
        GROUP_CONCAT(SUBSTR(idv_t.value,1,80), ' || ') as titulos
    FROM items i
    JOIN itemData id_t ON i.itemID = id_t.itemID AND id_t.fieldID = {FID_TITLE}
    JOIN itemDataValues idv_t ON id_t.valueID = idv_t.valueID
    LEFT JOIN itemData id_d ON i.itemID = id_d.itemID AND id_d.fieldID = {FID_DATE}
    LEFT JOIN itemDataValues idv_d ON id_d.valueID = idv_d.valueID
    WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
      AND i.itemTypeID NOT IN (SELECT itemTypeID FROM itemTypes WHERE typeName IN ('attachment','note','annotation'))
    GROUP BY LOWER(TRIM(idv_t.value)), SUBSTR(idv_d.value,1,4)
    HAVING n > 1
    ORDER BY n DESC
""")
w(f"\n### Por título+ano normalizados: **{len(dup_title)}** grupos\n")
if dup_title:
    w("| Título (truncado) | Ano | # cópias | itemIDs |")
    w("|-------------------|-----|---------:|---------|")
    for r in dup_title[:30]:
        t = (r['titulo_norm'] or '')[:80].replace('|','/')
        w(f"| {t} | {r['ano'] or '?'} | {r['n']} | {r['ids']} |")
    if len(dup_title) > 30:
        w(f"\n_…e mais {len(dup_title)-30} grupos_\n")

w()

# ---------- 4. ANEXOS / PDFs ----------
w("## 4. Anexos e PDFs\n")

# Itens regulares sem nenhum anexo
items_no_attach = q1("""
    SELECT COUNT(*) FROM items i
    WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
      AND i.itemTypeID NOT IN (SELECT itemTypeID FROM itemTypes WHERE typeName IN ('attachment','note','annotation'))
      AND i.itemID NOT IN (SELECT parentItemID FROM itemAttachments WHERE parentItemID IS NOT NULL)
""")

# Anexos órfãos (sem parent)
orphan_attach = q1("""
    SELECT COUNT(*) FROM itemAttachments
    WHERE parentItemID IS NULL
      AND itemID NOT IN (SELECT itemID FROM deletedItems)
""")

# Tipos de anexo
attach_types = q("""
    SELECT contentType, COUNT(*) as n
    FROM itemAttachments
    WHERE itemID NOT IN (SELECT itemID FROM deletedItems)
    GROUP BY contentType ORDER BY n DESC
""")

w(f"- **Itens sem nenhum anexo**: {items_no_attach:,}")
w(f"- **Anexos órfãos** (sem item-pai): {orphan_attach:,}\n")
w("### Tipos de anexo\n")
w("| contentType | n |")
w("|-------------|---:|")
for r in attach_types[:15]:
    w(f"| {r['contentType'] or '_(vazio)_'} | {r['n']:,} |")
w()

# ---------- 5. COLEÇÕES ----------
w("## 5. Coleções\n")
items_no_collection = q1("""
    SELECT COUNT(*) FROM items i
    WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
      AND i.itemTypeID NOT IN (SELECT itemTypeID FROM itemTypes WHERE typeName IN ('attachment','note','annotation'))
      AND i.itemID NOT IN (SELECT itemID FROM collectionItems)
""")
w(f"- **Itens fora de qualquer coleção**: {items_no_collection:,}\n")

# Top coleções por tamanho
col_sizes = q("""
    SELECT c.collectionName, COUNT(ci.itemID) as n
    FROM collections c LEFT JOIN collectionItems ci ON c.collectionID = ci.collectionID
    GROUP BY c.collectionID ORDER BY n DESC LIMIT 15
""")
w("### Top 15 coleções por tamanho\n")
w("| Coleção | Itens |")
w("|---------|------:|")
for r in col_sizes:
    w(f"| {r['collectionName']} | {r['n']:,} |")
w()

# Coleções vazias
empty_cols = q("""
    SELECT collectionName FROM collections
    WHERE collectionID NOT IN (SELECT collectionID FROM collectionItems)
""")
w(f"### Coleções vazias: **{len(empty_cols)}**\n")
if empty_cols and len(empty_cols) <= 30:
    for r in empty_cols:
        w(f"- {r['collectionName']}")
    w()

# ---------- 6. TAGS ----------
w("## 6. Tags\n")
tags_once = q("""
    SELECT t.name, COUNT(it.itemID) as n
    FROM tags t LEFT JOIN itemTags it ON t.tagID = it.tagID
    GROUP BY t.tagID HAVING n <= 1 ORDER BY t.name
""")
w(f"- **Tags usadas 1x ou menos**: {len(tags_once)}\n")

# Tags potencialmente duplicadas (case-insensitive)
all_tags = q("SELECT name FROM tags")
tag_lower = defaultdict(list)
for r in all_tags:
    tag_lower[r['name'].lower().strip()].append(r['name'])
case_dups = {k: v for k, v in tag_lower.items() if len(v) > 1}
w(f"- **Tags com variantes de caixa/espaço** (mesmo lower(): diferentes originais): {len(case_dups)}\n")
if case_dups:
    w("| Forma normalizada | Variantes |")
    w("|-------------------|-----------|")
    for k, v in list(case_dups.items())[:20]:
        w(f"| `{k}` | {' / '.join(f'`{x}`' for x in v)} |")
    w()

# Top tags
top_tags = q("""
    SELECT t.name, COUNT(it.itemID) as n
    FROM tags t JOIN itemTags it ON t.tagID = it.tagID
    GROUP BY t.tagID ORDER BY n DESC LIMIT 20
""")
w("### Top 20 tags mais usadas\n")
w("| Tag | n |")
w("|-----|---:|")
for r in top_tags:
    w(f"| {r['name']} | {r['n']} |")
w()

# ---------- 7. BETTER BIBTEX ----------
w("## 7. Better BibTeX (citation keys)\n")
bbt_path = os.path.join(os.path.dirname(__file__), "..", "better-bibtex.sqlite")
bbt_path = os.path.abspath(bbt_path)
if os.path.exists(bbt_path):
    try:
        # copia leitura
        import shutil
        bbt_copy = os.path.join(os.path.dirname(__file__), "bbt_readonly.sqlite")
        shutil.copy(bbt_path, bbt_copy)
        bcon = sqlite3.connect(f"file:{bbt_copy}?mode=ro", uri=True)
        bcur = bcon.cursor()
        # Estrutura típica: tabela "citationkey" (itemID, itemKey, libraryID, citationKey, pinned)
        tables = [r[0] for r in bcur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        w(f"- Tabelas BBT: {tables}")
        if 'citationkey' in tables:
            total_keys = bcur.execute("SELECT COUNT(*) FROM citationkey").fetchone()[0]
            dup_keys = bcur.execute("""
                SELECT citationKey, COUNT(*) n FROM citationkey
                GROUP BY citationKey HAVING n>1 ORDER BY n DESC
            """).fetchall()
            w(f"- Citation keys totais: **{total_keys:,}**")
            w(f"- Citation keys duplicadas: **{len(dup_keys)}**")
            if dup_keys:
                w("\n| Key duplicada | # |")
                w("|---------------|---:|")
                for k, n in dup_keys[:15]:
                    w(f"| `{k}` | {n} |")
        bcon.close()
    except Exception as e:
        w(f"- Erro lendo BBT: {e}")
else:
    w("- Arquivo `better-bibtex.sqlite` não encontrado (talvez ainda não inicializado)")
w()

# ---------- RESUMO FINAL ----------
w("## 8. Resumo executivo\n")
issues = [
    ("Duplicatas (DOI)", len(dup_doi)),
    ("Duplicatas (ISBN)", len(dup_isbn)),
    ("Duplicatas (título+ano)", len(dup_title)),
    ("Sem autor", no_author),
    ("Sem ano", no_date),
    ("Artigos sem DOI", no_doi_articles),
    ("Livros sem ISBN", no_isbn_books),
    ("Itens sem anexo", items_no_attach),
    ("Anexos órfãos", orphan_attach),
    ("Itens fora de coleção", items_no_collection),
    ("Tags com variantes de caixa", len(case_dups)),
    ("Tags usadas <=1x", len(tags_once)),
]
w("| Categoria | Quantidade |")
w("|-----------|-----------:|")
for label, n in issues:
    w(f"| {label} | {n:,} |")
w()

con.close()

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"OK -> {OUT}")
print(f"Total de linhas: {len(lines)}")
