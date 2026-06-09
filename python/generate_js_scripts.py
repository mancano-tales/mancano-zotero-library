"""
generate_js_scripts.py — gera scripts J/K/L em scripts/ a partir dos JSONs
de classify_problematic.py.

Lê:
  diagnostics/<YYYY-MM-DD>_balde_A.json
  diagnostics/<YYYY-MM-DD>_balde_B.json
  diagnostics/<YYYY-MM-DD>_balde_C.json

Escreve:
  scripts/J_problematic_enrich.js
  scripts/K_problematic_trash.js
  scripts/L_problematic_inst_creator.js

Cada script tem header padronizado (Data, Status, Output esperado).
Para regerar após nova triagem:
    1) rodar classify_problematic.py
    2) rodar este script com a mesma data:
        python generate_js_scripts.py 2026-05-30

NB: os scripts em scripts/ JÁ EXISTEM com header e Status=EXECUTADO.
    Este script REGENERA-os; rodar de novo só faz sentido se a triagem mudou
    (mas aí o Status passa de EXECUTADO de volta a PENDENTE — atenção!).
"""
import json, os, sys
from datetime import datetime

PROJECT_ROOT = r"C:\Users\Mancano\Documents\MancanoSync\mancano-zotero-library"
REPORT_DATE = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
INDIR = os.path.join(PROJECT_ROOT, "diagnostics")
OUTDIR = os.path.join(PROJECT_ROOT, "scripts")

def load(name):
    with open(os.path.join(INDIR, f"{REPORT_DATE}_{name}"), encoding="utf-8") as f: return json.load(f)
A = load("balde_A.json"); B = load("balde_B.json"); C = load("balde_C.json")

# ===== templates dos scripts =====
HEADER_J = """// Script J — Enriquecer metadados via DOI (CrossRef) / ISBN (OpenLibrary)
// Data de criação: __DATE__
// Data de execução: __DATE__
// Status: PENDENTE (regere e re-execute se a triagem mudou)
// Output esperado: ~__N__ tentativas; preencher só campos vazios.
//
// Contexto:
//   Fase 0.5 — coleção "Problematic - No author". Balde A da triagem.
//   Para cada item: DOI → CrossRef, ISBN → OpenLibrary. setIfEmpty() nunca sobrescreve.
"""

JS_A_BODY = r"""
const ITEMS = __ITEMS__;
const out = [];

async function fetchCrossref(doi) {
  const r = await fetch(`https://api.crossref.org/works/${encodeURIComponent(doi)}`, {
    headers: {"User-Agent": "Mancano-Zotero-cleanup/1.0 (mailto:talesmanz01@gmail.com)"}
  });
  if (!r.ok) throw new Error(`CrossRef ${r.status}`);
  return (await r.json()).message;
}
async function fetchOpenLibrary(isbn) {
  const key = `ISBN:${isbn.replace(/[^0-9Xx]/g,'')}`;
  const r = await fetch(`https://openlibrary.org/api/books?bibkeys=${encodeURIComponent(key)}&format=json&jscmd=data`);
  if (!r.ok) throw new Error(`OpenLibrary ${r.status}`);
  return (await r.json())[key];
}
function setIfEmpty(item, field, value) {
  if (!value) return false;
  try {
    const cur = item.getField(field);
    if (cur && String(cur).trim() !== "") return false;
    item.setField(field, String(value));
    return true;
  } catch(e) { return false; }
}
async function enrichDOI(item, doi) {
  const m = await fetchCrossref(doi);
  let touched = [];
  if (m.title && m.title[0] && setIfEmpty(item, "title", m.title[0])) touched.push("title");
  if (m["container-title"] && m["container-title"][0] && setIfEmpty(item, "publicationTitle", m["container-title"][0])) touched.push("publicationTitle");
  if (m.publisher && setIfEmpty(item, "publisher", m.publisher)) touched.push("publisher");
  if (m.volume && setIfEmpty(item, "volume", m.volume)) touched.push("volume");
  if (m.issue && setIfEmpty(item, "issue", m.issue)) touched.push("issue");
  if (m.page && setIfEmpty(item, "pages", m.page)) touched.push("pages");
  if (m.abstract && setIfEmpty(item, "abstractNote", m.abstract.replace(/<[^>]+>/g,""))) touched.push("abstractNote");
  const dp = m["published-print"] || m["published-online"] || m["issued"];
  if (dp && dp["date-parts"] && dp["date-parts"][0]) {
    const date = dp["date-parts"][0].join("-");
    if (setIfEmpty(item, "date", date)) touched.push("date");
  }
  if (item.getCreators().length === 0 && m.author) {
    const creators = m.author.map(a => ({firstName: a.given || "", lastName: a.family || a.name || "", creatorType: "author"})).filter(c => c.firstName || c.lastName);
    if (creators.length) { item.setCreators(creators); touched.push(`creators(${creators.length})`); }
  }
  return touched;
}
async function enrichISBN(item, isbn) {
  const data = await fetchOpenLibrary(isbn);
  if (!data) return [];
  let touched = [];
  if (data.title && setIfEmpty(item, "title", data.title)) touched.push("title");
  if (data.publish_date && setIfEmpty(item, "date", data.publish_date)) touched.push("date");
  if (data.publishers && data.publishers[0] && setIfEmpty(item, "publisher", data.publishers[0].name)) touched.push("publisher");
  if (data.publish_places && data.publish_places[0] && setIfEmpty(item, "place", data.publish_places[0].name)) touched.push("place");
  if (data.number_of_pages && setIfEmpty(item, "numPages", String(data.number_of_pages))) touched.push("numPages");
  if (data.notes && setIfEmpty(item, "abstractNote", data.notes)) touched.push("abstractNote");
  if (item.getCreators().length === 0 && data.authors) {
    const creators = data.authors.map(a => {
      const name = a.name || ""; const parts = name.trim().split(/\s+/);
      const last = parts.pop() || ""; const first = parts.join(" ");
      return { firstName: first, lastName: last, creatorType: "author" };
    }).filter(c => c.firstName || c.lastName);
    if (creators.length) { item.setCreators(creators); touched.push(`creators(${creators.length})`); }
  }
  return touched;
}

const total = ITEMS.length;
let ok = 0, fail = 0;
out.push(`=== BALDE A: enrich ${total} itens ===`);
for (let i = 0; i < ITEMS.length; i++) {
  const spec = ITEMS[i];
  try {
    const item = await Zotero.Items.getAsync(spec.id);
    if (!item) { out.push(`[${spec.id}] NÃO ENCONTRADO`); fail++; continue; }
    let touched = [];
    if (spec.action === "enrich_via_doi") touched = await enrichDOI(item, spec.lookup_key);
    else if (spec.action === "enrich_via_isbn") touched = await enrichISBN(item, spec.lookup_key);
    if (touched.length) { await item.saveTx(); out.push(`[${spec.id}] ✓ ${touched.join(", ")}`); ok++; }
    else out.push(`[${spec.id}] — nada a preencher`);
  } catch (e) {
    out.push(`[${spec.id}] ✗ ERRO: ${e.message || e}`); fail++;
  }
  if ((i+1) % 10 === 0) await Zotero.Promise.delay(1000);
  else await Zotero.Promise.delay(250);
}
out.push(`=== Resultado: ${ok} enriquecidos, ${fail} falhas, ${total-ok-fail} sem mudança ===`);
return out.join("\n");
"""

HEADER_K = """// Script K — Mover blogs ABNT/TCC de baixa qualidade para lixeira
// Data de criação: __DATE__
// Data de execução: __DATE__
// Status: PENDENTE
// Output esperado: __N__ itens movidos para a lixeira (reversível 30 dias).
//
// Contexto: Fase 0.5. Balde B (lixo de baixa qualidade).
"""

JS_B_BODY = r"""
const IDS = __IDS__;
const TITLES = __TITLES__;
let log = ["=== BALDE B — candidatos a lixeira ==="];
for (let i = 0; i < IDS.length; i++) log.push(`  [${IDS[i]}] ${TITLES[i]}`);
log.push(`Total: ${IDS.length} itens.`);
log.push("\nEstes itens vão para a LIXEIRA (reversível 30 dias).");
const proceed = confirm(log.join("\n") + "\n\nMover esses " + IDS.length + " itens para a lixeira?");
if (!proceed) return "Cancelado pelo usuário.";
await Zotero.Items.trashTx(IDS);
return `✓ ${IDS.length} itens movidos para a lixeira.`;
"""

HEADER_L = """// Script L — Atribuir creator institucional (fieldMode=1) a anônimos legítimos
// Data de criação: __DATE__
// Data de execução: __DATE__
// Status: PENDENTE
// Output esperado: __N__ tentativas (atribuir creator institucional).
//
// Contexto: Fase 0.5. Balde C (anônimos legítimos com URL conhecida).
// fieldMode=1 = single-field "name only" (CSL trata como corporate author).
"""

JS_C_BODY = r"""
const SPECS = __SPECS__;
const out = ["=== BALDE C — atribuir creator institucional ==="];
let ok = 0, skip = 0, fail = 0, review = 0;
for (const spec of SPECS) {
  try {
    const item = await Zotero.Items.getAsync(spec.id);
    if (!item) { out.push(`[${spec.id}] NÃO ENCONTRADO`); fail++; continue; }
    if (item.getCreators().length > 0) { out.push(`[${spec.id}] ⊘ já tem creator, pulei`); skip++; continue; }
    if (spec.proposed_creator === "?" || spec.needs_review) {
      out.push(`[${spec.id}] 🔍 REVISAR — ${spec.title}`); review++; continue;
    }
    item.setCreators([{name: spec.proposed_creator, creatorType: "author", fieldMode: 1}]);
    await item.saveTx();
    out.push(`[${spec.id}] ✓ ${spec.proposed_creator}`); ok++;
  } catch (e) { out.push(`[${spec.id}] ✗ ERRO: ${e.message || e}`); fail++; }
}
out.push(`=== Resultado: ${ok} atribuídos, ${skip} pulados (já tinham creator), ${review} precisam revisão manual, ${fail} falhas ===`);
return out.join("\n");
"""

def write(name, content):
    p = os.path.join(OUTDIR, name)
    with open(p, "w", encoding="utf-8") as f: f.write(content)
    print(f"  {p}  ({len(content)} chars)")

os.makedirs(OUTDIR, exist_ok=True)

# J
items_a = [{"id": x["id"], "action": x["action"], "lookup_key": x["lookup_key"]} for x in A]
js_j = HEADER_J.replace("__DATE__", REPORT_DATE).replace("__N__", str(len(items_a))) \
       + JS_A_BODY.replace("__ITEMS__", json.dumps(items_a, ensure_ascii=False))
write("J_problematic_enrich.js", js_j)

# K
ids = [x["id"] for x in B]
titles = [f"[{x['type']}] {x['title']}" for x in B]
js_k = HEADER_K.replace("__DATE__", REPORT_DATE).replace("__N__", str(len(ids))) \
       + JS_B_BODY.replace("__IDS__", json.dumps(ids)).replace("__TITLES__", json.dumps(titles, ensure_ascii=False))
write("K_problematic_trash.js", js_k)

# L
specs_c = [{"id": x["id"], "title": x["title"][:80], "proposed_creator": x["proposed_creator"],
            "needs_review": x.get("needs_review", False)} for x in C]
js_l = HEADER_L.replace("__DATE__", REPORT_DATE).replace("__N__", str(len(specs_c))) \
       + JS_C_BODY.replace("__SPECS__", json.dumps(specs_c, ensure_ascii=False))
write("L_problematic_inst_creator.js", js_l)

print(f"\nPronto. {len(items_a)} no A, {len(B)} no B, {len(specs_c)} no C.")
