"""
classify_problematic.py — classifica itens da triagem em 3 baldes.

Lê o .bak em modo read-only (não toca o banco vivo) e classifica
os 114 itens em:
  A) Auto-enrichable — tem DOI/ISBN, dá pra preencher via API externa.
  B) Lixo — sites de baixa qualidade (blogs ABNT/TCC etc.) para a lixeira.
  C) Anônimo legítimo — webpage/blog/vídeo sem autor cuja autoria
     é institucional (jornal, canal, órgão de governo).
  SKIP — case/statute com caseName/nameOfAct (não é bug real).

Saídas em diagnostics/:
  <YYYY-MM-DD>_balde_A.json
  <YYYY-MM-DD>_balde_B.json
  <YYYY-MM-DD>_balde_C.json
  <YYYY-MM-DD>_balde_skip.json
  <YYYY-MM-DD>_problematic_triagem.md

Os JSONs alimentam python/generate_js_scripts.py, que gera as versões
data-aware dos scripts J/K/L em scripts/.
"""
import sqlite3, json, os, sys
from collections import defaultdict
from urllib.parse import urlparse
from datetime import datetime

BAK_DB = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(r"~/Zotero/zotero.sqlite.bak")
PROJECT_ROOT = r"C:\Users\Mancano\Documents\MancanoSync\mancano-zotero-library"
REPORT_DATE = datetime.now().strftime("%Y-%m-%d")
OUTDIR = os.path.join(PROJECT_ROOT, "diagnostics")

con = sqlite3.connect(f"file:{BAK_DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()

def q(sql, params=()): return cur.execute(sql, params).fetchall()
def q1(sql, params=()):
    r = cur.execute(sql, params).fetchone()
    return r[0] if r else None
def itemtype_id(name): return q1("SELECT itemTypeID FROM itemTypes WHERE typeName=?", (name,))
def field_id(name): return q1("SELECT fieldID FROM fields WHERE fieldName=?", (name,))

NOTE_ID, ATT_ID, ANN_ID = itemtype_id("note"), itemtype_id("attachment"), itemtype_id("annotation")
TITLE_FID = field_id("title")

# ===== mapa domínio -> creator institucional =====
DOMAIN_CREATOR = {
    # imprensa BR
    "folha.uol.com.br":          "Folha de S.Paulo",
    "www1.folha.uol.com.br":     "Folha de S.Paulo",
    "valor.globo.com":           "Valor Econômico",
    "www.valor.com.br":          "Valor Econômico",
    "g1.globo.com":              "G1",
    "economia.uol.com.br":       "UOL Economia",
    "agenciabrasil.ebc.com.br":  "Agência Brasil",
    "br.reuters.com":            "Reuters Brasil",
    "exame.com":                 "Revista Exame",
    "istoe.com.br":              "Revista IstoÉ",
    "revistamarieclaire.globo.com": "Marie Claire Brasil",
    "jornaldebrasilia.com.br":   "Jornal de Brasília",
    "jota.info":                 "JOTA",
    "www.jota.info":             "JOTA",
    "cartacampinas.com.br":      "Carta Campinas",
    "reporterbrasil.org.br":     "Repórter Brasil",
    "sul21.com.br":              "Sul21",
    "www.sul21.com.br":          "Sul21",
    "jornalistaslivres.org":     "Jornalistas Livres",
    "ocafezinho.com":            "O Cafezinho",
    "www.ocafezinho.com":        "O Cafezinho",
    "ojoioeotrigo.com.br":       "O Joio e o Trigo",

    # USP / universidades
    "jornal.usp.br":             "Jornal da USP",
    "www.fo.usp.br":             "Faculdade de Odontologia da USP",
    "www.labcidade.fau.usp.br":  "LabCidade FAU-USP",
    "www.adusp.org.br":          "ADUSP",
    "www.leginf.usp.br":         "Legislação USP",
    "www.ufabc.edu.br":          "UFABC",
    "politicalscience.mcmaster.ca": "McMaster University — Political Science",

    # governo / oficial
    "www.planalto.gov.br":       "Brasil. Presidência da República",
    "planalto.gov.br":           "Brasil. Presidência da República",
    "www12.senado.leg.br":       "Senado Federal",
    "www.fundosocial.sp.gov.br": "Fundo Social do Estado de São Paulo",

    # orgs civis / movimentos
    "ubes.org.br":               "UBES",
    "www.ubes.org.br":           "UBES",
    "une.org.br":                "UNE",
    "www.une.org.br":            "UNE",
    "levante.org.br":            "Levante Popular da Juventude",
    "fpabramo.org.br":           "Fundação Perseu Abramo",
    "racismoambiental.net.br":   "Racismo Ambiental",
    "www.monitordasdoacoes.org.br": "Monitor das Doações",
    "wribrasil.org.br":          "WRI Brasil",
    "change.org":                "Change.org",
    "www.change.org":            "Change.org",

    # Wikipedia / wikis
    "pt.wikipedia.org":          "Wikipédia",
    "en.wikipedia.org":          "Wikipedia",

    # blogs / sites
    "politize.com.br":           "Politize!",
    "www.politize.com.br":       "Politize!",
    "blogdosociofilo.com":       "Blog do Sociófilo",
    "politicalanthro.wordpress.com": "Political Anthropology Blog",

    # vídeo
    "www.youtube.com":           "YouTube",
    "youtube.com":                "YouTube",
}

# blogs ABNT/TCC de baixa qualidade — bucket B (lixo)
LOW_VALUE_DOMAINS = {
    "blog.mettzer.com", "blog.fastformat.co", "viacarreira.com",
    "projetoacademico.com.br", "tecnoblog.net", "www.normastecnicas.com",
}

# ===== helpers =====
def get_fields(item_id):
    rows = q("""
    SELECT f.fieldName, iv.value
    FROM itemData id JOIN fields f ON f.fieldID=id.fieldID
    JOIN itemDataValues iv ON iv.valueID=id.valueID
    WHERE id.itemID=?""", (item_id,))
    return {r["fieldName"]: r["value"] for r in rows}

def get_creators_count(item_id):
    return q1("SELECT COUNT(*) FROM itemCreators WHERE itemID=?", (item_id,))

def get_item_type(item_id):
    return q1("""SELECT t.typeName FROM items i JOIN itemTypes t ON t.itemTypeID=i.itemTypeID
                 WHERE i.itemID=?""", (item_id,))

def domain_of(url):
    if not url: return None
    try: return urlparse(url).netloc.lower()
    except Exception: return None

# ===== universo: coleção + sem-título =====
coll_id = q1("SELECT collectionID FROM collections WHERE collectionName='Problematic - No author'")
prob_ids = [r["itemID"] for r in q("SELECT itemID FROM collectionItems WHERE collectionID=?", (coll_id,))] if coll_id else []
no_title_ids = [r["itemID"] for r in q(f"""
SELECT i.itemID FROM items i
WHERE i.itemTypeID NOT IN ({NOTE_ID},{ATT_ID},{ANN_ID})
  AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
  AND i.itemID NOT IN (SELECT itemID FROM itemData WHERE fieldID=?)""", (TITLE_FID,))]

all_ids = sorted(set(prob_ids) | set(no_title_ids))
balde_A, balde_B, balde_C, balde_skip = [], [], [], []

for iid in all_ids:
    t = get_item_type(iid)
    f = get_fields(iid)
    title = f.get("title") or f.get("caseName") or f.get("nameOfAct") or ""
    doi = (f.get("DOI") or "").strip()
    isbn = (f.get("ISBN") or "").strip()
    url = (f.get("url") or "").strip()
    date = f.get("date") or f.get("dateDecided") or ""
    n_creators = get_creators_count(iid)
    in_prob = iid in prob_ids
    base = {"id": iid, "type": t, "title": title[:120], "date": date,
            "doi": doi, "isbn": isbn, "url": url, "publication": f.get("publicationTitle") or f.get("publisher") or "",
            "has_creator": n_creators > 0, "in_problematic_coll": in_prob}

    # case/statute legítimos
    if t in ("case", "statute") and n_creators > 0 and (f.get("caseName") or f.get("nameOfAct")):
        balde_skip.append({**base, "reason": f"{t}: usa {('caseName' if t=='case' else 'nameOfAct')}; já tem creator. Não é bug."})
        continue

    if doi:
        balde_A.append({**base, "action": "enrich_via_doi", "lookup_key": doi}); continue
    if isbn:
        balde_A.append({**base, "action": "enrich_via_isbn", "lookup_key": isbn}); continue
    if t == "book" and title:
        balde_A.append({**base, "action": "enrich_book_by_title", "lookup_key": title}); continue

    if t in ("webpage","blogPost","videoRecording","newspaperArticle","encyclopediaArticle","journalArticle","document","report"):
        d = domain_of(url)
        creator = DOMAIN_CREATOR.get(d)
        if not creator and d and "wikipedia.org" in d:
            creator = "Wikipédia" if d.startswith("pt.") else "Wikipedia"
        if not creator and d and "youtube.com" in d:
            creator = "YouTube"
        if d in LOW_VALUE_DOMAINS:
            balde_B.append({**base, "reason": f"site de baixa qualidade ({d}); recomendado deletar"}); continue
        if creator:
            balde_C.append({**base, "action": "set_inst_creator", "proposed_creator": creator}); continue
        if url:
            balde_C.append({**base, "action": "set_inst_creator_review", "proposed_creator": d or "?", "needs_review": True}); continue

    if not title and not url and not doi and not isbn:
        balde_B.append({**base, "reason": "sem título, sem URL, sem DOI/ISBN — lixo"}); continue
    balde_C.append({**base, "action": "set_inst_creator_review", "proposed_creator": "?",
                    "needs_review": True, "reason": "tem título mas sem URL/DOI/ISBN — revisar"})

# ===== persist =====
os.makedirs(OUTDIR, exist_ok=True)
def save(name, data):
    p = os.path.join(OUTDIR, f"{REPORT_DATE}_{name}")
    with open(p, "w", encoding="utf-8") as fh: json.dump(data, fh, ensure_ascii=False, indent=2)
    return p

pA = save("balde_A.json", balde_A); pB = save("balde_B.json", balde_B)
pC = save("balde_C.json", balde_C); pS = save("balde_skip.json", balde_skip)

print(f"Total inspecionado: {len(all_ids)}")
print(f"  Balde A (enrich):  {len(balde_A)}")
print(f"  Balde B (lixo):    {len(balde_B)}")
print(f"  Balde C (inst):    {len(balde_C)}")
print(f"  SKIP (não é bug):  {len(balde_skip)}")
print(f"\nJSONs: {pA}, {pB}, {pC}, {pS}")

# resumo markdown
lines = [f"# Triagem 'Problematic - No author' + sem título — {REPORT_DATE}", "",
         f"Total: **{len(all_ids)}** itens.", "",
         "## Distribuição", "",
         f"- **Balde A (enrich):** {len(balde_A)}",
         f"- **Balde B (lixo):** {len(balde_B)}",
         f"- **Balde C (creator institucional):** {len(balde_C)}",
         f"- **SKIP (não é bug — case/statute):** {len(balde_skip)}", ""]
lines += ["## SKIP — case/statute com caseName/nameOfAct", ""]
for x in balde_skip:
    lines.append(f"- `{x['id']}` [{x['type']}] {x['title']} — _{x['reason']}_")
lines += ["", "## Balde B — proposta de delete", "",
          "| id | tipo | título | URL | razão |", "|---:|------|--------|-----|-------|"]
for x in balde_B:
    lines.append(f"| {x['id']} | {x['type']} | {x['title'][:60]} | {x['url'][:60]} | {x['reason']} |")
lines += ["", "## Balde A — enrich", "",
          "| id | tipo | ação | chave | título |", "|---:|------|------|-------|--------|"]
for x in balde_A:
    lines.append(f"| {x['id']} | {x['type']} | {x['action']} | `{x['lookup_key'][:50]}` | {x['title'][:60]} |")
lines += ["", "## Balde C — creator institucional proposto", "",
          "| id | tipo | título | creator proposto | revisar? |",
          "|---:|------|--------|------------------|:--------:|"]
for x in balde_C:
    rev = "🔍" if x.get("needs_review") else ""
    lines.append(f"| {x['id']} | {x['type']} | {x['title'][:50]} | **{x['proposed_creator']}** | {rev} |")

with open(os.path.join(OUTDIR, f"{REPORT_DATE}_problematic_triagem.md"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print(f"Resumo: {os.path.join(OUTDIR, f'{REPORT_DATE}_problematic_triagem.md')}")
con.close()
