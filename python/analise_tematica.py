"""Analise tematica profunda para sugerir nova taxonomia."""
import sqlite3, os, re
from collections import Counter

DB = os.path.join(os.path.dirname(__file__), "zotero_readonly.sqlite")
OUT = os.path.join(os.path.dirname(__file__), "analise_tematica.md")
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()

def q(s, p=()): return cur.execute(s, p).fetchall()
def q1(s, p=()):
    r = cur.execute(s, p).fetchone(); return r[0] if r else None

FID_TITLE = q1("SELECT fieldID FROM fields WHERE fieldName='title'")
FID_DATE  = q1("SELECT fieldID FROM fields WHERE fieldName='date'")

lines = []
def w(s=""): lines.append(s)

# --------- 1. ARVORE COMPLETA DE COLECOES ----------
w("# Análise temática da biblioteca\n")
w("## 1. Árvore completa de coleções (com tamanho)\n")

# Buscar todas as coleções
cols = {r['collectionID']: dict(r) for r in q("""
    SELECT c.collectionID, c.collectionName, c.parentCollectionID,
           (SELECT COUNT(*) FROM collectionItems ci
            JOIN items i ON ci.itemID = i.itemID
            WHERE ci.collectionID = c.collectionID
              AND i.itemID NOT IN (SELECT itemID FROM deletedItems)) AS n_direct
    FROM collections c
""")}

# montar filhos
children = {}
for cid, c in cols.items():
    children.setdefault(c['parentCollectionID'], []).append(cid)

# ordenar filhos por nome
for k in children:
    children[k].sort(key=lambda x: cols[x]['collectionName'].lower())

# n_total = direto + descendentes
def n_total(cid):
    n = cols[cid]['n_direct']
    for ch in children.get(cid, []):
        n += n_total(ch)
    return n

w("```")
def render(cid, depth):
    c = cols[cid]
    nt = n_total(cid)
    nd = c['n_direct']
    lines.append(f"{'  '*depth}- {c['collectionName']}  [direto: {nd}, total: {nt}]")
    for ch in children.get(cid, []):
        render(ch, depth+1)
for root in children.get(None, []):
    render(root, 0)
w("```\n")

# --------- 2. TOP AUTORES ----------
w("## 2. Top 30 autores (por número de itens)\n")
w("| Autor | Itens |")
w("|-------|------:|")
for r in q("""
    SELECT cr.lastName || COALESCE(', ' || cr.firstName, '') AS author, COUNT(DISTINCT ic.itemID) AS n
    FROM creators cr JOIN itemCreators ic ON cr.creatorID = ic.creatorID
    JOIN items i ON ic.itemID = i.itemID
    WHERE i.itemID NOT IN (SELECT itemID FROM deletedItems)
    GROUP BY cr.lastName, cr.firstName
    ORDER BY n DESC LIMIT 30
"""):
    w(f"| {r['author']} | {r['n']} |")
w()

# --------- 3. DISTRIBUICAO TEMPORAL ----------
w("## 3. Distribuição temporal (década de publicação)\n")
w("| Década | Itens |")
w("|--------|------:|")
decadas = Counter()
for r in q(f"""
    SELECT idv.value AS d FROM itemData id JOIN itemDataValues idv ON id.valueID=idv.valueID
    JOIN items i ON id.itemID=i.itemID
    WHERE id.fieldID={FID_DATE} AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
"""):
    m = re.search(r'(19|20)\d{2}', r['d'] or '')
    if m:
        ano = int(m.group())
        decadas[(ano//10)*10] += 1
for dec in sorted(decadas):
    w(f"| {dec}s | {decadas[dec]} |")
w()

# --------- 4. PALAVRAS-CHAVE DE TITULOS ----------
w("## 4. Palavras e bigramas mais frequentes em títulos\n")
STOP = set("""
the a an of and or to in for on at by with from as is are was were be been being
this that these those it its their our we us their his her him she he they them
i me my your you not no nor so yet but if then than when which who whom what
de la el las los del en y o u con para por sin sobre entre sin como su sus
da do das dos no na nos nas com sem para por o a os as e ou um uma uns umas
um uma como pelo pela pelos pelas que mais menos sao sera ter teve foi sido
toward towards into through about against between among after before during
""".split())

titles = [r['t'] for r in q(f"""
    SELECT idv.value AS t FROM itemData id JOIN itemDataValues idv ON id.valueID=idv.valueID
    JOIN items i ON id.itemID=i.itemID
    WHERE id.fieldID={FID_TITLE} AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
      AND i.itemTypeID NOT IN (SELECT itemTypeID FROM itemTypes WHERE typeName IN ('attachment','note','annotation'))
""")]

def tokens(t):
    t = t.lower()
    t = re.sub(r"[^\w\sÀ-ÿ-]", " ", t)
    return [w for w in t.split() if len(w) > 2 and w not in STOP and not w.isdigit()]

uni = Counter(); bi = Counter()
for t in titles:
    toks = tokens(t)
    uni.update(toks)
    bi.update(zip(toks, toks[1:]))

w("### Top 40 unigramas\n")
w("| Termo | n |")
w("|-------|---:|")
for term, n in uni.most_common(40):
    w(f"| {term} | {n} |")
w()
w("### Top 30 bigramas\n")
w("| Termo | n |")
w("|-------|---:|")
for (a, b), n in bi.most_common(30):
    w(f"| {a} {b} | {n} |")
w()

# --------- 5. JOURNALS MAIS CITADOS ----------
w("## 5. Top 20 journals/editoras\n")
FID_PUB = q1("SELECT fieldID FROM fields WHERE fieldName='publicationTitle'")
FID_PUBLISHER = q1("SELECT fieldID FROM fields WHERE fieldName='publisher'")
w("### Journals\n| Journal | n |\n|---------|---:|")
for r in q(f"""
    SELECT idv.value AS v, COUNT(*) AS n
    FROM itemData id JOIN itemDataValues idv ON id.valueID=idv.valueID
    JOIN items i ON id.itemID=i.itemID
    WHERE id.fieldID={FID_PUB} AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
    GROUP BY LOWER(idv.value) ORDER BY n DESC LIMIT 20
"""):
    w(f"| {r['v']} | {r['n']} |")
w()
w("### Editoras (livros)\n| Editora | n |\n|---------|---:|")
for r in q(f"""
    SELECT idv.value AS v, COUNT(*) AS n
    FROM itemData id JOIN itemDataValues idv ON id.valueID=idv.valueID
    JOIN items i ON id.itemID=i.itemID
    WHERE id.fieldID={FID_PUBLISHER} AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
    GROUP BY LOWER(idv.value) ORDER BY n DESC LIMIT 20
"""):
    w(f"| {r['v']} | {r['n']} |")
w()

# --------- 6. IDIOMAS / GEOGRAFIA via tags ----------
w("## 6. Tags por categoria semântica\n")
all_tags = q("SELECT t.name, COUNT(it.itemID) n FROM tags t JOIN itemTags it ON t.tagID=it.tagID GROUP BY t.tagID HAVING n>=2 ORDER BY n DESC")
geo = []; metodo = []; campo = []; outros = []
GEO = {'brazil','brasil','united states','usa','europe','latin america','américa latina','china','africa','india','germany','france','japan','argentina','chile','méxico','mexico'}
METODO = {'methodology','método','métodos','qualitative','quantitative','case study','ethnography','survey','experiment','regression','causal inference'}
CAMPO = {'sociology','political science','economics','education','history','philosophy','sociologia','ciência política','economia','educação','história','filosofia','antropologia'}
for r in all_tags:
    nm = r['name'].lower().strip()
    if nm in GEO: geo.append((r['name'], r['n']))
    elif nm in METODO: metodo.append((r['name'], r['n']))
    elif nm in CAMPO: campo.append((r['name'], r['n']))
    else: outros.append((r['name'], r['n']))
w(f"- **Geografia identificada**: {geo}")
w(f"- **Métodos identificados**: {metodo}")
w(f"- **Campos identificados**: {campo}")
w(f"\n_(análise simples — pode haver mais escondidas em 'outros')_\n")

con.close()
with open(OUT, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines))
print(f"OK -> {OUT}  ({len(lines)} linhas)")
