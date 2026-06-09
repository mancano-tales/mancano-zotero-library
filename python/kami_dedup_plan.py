"""
kami_dedup_plan.py — gera plano de deduplicação por hash.

Lê:
  - diagnostics/<DATE>_kami_audit.json (precisa re-hashar pra ter todos paths)
  - O .bak do Zotero (read-only) — pra saber quais paths estão linkados

Regra de canônica:
  1) Se ALGUMA cópia do grupo está linkada no Zotero: canônica = a linkada.
     Se 2+ estão linkadas: canônica = a primeira; as outras precisam de
     update via JS Runner (FLAG `needs_zotero_repoint`).
  2) Se NENHUMA está linkada: canônica = nome mais curto entre as que estão
     na raiz; se nenhuma na raiz, a com path mais raso.

Destino dos duplicados (não-canônicos):
  G:\\My Drive\\[[1]] Kami Uploads\\_TRASH_dedup_<DATE>\\
  Nome: `<canonical_stem>__dup_<N>__<original_stem_short>.<ext>`
  (pra facilitar comparação visual)

Saídas:
  diagnostics/<DATE>_kami_dedup_plan.md       (relatório humano)
  diagnostics/<DATE>_kami_dedup_plan.json     (dados para executor)
  scripts/M_kami_dedup_repoint.js             (JS Runner pra repointar Zotero quando precisar)

NÃO MOVE NADA. Apenas planeja. O executor é kami_dedup_execute.py (criado depois da aprovação).
"""
import sqlite3, os, json, hashlib, re, sys
from collections import defaultdict
from datetime import datetime

KAMI = r"G:\My Drive\[[1]] Kami Uploads"
BAK_DB = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(r"~/Zotero/zotero.sqlite.bak")
PROJECT_ROOT = r"C:\Users\Mancano\Documents\MancanoSync\mancano-zotero-library"
DATE = datetime.now().strftime("%Y-%m-%d")
PLAN_MD   = os.path.join(PROJECT_ROOT, "diagnostics", f"{DATE}_kami_dedup_plan.md")
PLAN_JSON = os.path.join(PROJECT_ROOT, "diagnostics", f"{DATE}_kami_dedup_plan.json")
TRASH_DIR = os.path.join(KAMI, f"_TRASH_dedup_{DATE}")
FINGERPRINT_BYTES = 1024 * 1024
SKIP_DIRS = {".obsidian", f"_TRASH_dedup_{DATE}"}

# ============================================================================
# 1. Re-varre filesystem e calcula fingerprints
# ============================================================================
print(f"[1] Hasheando arquivos em {KAMI}...")

def fingerprint(path, size):
    h = hashlib.sha256(); h.update(str(size).encode())
    try:
        with open(path, "rb") as f: h.update(f.read(FINGERPRINT_BYTES))
        return h.hexdigest()
    except (OSError, PermissionError): return None

files = {}  # full path → {ext, size, fp, name, parent_subdir}
fp_groups = defaultdict(list)
n = 0
for root, dirs, names in os.walk(KAMI):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    rel = os.path.relpath(root, KAMI)
    subdir = rel.split(os.sep)[0] if rel != "." else "(root)"
    for nm in names:
        n += 1
        full = os.path.join(root, nm)
        try: sz = os.path.getsize(full)
        except: continue
        fp = fingerprint(full, sz)
        if not fp: continue
        info = {"abs": full, "name": nm, "ext": os.path.splitext(nm)[1].lower(),
                "size": sz, "fp": fp, "parent_subdir": subdir,
                "depth": rel.count(os.sep) + (0 if rel == "." else 1)}
        files[full] = info
        fp_groups[fp].append(full)
        if n % 500 == 0: print(f"    ...{n}")
print(f"    {len(files)} arquivos indexados, {len(fp_groups)} fingerprints únicos")

# ============================================================================
# 2. Lê paths linkados no Zotero
# ============================================================================
print(f"\n[2] Lendo Zotero ({BAK_DB})...")
con = sqlite3.connect(f"file:{BAK_DB}?mode=ro", uri=True); con.row_factory = sqlite3.Row
LINKED_FILE = 2
zotero_paths = {}  # path_normalized → {itemID, title, original_zotero_path}
rows = con.execute("""
  SELECT ia.itemID, ia.linkMode, ia.path,
         (SELECT iv.value FROM itemData id JOIN itemDataValues iv ON iv.valueID=id.valueID
          JOIN fields f ON f.fieldID=id.fieldID WHERE id.itemID=ia.itemID AND f.fieldName='title') AS title
  FROM itemAttachments ia
  WHERE ia.itemID NOT IN (SELECT itemID FROM deletedItems) AND ia.linkMode=?
""", (LINKED_FILE,)).fetchall()
for r in rows:
    p = r["path"]
    if not p: continue
    if p.startswith("attachments:"):
        rel = p[len("attachments:"):]
        resolved = os.path.join(KAMI, rel)
    elif os.path.isabs(p):
        resolved = p
    else:
        resolved = os.path.join(KAMI, p)
    zotero_paths[resolved.lower()] = {
        "itemID": r["itemID"], "title": r["title"],
        "zotero_path": r["path"], "resolved": resolved
    }
con.close()
print(f"    {len(zotero_paths)} paths LINKED_FILE no Zotero")

# ============================================================================
# 3. Decide canônica por grupo + plano de movimentação
# ============================================================================
def safe_stem(s, maxlen=80):
    s = re.sub(r'[<>:"|?*\r\n\t]', '_', s)
    s = s[:maxlen]
    return s.rstrip(". ")

groups_with_dups = {fp: paths for fp, paths in fp_groups.items() if len(paths) > 1}
print(f"\n[3] {len(groups_with_dups)} grupos com 2+ cópias")

plan = []  # cada item: {fp, canonical, to_move:[{src,dst,note,...}], needs_zotero_repoint:[itemID,...]}
stats = {"singletons":0, "groups":0, "files_to_move":0, "bytes_to_free":0,
         "groups_with_zotero_link":0, "groups_needing_repoint":0, "files_lost_link":0}

for fp, paths in groups_with_dups.items():
    stats["groups"] += 1
    # detecta quais são linkadas
    linked = [p for p in paths if p.lower() in zotero_paths]
    if linked:
        stats["groups_with_zotero_link"] += 1
        canonical = linked[0]
        repoint_needed = [zotero_paths[l.lower()]["itemID"] for l in linked[1:]]
        if len(linked) > 1:
            stats["groups_needing_repoint"] += 1
    else:
        # nenhuma linkada — escolhe por regra: na raiz, nome mais curto
        root_paths = [p for p in paths if files[p]["parent_subdir"] == "(root)"]
        candidates = root_paths if root_paths else paths
        canonical = min(candidates, key=lambda p: (files[p]["depth"], len(files[p]["name"])))
        repoint_needed = []

    canonical_info = files[canonical]
    canonical_stem = os.path.splitext(canonical_info["name"])[0]

    to_move = []
    for i, p in enumerate([x for x in paths if x != canonical]):
        info = files[p]
        orig_stem = os.path.splitext(info["name"])[0]
        # dst name: canonical__dup_N__originalShort.ext
        dst_name = f"{safe_stem(canonical_stem, 100)}__dup_{i+1}__{safe_stem(orig_stem, 60)}{info['ext']}"
        dst = os.path.join(TRASH_DIR, dst_name)
        to_move.append({
            "src": p, "dst": dst, "size": info["size"],
            "original_subdir": info["parent_subdir"],
            "was_zotero_linked": p.lower() in zotero_paths,
            "zotero_item_id": zotero_paths.get(p.lower(), {}).get("itemID"),
        })
        stats["files_to_move"] += 1
        stats["bytes_to_free"] += info["size"]
        if p.lower() in zotero_paths:
            stats["files_lost_link"] += 1

    plan.append({
        "fp": fp,
        "n_copies": len(paths),
        "canonical": canonical,
        "canonical_size": canonical_info["size"],
        "canonical_subdir": canonical_info["parent_subdir"],
        "n_zotero_linked": len(linked),
        "repoint_needed_item_ids": repoint_needed,
        "to_move": to_move,
    })

# ============================================================================
# 4. Saída
# ============================================================================
os.makedirs(os.path.dirname(PLAN_JSON), exist_ok=True)
with open(PLAN_JSON, "w", encoding="utf-8") as f:
    json.dump({"date": DATE, "stats": stats, "trash_dir": TRASH_DIR, "plan": plan}, f, ensure_ascii=False, indent=2)

# Markdown
lines = [f"# Plano de Dedup — Kami Uploads {DATE}", "",
         f"**Destino dos movidos**: `{TRASH_DIR}\\` (subpasta de Kami Uploads, você revisa manualmente)",
         "",
         "## Resumo", "",
         f"- Grupos de hash com 2+ cópias: **{stats['groups']:,}**",
         f"- Grupos com pelo menos 1 cópia linkada no Zotero: **{stats['groups_with_zotero_link']:,}**",
         f"- Grupos que precisam de **repoint do Zotero** (2+ links no mesmo conteúdo): **{stats['groups_needing_repoint']:,}**",
         f"- Arquivos a mover para `_TRASH_dedup_{DATE}\\`: **{stats['files_to_move']:,}**",
         f"- Tamanho a liberar da raiz/subpastas: **{stats['bytes_to_free']/1e9:.2f} GB**",
         f"- Arquivos movidos que estão linkados (precisam repoint): **{stats['files_lost_link']:,}**",
         "",
         "## Regras aplicadas",
         "",
         "1. Se 1+ cópia do grupo é linkada por algum item do Zotero: **canonical = primeira linkada**.",
         "   Se 2+ são linkadas: as demais geram entrada para repoint (script JS auxiliar).",
         "2. Se NENHUMA é linkada: **canonical = na raiz com nome mais curto** (fallback: path mais raso).",
         "3. Movidos vão para subpasta TRASH com nome `<canonical>__dup_N__<original_short>.ext`",
         "   para facilitar comparação visual quando você conferir.",
         "",
         "## Top 30 grupos (mais cópias)", "",
         "| # cópias | Canonical | Linkado? | Subdir canonical |",
         "|---:|-----------|:--------:|------------------|",
         ]

for entry in sorted(plan, key=lambda x: -x["n_copies"])[:30]:
    name = os.path.basename(entry["canonical"])[:70].replace("|","\\|")
    linked = "✓" if entry["n_zotero_linked"] > 0 else "—"
    if entry["n_zotero_linked"] > 1: linked = f"⚠️ {entry['n_zotero_linked']}"
    lines.append(f"| {entry['n_copies']} | `{name}` | {linked} | {entry['canonical_subdir']} |")
lines += ["", "## Grupos que precisam de repoint do Zotero", ""]
needing = [e for e in plan if e["repoint_needed_item_ids"]]
if needing:
    lines.append("Items abaixo apontam pra cópias que vão pra TRASH. Script `M_kami_dedup_repoint.js` "
                 "re-aponta esses items pro canonical do grupo.")
    lines.append("")
    lines.append("| itemID(s) | canonical | # cópias |")
    lines.append("|---|---|---:|")
    for e in needing[:50]:
        ids = ",".join(map(str, e["repoint_needed_item_ids"]))
        name = os.path.basename(e["canonical"])[:70].replace("|","\\|")
        lines.append(f"| {ids} | `{name}` | {e['n_copies']} |")
else:
    lines.append("_Nenhum — todo grupo tem no máximo 1 link Zotero. Nada pra repointar._")
lines += ["", "## Exemplos de arquivos que serão movidos (primeiros 20)", "",
          "| Src (subdir) | Dst (nome em TRASH) |",
          "|--------------|---------------------|"]
shown = 0
for e in plan:
    for m in e["to_move"]:
        if shown >= 20: break
        src = os.path.relpath(m["src"], KAMI)[:80].replace("|","\\|")
        dst = os.path.basename(m["dst"])[:80].replace("|","\\|")
        lines.append(f"| `{src}` | `{dst}` |")
        shown += 1
    if shown >= 20: break

with open(PLAN_MD, "w", encoding="utf-8") as f: f.write("\n".join(lines))

# ============================================================================
# 5. Gera M_kami_dedup_repoint.js se precisar
# ============================================================================
if needing:
    repoints = []
    for e in needing:
        # apontar itens pro canonical (que continua no mesmo path — mas pode estar em subdir; usa rel ao KAMI)
        canonical_rel = os.path.relpath(e["canonical"], KAMI).replace("\\", "/")
        for iid in e["repoint_needed_item_ids"]:
            repoints.append({"itemID": iid, "new_path": f"attachments:{canonical_rel}",
                             "canonical_name": os.path.basename(e["canonical"])})
    js = f"""// Script M — Repointar itens Zotero para canonical pós-dedup
// Data de criação: {DATE}
// Data de execução: PENDENTE
// Status: PENDENTE
// Output esperado: {len(repoints)} items repointados.
//
// Contexto: Fase 6.2a. Quando um grupo de hash duplicado tinha 2+ items Zotero
// apontando para cópias diferentes do mesmo conteúdo, mantemos só a canonical
// e re-apontamos os outros items pra ela. Faz isso ANTES de mover os arquivos.

const REPOINTS = {json.dumps(repoints, ensure_ascii=False)};
const out = [`=== Repointar ${{REPOINTS.length}} items ===`];
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
    js_path = os.path.join(PROJECT_ROOT, "scripts", f"M_kami_dedup_repoint.js")
    with open(js_path, "w", encoding="utf-8") as f: f.write(js)
    print(f"\n[5] Script JS para repoint: {js_path} ({len(repoints)} items)")

print(f"\n[4] Plano:\n    {PLAN_MD}\n    {PLAN_JSON}")
print(f"\n=== RESUMO ===")
for k, v in stats.items():
    if 'bytes' in k:
        print(f"  {k:30s} {v/1e9:.2f} GB")
    else:
        print(f"  {k:30s} {v:,}")
