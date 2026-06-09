"""
kami_fuzzy_match.py — Fase 6.2b: recupera links broken via fuzzy match.

Para cada item Zotero com link broken (categoria `truly_missing` da
investigação), tenta achar arquivo equivalente na pasta Kami Uploads por:

1. **Exact basename**: arquivo com mesmo nome em outro lugar.
2. **Basename normalizado**: tira ` 1`, ` 2`, ` (1)`, `_copy`, `_1` do nome.
3. **Title tokens**: extrai author+year+keywords do item Zotero, procura
   arquivos contendo essas palavras.
4. **difflib.get_close_matches** sobre basenames como rede de segurança.

Output:
  diagnostics/<DATE>_fuzzy_match_proposals.md   (revisão humana)
  diagnostics/<DATE>_fuzzy_match_proposals.json (executor)
  scripts/O_kami_fuzzy_repoint.js               (JS Runner pra aplicar)

Política conservadora: só sugere match de **alta confiança**. Restante vai
pra revisão manual no MD (você decide depois).

Uso: python kami_fuzzy_match.py
"""
import os, sqlite3, json, re, difflib, sys
from datetime import datetime

KAMI = r"G:\My Drive\[[1]] Kami Uploads"
PROJECT_ROOT = r"C:\Users\Mancano\Documents\MancanoSync\mancano-zotero-library"
SNAP = os.path.join(PROJECT_ROOT, "diagnostics", "zotero_snap_2026-06-06_post-script-M.sqlite")
INVEST_JSON = os.path.join(PROJECT_ROOT, "diagnostics", "2026-06-06_broken_investigation.json")
DATE = datetime.now().strftime("%Y-%m-%d")
OUT_MD   = os.path.join(PROJECT_ROOT, "diagnostics", f"{DATE}_fuzzy_match_proposals.md")
OUT_JSON = os.path.join(PROJECT_ROOT, "diagnostics", f"{DATE}_fuzzy_match_proposals.json")
SCRIPT_O = os.path.join(PROJECT_ROOT, "scripts", "O_kami_fuzzy_repoint.js")

SKIP_DIRS_EXACT = {".obsidian"}
SKIP_DIRS_PREFIX = ("_TRASH_dedup_",)

# ----------------------------------------------------------------------------
# 1. Carrega lista de truly_missing
# ----------------------------------------------------------------------------
with open(INVEST_JSON, encoding="utf-8") as f:
    inv = json.load(f)
missing = [x for x in inv["results"] if x["status"] == "truly_missing"]
print(f"[1] {len(missing)} items truly_missing pra recuperar")

# ----------------------------------------------------------------------------
# 2. Enriquece com metadados do Zotero (título, autores, ano)
# ----------------------------------------------------------------------------
con = sqlite3.connect(f"file:{SNAP}?mode=ro", uri=True); con.row_factory = sqlite3.Row
def fields(itemID):
    return {r["fieldName"]: r["value"] for r in con.execute("""
      SELECT f.fieldName, iv.value
      FROM itemData id JOIN fields f ON f.fieldID=id.fieldID
      JOIN itemDataValues iv ON iv.valueID=id.valueID
      WHERE id.itemID=?""", (itemID,))}

def creators(itemID):
    rows = list(con.execute("""
      SELECT c.lastName, c.firstName FROM itemCreators ic
      JOIN creators c ON c.creatorID=ic.creatorID
      WHERE ic.itemID=? ORDER BY ic.orderIndex""", (itemID,)))
    return [(r["lastName"], r["firstName"]) for r in rows]

def parent_meta(itemID):
    # se for um attachment, busca metadados do PAI
    parent = con.execute("SELECT parentItemID FROM itemAttachments WHERE itemID=?", (itemID,)).fetchone()
    if parent and parent["parentItemID"]:
        return fields(parent["parentItemID"]), creators(parent["parentItemID"])
    return fields(itemID), creators(itemID)

# ----------------------------------------------------------------------------
# 3. Walk filesystem pra catálogo de basenames
# ----------------------------------------------------------------------------
print("[2] Indexando filesystem (excluindo TRASH e .obsidian)...")
all_files = []  # list of {abs_path, name, name_lower, name_norm}
def normalize_name(n):
    """Tira sufixos de cópia comuns."""
    n = n.lower()
    n = re.sub(r'\s+\(\d+\)(?=\.[a-z0-9]+$)', '', n)   # ' (1).pdf'
    n = re.sub(r'\s+\d+(?=\.[a-z0-9]+$)', '', n)       # ' 1.pdf'
    n = re.sub(r'[_-]copy\d*(?=\.[a-z0-9]+$)', '', n)  # '_copy.pdf'
    n = re.sub(r'[_-]\d+(?=\.[a-z0-9]+$)', '', n)      # '_1.pdf'
    return n

for root, dirs, names in os.walk(KAMI):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS_EXACT
               and not any(d.startswith(p) for p in SKIP_DIRS_PREFIX)]
    for n in names:
        all_files.append({"abs": os.path.join(root, n), "name": n,
                          "name_lower": n.lower(), "name_norm": normalize_name(n)})
print(f"    {len(all_files)} arquivos indexados")

# index por name_lower e name_norm pra lookup O(1)
by_lower = {}
by_norm = {}
all_lowers = []
for f in all_files:
    by_lower.setdefault(f["name_lower"], []).append(f)
    by_norm.setdefault(f["name_norm"], []).append(f)
    all_lowers.append(f["name_lower"])

# ----------------------------------------------------------------------------
# 4. Tenta match pra cada item
# ----------------------------------------------------------------------------
def find_match(item):
    """Retorna (match_file, confidence_level) ou (None, None)."""
    z_basename = item["basename"]  # ex: 'paper.pdf'

    # Strategy 1: exact basename match
    if z_basename in by_lower:
        cands = by_lower[z_basename]
        if len(cands) == 1: return (cands[0], "exact")
        # multiple — escolhe o que está mais raso na hierarquia
        cands.sort(key=lambda c: c["abs"].count(os.sep))
        return (cands[0], "exact_multi")

    # Strategy 2: normalized basename
    z_norm = normalize_name(z_basename)
    if z_norm in by_norm:
        cands = by_norm[z_norm]
        if len(cands) >= 1:
            cands.sort(key=lambda c: c["abs"].count(os.sep))
            return (cands[0], "normalized")

    # Strategy 3: difflib close match (high cutoff)
    closes = difflib.get_close_matches(z_basename, all_lowers, n=3, cutoff=0.88)
    if closes:
        cands = by_lower[closes[0]]
        cands.sort(key=lambda c: c["abs"].count(os.sep))
        return (cands[0], f"difflib_88")

    return (None, None)

print("[3] Matching...")
proposals = []
counts = {"exact": 0, "exact_multi": 0, "normalized": 0, "difflib_88": 0, "no_match": 0}
for item in missing:
    match, conf = find_match(item)
    rec = {"itemID": item["itemID"], "title": item["title"],
           "zotero_basename": item["basename"], "confidence": conf,
           "match_abs": match["abs"] if match else None,
           "match_rel": os.path.relpath(match["abs"], KAMI).replace("\\", "/") if match else None}
    proposals.append(rec)
    counts[conf or "no_match"] += 1

for k, v in counts.items(): print(f"  {k}: {v}")

# ----------------------------------------------------------------------------
# 5. Escreve outputs
# ----------------------------------------------------------------------------
with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump({"date": DATE, "counts": counts, "proposals": proposals}, f, ensure_ascii=False, indent=2)

lines = [f"# Fuzzy match proposals — {DATE}", "",
         f"Total truly_missing: **{len(missing)}**", "",
         "## Resultado",
         f"- ✅ exact match (1 candidato): **{counts['exact']}**",
         f"- 🔀 exact match (vários candidatos, escolhi mais raso): **{counts['exact_multi']}**",
         f"- 🧹 normalized match (` 1.pdf`, ` (1).pdf` removidos): **{counts['normalized']}**",
         f"- ❓ difflib match (similaridade ≥88%): **{counts['difflib_88']}**",
         f"- ❌ sem match: **{counts['no_match']}**",
         "",
         "## Política conservadora",
         "",
         "Script `O_kami_fuzzy_repoint.js` aplica APENAS matches de confiança alta:",
         "- `exact` (sempre)",
         "- `exact_multi` (sempre — escolheu o mais raso)",
         "- `normalized` (sempre — diferença só em sufixo de cópia)",
         "",
         "Matches `difflib_88` ficam pendentes pra você revisar abaixo antes de aplicar.",
         "Matches `no_match` exigem ação manual (importar de novo, deletar item, etc.).",
         ""]

# tabela auto-aplicáveis
auto = [p for p in proposals if p["confidence"] in ("exact","exact_multi","normalized")]
lines.append(f"## Auto-aplicáveis ({len(auto)})")
lines.append("")
lines.append("| itemID | confiança | Zotero busca | Match encontrado (path) |")
lines.append("|---:|:---:|--------------|---------------------|")
for p in auto[:80]:
    t = (p["zotero_basename"] or "_(?)_")[:50].replace("|","\\|")
    m = p["match_rel"][:80].replace("|","\\|") if p["match_rel"] else "—"
    lines.append(f"| {p['itemID']} | {p['confidence']} | `{t}` | `{m}` |")
if len(auto) > 80: lines.append(f"\n_...e mais {len(auto)-80}_")

# tabela revisar
review = [p for p in proposals if p["confidence"] == "difflib_88"]
lines.append("")
lines.append(f"## Para revisão manual ({len(review)})")
lines.append("")
lines.append("Match com confiança 88%+ via difflib. Confira antes de aplicar.")
lines.append("")
lines.append("| itemID | título | Zotero busca | Sugerido (path) |")
lines.append("|---:|--------|--------------|------------------|")
for p in review[:50]:
    t = (p["title"] or "_(?)_")[:40].replace("|","\\|")
    z = (p["zotero_basename"] or "")[:50].replace("|","\\|")
    m = p["match_rel"][:60].replace("|","\\|") if p["match_rel"] else "—"
    lines.append(f"| {p['itemID']} | {t} | `{z}` | `{m}` |")
if len(review) > 50: lines.append(f"\n_...e mais {len(review)-50}_")

# tabela sem match
no_match = [p for p in proposals if p["confidence"] is None]
lines.append("")
lines.append(f"## Sem match ({len(no_match)}) — provavelmente foram deletados manualmente ou estão fora da pasta")
lines.append("")
lines.append("| itemID | título | Zotero busca |")
lines.append("|---:|--------|--------------|")
for p in no_match[:50]:
    t = (p["title"] or "_(?)_")[:50].replace("|","\\|")
    z = (p["zotero_basename"] or "")[:60].replace("|","\\|")
    lines.append(f"| {p['itemID']} | {t} | `{z}` |")
if len(no_match) > 50: lines.append(f"\n_...e mais {len(no_match)-50}_")

with open(OUT_MD, "w", encoding="utf-8") as f: f.write("\n".join(lines))

# ----------------------------------------------------------------------------
# 6. Gera Script O (só auto-aplicáveis)
# ----------------------------------------------------------------------------
js_repoints = [{"itemID": p["itemID"],
                "new_path": f"attachments:{p['match_rel']}",
                "match_name": os.path.basename(p["match_rel"])}
               for p in auto]

js = f"""// Script O — Recuperar broken links via fuzzy match (Fase 6.2b)
// Data de criação: {DATE}
// Data de execução: PENDENTE
// Status: PENDENTE
// Output esperado: {len(js_repoints)} items repointados (matches de alta confiança).
//
// Contexto: Fase 6.2b. Investigação dos broken pós-dedup achou {len(missing)} items
// "truly_missing" — arquivos que sumiram (não estão no TRASH). Este script aplica
// matches automáticos de alta confiança (exact filename / normalized / difflib≥88%).
//
// Origem: diagnostics/{DATE}_fuzzy_match_proposals.json

const REPOINTS = {json.dumps(js_repoints, ensure_ascii=False)};
const out = [`=== Fuzzy repoint: ${{REPOINTS.length}} items ===`];
for (const r of REPOINTS) {{
  try {{
    const it = await Zotero.Items.getAsync(r.itemID);
    if (!it) {{ out.push(`[${{r.itemID}}] NÃO ENCONTRADO`); continue; }}
    it.attachmentPath = r.new_path;
    await it.saveTx();
    out.push(`[${{r.itemID}}] ✓ → ${{r.match_name}}`);
  }} catch (e) {{ out.push(`[${{r.itemID}}] ✗ ${{e.message||e}}`); }}
}}
return out.join("\\n");
"""
with open(SCRIPT_O, "w", encoding="utf-8") as f: f.write(js)
print(f"\n[4] Outputs:")
print(f"  {OUT_MD}")
print(f"  {OUT_JSON}")
print(f"  {SCRIPT_O} ({len(js_repoints)} items auto-aplicáveis)")
con.close()
