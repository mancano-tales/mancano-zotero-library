"""
Gera Script N — repointar 42 items que o plano original deixou passar.

Origem: kami_broken_investigation.json (categoria "in_trash_via_manifest").
Esses items linkavam pra arquivos que o dedup moveu pra TRASH, mas o plan
não capturou no Script M.
"""
import json, os
from datetime import datetime

PROJECT_ROOT = r"C:\Users\Mancano\Documents\MancanoSync\mancano-zotero-library"
KAMI = r"G:\My Drive\[[1]] Kami Uploads"
DATE = datetime.now().strftime("%Y-%m-%d")
INVEST_JSON = os.path.join(PROJECT_ROOT, "diagnostics", "2026-06-06_broken_investigation.json")
SCRIPT_OUT = os.path.join(PROJECT_ROOT, "scripts", "N_kami_dedup_repoint_round2.js")

with open(INVEST_JSON, encoding="utf-8") as f:
    data = json.load(f)

repoints = []
for x in data["results"]:
    if x["status"] != "in_trash_via_manifest": continue
    canonical = x["canonical_to_repoint"]
    if not canonical: continue
    canonical_rel = os.path.relpath(canonical, KAMI).replace("\\", "/")
    repoints.append({
        "itemID": x["itemID"],
        "new_path": f"attachments:{canonical_rel}",
        "canonical_name": os.path.basename(canonical),
    })

js = f"""// Script N — Repointar round 2 (items que Script M deixou passar)
// Data de criação: {DATE}
// Data de execução: PENDENTE
// Status: PENDENTE
// Output esperado: {len(repoints)} items repointados.
//
// Contexto: Fase 6.2a.2. Investigação dos broken pós-dedup revelou {len(repoints)}
// items que Zotero linkava pra non-canonicals (movidos pra TRASH). O plano
// original (Script M) só capturou 31 desses por causa de match de path
// case/normalization. Este script cobre o resto.
//
// Origem dos dados: diagnostics/2026-06-06_broken_investigation.json
//                   (categoria "in_trash_via_manifest")

const REPOINTS = {json.dumps(repoints, ensure_ascii=False)};
const out = [`=== Repointar round 2: ${{REPOINTS.length}} items ===`];
for (const r of REPOINTS) {{
  try {{
    const it = await Zotero.Items.getAsync(r.itemID);
    if (!it) {{ out.push(`[${{r.itemID}}] NÃO ENCONTRADO`); continue; }}
    it.attachmentPath = r.new_path;
    await it.saveTx();
    out.push(`[${{r.itemID}}] ✓ → ${{r.canonical_name}}`);
  }} catch (e) {{ out.push(`[${{r.itemID}}] ✗ ${{e.message||e}}`); }}
}}
return out.join("\\n");
"""

with open(SCRIPT_OUT, "w", encoding="utf-8") as f: f.write(js)
print(f"Script N gerado: {SCRIPT_OUT}")
print(f"Repoints: {len(repoints)}")
