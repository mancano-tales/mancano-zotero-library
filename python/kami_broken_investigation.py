"""
Investiga por que linked_broken aumentou de 239 → 306 após dedup.

Hipótese: alguns items Zotero linkavam a non-canonicals que o plano não
capturou (linkMode != 2 ou path encoding diferente). Resultado: file movido
pra TRASH, mas item Zotero ainda aponta pro path original.

Output: lista detalhada dos 306 brokens com:
  - itemID, título, path Zotero
  - Onde o arquivo está AGORA (raiz? TRASH? sumido?)
  - Se está no TRASH, qual é o canonical correspondente (pra repoint)
"""
import sqlite3, os, json, sys
from datetime import datetime

KAMI = r"G:\My Drive\[[1]] Kami Uploads"
TRASH = os.path.join(KAMI, "_TRASH_dedup_2026-06-05")
PROJECT_ROOT = r"C:\Users\Mancano\Documents\MancanoSync\mancano-zotero-library"
SNAP = os.path.join(PROJECT_ROOT, "diagnostics", "zotero_snap_2026-06-06_post-script-M.sqlite")
OUT = os.path.join(PROJECT_ROOT, "diagnostics", "2026-06-06_broken_investigation.md")
MANIFEST_CSV = os.path.join(TRASH, "_manifest.csv")

# Lê manifest pra mapear dst (TRASH) → src (original path)
import csv
manifest = {}  # original_path_basename.lower() → {dst_name, canonical_path, original_path}
with open(MANIFEST_CSV, encoding="utf-8") as f:
    rdr = csv.DictReader(f)
    for row in rdr:
        original_basename = os.path.basename(row["src_path"]).lower()
        manifest[original_basename] = {
            "dst": row["dst_filename"],
            "canonical": row["canonical_path"],
            "original": row["src_path"],
            "zotero_item_id": row["zotero_item_id"],
        }

# Lê Zotero brokens
con = sqlite3.connect(f"file:{SNAP}?mode=ro", uri=True); con.row_factory = sqlite3.Row
LINKED_FILE = 2
rows = con.execute("""
  SELECT ia.itemID, ia.linkMode, ia.path,
         (SELECT iv.value FROM itemData id JOIN itemDataValues iv ON iv.valueID=id.valueID
          JOIN fields f ON f.fieldID=id.fieldID WHERE id.itemID=ia.itemID AND f.fieldName='title') AS title
  FROM itemAttachments ia
  WHERE ia.itemID NOT IN (SELECT itemID FROM deletedItems) AND ia.linkMode=?
""", (LINKED_FILE,)).fetchall()
con.close()

# Resolve cada path Zotero, classifica
results = []
counts = {"file_exists_at_path": 0, "in_trash_via_manifest": 0,
          "in_trash_by_name": 0, "truly_missing": 0,
          "not_in_kami": 0}

for r in rows:
    p = r["path"] or ""
    if p.startswith("attachments:"):
        rel = p[len("attachments:"):]
        resolved = os.path.join(KAMI, rel)
    elif os.path.isabs(p):
        resolved = p
    else:
        resolved = os.path.join(KAMI, p)

    if os.path.exists(resolved):
        counts["file_exists_at_path"] += 1
        continue  # não é broken

    # broken — investigar
    basename = os.path.basename(resolved).lower()
    info = {"itemID": r["itemID"], "title": r["title"], "zotero_path": p,
            "resolved": resolved, "basename": basename, "status": None,
            "trash_dst": None, "canonical_to_repoint": None}

    # 1. Está no TRASH via manifest?
    if basename in manifest:
        m = manifest[basename]
        info["status"] = "in_trash_via_manifest"
        info["trash_dst"] = m["dst"]
        info["canonical_to_repoint"] = m["canonical"]
        counts["in_trash_via_manifest"] += 1
    else:
        # 2. Está no TRASH por nome (procura no diretório TRASH por algo que termine com o basename)
        if os.path.exists(TRASH):
            for tf in os.listdir(TRASH):
                tf_lower = tf.lower()
                # dst pattern: <canonical>__dup_N__<original>.ext
                if "__dup_" in tf_lower and tf_lower.endswith(basename.replace(".pdf",".pdf").replace(".epub",".epub")):
                    info["status"] = "in_trash_by_name"
                    info["trash_dst"] = tf
                    counts["in_trash_by_name"] += 1
                    break
        if not info["status"]:
            # 3. Path está em /Kami Uploads/ mas sumiu mesmo
            if KAMI.lower() in resolved.lower():
                info["status"] = "truly_missing"
                counts["truly_missing"] += 1
            else:
                info["status"] = "not_in_kami"
                counts["not_in_kami"] += 1

    results.append(info)

# Output
print(f"Total brokens analisados: {len(results)}")
for k,v in counts.items(): print(f"  {k}: {v}")

lines = [f"# Investigação dos brokens — 2026-06-06", "",
         f"Total: **{len(results)}** items broken (linkMode=LINKED_FILE).",
         "", "## Distribuição",
         f"- 💡 **Está no TRASH (via manifest)**: {counts['in_trash_via_manifest']} → repoint para canonical",
         f"- 🔍 **Está no TRASH (por nome)**: {counts['in_trash_by_name']} → repoint",
         f"- ❌ **Truly missing** (file sumiu mesmo): {counts['truly_missing']}",
         f"- ❓ **Path fora de Kami Uploads**: {counts['not_in_kami']}",
         "", "## Lista (in_trash_via_manifest — auto-corrigíveis)", "",
         "| itemID | título | dst no TRASH | canonical pra repoint |",
         "|---:|--------|--------------|----------------------|"]
for x in results:
    if x["status"] == "in_trash_via_manifest":
        t = (x["title"] or "_(sem título)_")[:50].replace("|","\\|")
        dst = x["trash_dst"][:60].replace("|","\\|")
        can = os.path.basename(x["canonical_to_repoint"])[:60].replace("|","\\|")
        lines.append(f"| {x['itemID']} | {t} | `{dst}` | `{can}` |")

lines += ["", "## Lista (truly_missing — precisam fuzzy match)", ""]
truly = [x for x in results if x["status"] == "truly_missing"]
lines.append(f"Total: **{len(truly)}**")
lines.append("")
lines.append("| itemID | título | basename procurado |")
lines.append("|---:|--------|-------------------|")
for x in truly[:50]:
    t = (x["title"] or "_(sem título)_")[:50].replace("|","\\|")
    b = x["basename"][:80].replace("|","\\|")
    lines.append(f"| {x['itemID']} | {t} | `{b}` |")
if len(truly) > 50:
    lines.append(f"\n_...e mais {len(truly)-50}_")

with open(OUT, "w", encoding="utf-8") as f: f.write("\n".join(lines))
with open(OUT.replace(".md", ".json"), "w", encoding="utf-8") as f:
    json.dump({"counts": counts, "results": results}, f, ensure_ascii=False, indent=2)
print(f"\nOutputs:\n  {OUT}\n  {OUT.replace('.md','.json')}")
