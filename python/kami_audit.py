"""
kami_audit.py — Fase 6.0: auditoria read-only da pasta Kami Uploads.

Cruza:
  - Filesystem: G:\\My Drive\\[[1]] Kami Uploads (recursive)
  - Zotero:     itemAttachments do .bak (read-only via URI)

Produz 4 listas:
  1. Linked OK         — Zotero referencia + arquivo existe
  2. Linked broken     — Zotero referencia mas arquivo sumiu
  3. Physical orphan   — arquivo existe, ninguém linka
  4. Hash duplicates   — mesmo fingerprint, paths diferentes

Performance:
  Fingerprint = (size, sha256 dos primeiros 1 MB). Suficiente para detectar
  duplicatas reais em PDFs/EPUBs. Full SHA256 dos 13.7 GB levaria ~10 min;
  fingerprint dá <1 min num SSD.

Output:
  diagnostics/<YYYY-MM-DD>_kami_audit.md       (relatório humano)
  diagnostics/<YYYY-MM-DD>_kami_audit.json     (dados brutos pra próximas fases)

Uso:
    python kami_audit.py
    python kami_audit.py [path_bak]
"""
import sqlite3, os, sys, json, hashlib, re
from collections import defaultdict
from datetime import datetime

KAMI = r"G:\My Drive\[[1]] Kami Uploads"
BAK_DB = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(r"~/Zotero/zotero.sqlite.bak")
PROJECT_ROOT = r"C:\Users\Mancano\Documents\MancanoSync\mancano-zotero-library"
DATE = datetime.now().strftime("%Y-%m-%d")
OUT_MD = os.path.join(PROJECT_ROOT, "diagnostics", f"{DATE}_kami_audit.md")
OUT_JSON = os.path.join(PROJECT_ROOT, "diagnostics", f"{DATE}_kami_audit.json")

FINGERPRINT_BYTES = 1024 * 1024   # 1 MB
# Skip:
#  - .obsidian (vault do user)
#  - _TRASH_dedup_* (arquivos movidos pela Fase 6.2a — preservados pra revisão)
SKIP_DIRS_EXACT = {".obsidian"}
SKIP_DIRS_PREFIX = ("_TRASH_dedup_",)

# ============================================================================
# 1) Varre o filesystem
# ============================================================================
print(f"[1] Varrendo {KAMI}...")
def fingerprint(path, size):
    """Hash dos primeiros FINGERPRINT_BYTES + size. Stable e rápido."""
    h = hashlib.sha256()
    h.update(str(size).encode())
    try:
        with open(path, "rb") as f:
            h.update(f.read(FINGERPRINT_BYTES))
    except (OSError, PermissionError) as e:
        return None
    return h.hexdigest()

files_by_path = {}     # path normalizado lower → dict
fp_groups = defaultdict(list)  # fingerprint → [paths]
scanned = skipped = 0

for root, dirs, names in os.walk(KAMI):
    dirs[:] = [d for d in dirs
               if d not in SKIP_DIRS_EXACT
               and not any(d.startswith(p) for p in SKIP_DIRS_PREFIX)]
    for n in names:
        scanned += 1
        full = os.path.join(root, n)
        try:
            st = os.stat(full)
        except OSError:
            skipped += 1; continue
        rel = os.path.relpath(full, KAMI)
        fp = fingerprint(full, st.st_size)
        info = {
            "abs": full,
            "rel": rel,
            "filename": n,
            "ext": os.path.splitext(n)[1].lower(),
            "size": st.st_size,
            "fp": fp,
        }
        files_by_path[full.lower()] = info
        if fp: fp_groups[fp].append(full)
        if scanned % 500 == 0:
            print(f"    ...{scanned} arquivos varridos")

print(f"    Total: {scanned} varridos, {skipped} pulados, {len(files_by_path)} indexados")

# ============================================================================
# 2) Lê paths do Zotero
# ============================================================================
print(f"\n[2] Lendo {BAK_DB} (read-only)...")
con = sqlite3.connect(f"file:{BAK_DB}?mode=ro", uri=True); con.row_factory = sqlite3.Row
cur = con.cursor()

# Base path setting do Zotero
base_path = cur.execute(
    "SELECT value FROM settings WHERE setting='extensions.zotero' AND key='baseAttachmentPath'"
).fetchone()
# fallback: pegar do prefs.js — hardcoded já que sabemos
base_path = base_path[0] if base_path else r"G:\My Drive\[[1]] Kami Uploads"
print(f"    baseAttachmentPath: {base_path}")

# linkMode: 0=IMPORTED_FILE, 1=IMPORTED_URL, 2=LINKED_FILE, 3=LINKED_URL
LINKED_FILE = 2; IMPORTED_FILE = 0
rows = cur.execute("""
    SELECT ia.itemID, ia.parentItemID, ia.linkMode, ia.contentType, ia.path,
           (SELECT iv.value FROM itemData id JOIN itemDataValues iv ON iv.valueID=id.valueID
            JOIN fields f ON f.fieldID=id.fieldID WHERE id.itemID=ia.itemID AND f.fieldName='title') AS title,
           (SELECT key FROM items WHERE itemID=ia.itemID) AS key
    FROM itemAttachments ia
    WHERE ia.itemID NOT IN (SELECT itemID FROM deletedItems)
""").fetchall()
print(f"    {len(rows)} attachments encontrados no Zotero")

def resolve_zotero_path(path, link_mode, item_key):
    """Resolve o path do Zotero para um caminho absoluto verificável."""
    if not path: return None
    # Prefixo "attachments:" = relativo ao baseAttachmentPath
    if path.startswith("attachments:"):
        rel = path[len("attachments:"):]
        return os.path.join(base_path, rel)
    # Prefixo "storage:" = dentro de storage/<itemKey>/
    if path.startswith("storage:"):
        rel = path[len("storage:"):]
        return os.path.join(os.path.expanduser(r"~/Zotero/storage"), item_key or "", rel)
    # Path absoluto
    if os.path.isabs(path):
        return path
    # Fallback: trata como relativo ao baseAttachmentPath
    return os.path.join(base_path, path)

linked_ok = []
linked_broken = []
zotero_paths_lower = set()  # paths que o Zotero conhece (lower-case para comparação)

for r in rows:
    p = resolve_zotero_path(r["path"], r["linkMode"], r["key"])
    if not p:
        # provavelmente snapshot HTML salvo, nada a fazer
        continue
    plow = p.lower()
    zotero_paths_lower.add(plow)
    rec = {
        "itemID": r["itemID"], "parentItemID": r["parentItemID"],
        "linkMode": r["linkMode"], "contentType": r["contentType"],
        "zotero_path": r["path"], "resolved": p,
        "title": r["title"],
    }
    if plow in files_by_path:
        rec["fs_size"] = files_by_path[plow]["size"]
        linked_ok.append(rec)
    else:
        # arquivo não está onde Zotero acha — só consideramos "broken" se for
        # link pra dentro de Kami Uploads (não conta storage:)
        if p.lower().startswith(base_path.lower()) and r["linkMode"] == LINKED_FILE:
            linked_broken.append(rec)

# ============================================================================
# 3) Identifica órfãos físicos (estão no filesystem mas ninguém linka)
# ============================================================================
orphan_physical = []
for plow, info in files_by_path.items():
    if plow not in zotero_paths_lower:
        # ignora arquivos do Obsidian e meta-arquivos
        if info["ext"] in (".tmp", ""): continue
        if info["filename"].startswith("."): continue  # arquivos ocultos / locks remanescentes
        orphan_physical.append(info)

# ============================================================================
# 4) Duplicatas físicas (mesmo fingerprint, mais de 1 path)
# ============================================================================
hash_dups = {fp: paths for fp, paths in fp_groups.items() if len(paths) > 1}

# ============================================================================
# 5) Categorização por tipo (alinhada com preferência do user: flat + alguns subdirs)
# ============================================================================
def file_category(info):
    name_lower = info["filename"].lower()
    ext = info["ext"]
    if ext == ".pdf":
        # heurísticas de sub-tipo
        if re.search(r"\b(syllabus|programa de curso|ementa|course outline)\b", name_lower):
            return "syllabi"
        if re.search(r"\b(cv|currículo|curriculum vitae|lattes)\b", name_lower):
            return "cvs"
        return "academic_pdf"
    if ext == ".epub":   return "academic_epub"
    if ext == ".pptx":   return "presentations"
    if ext == ".docx":
        if re.search(r"\b(syllabus|programa de curso|ementa)\b", name_lower):
            return "syllabi"
        if re.search(r"\b(cv|currículo)\b", name_lower):
            return "cvs"
        return "documents"
    if ext in (".doc",".rtf",".odt"):  return "documents"
    if ext in (".jpg",".png",".gif"):  return "images"
    if ext == ".zip":     return "archives"
    if ext in (".md",".gdoc"): return "notes"
    return "other"

orphan_by_cat = defaultdict(list)
for o in orphan_physical:
    orphan_by_cat[file_category(o)].append(o)

# ============================================================================
# 6) Tamanho ocupado por categoria de problema
# ============================================================================
def size_of(items, get_size=lambda x: x.get("size") or x.get("fs_size") or 0):
    return sum(get_size(x) for x in items)

# ============================================================================
# 7) Output JSON (bruto para próximas fases)
# ============================================================================
os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
report_data = {
    "date": DATE,
    "stats": {
        "total_files_scanned": scanned,
        "total_files_indexed": len(files_by_path),
        "total_zotero_attachments": len(rows),
        "linked_ok": len(linked_ok),
        "linked_broken": len(linked_broken),
        "orphan_physical": len(orphan_physical),
        "hash_dup_groups": len(hash_dups),
    },
    "linked_broken": linked_broken,
    "orphan_physical": orphan_physical[:1000],  # limita para JSON não explodir
    "orphan_total": len(orphan_physical),
    "orphan_by_category": {k: [o["filename"] for o in v[:50]] for k, v in orphan_by_cat.items()},
    "orphan_category_counts": {k: len(v) for k, v in orphan_by_cat.items()},
    "orphan_category_size_gb": {k: round(size_of(v)/1e9, 2) for k, v in orphan_by_cat.items()},
    "hash_dups": [{"fp": fp, "paths": paths} for fp, paths in list(hash_dups.items())[:200]],
    "hash_dup_total": len(hash_dups),
    "base_path": base_path,
}
with open(OUT_JSON, "w", encoding="utf-8") as fh:
    json.dump(report_data, fh, ensure_ascii=False, indent=2)

# ============================================================================
# 8) Markdown legível
# ============================================================================
def gb(n): return f"{n/1e9:.2f} GB"

L = []
def w(s=""): L.append(s)

w(f"# Kami Uploads — Auditoria {DATE}")
w()
w(f"**Pasta:** `{KAMI}`  ")
w(f"**Banco Zotero:** `{BAK_DB}` (read-only via URI)  ")
w(f"**baseAttachmentPath registrado:** `{base_path}`")
w()
w("## 1. Resumo")
w()
w(f"- Arquivos varridos: **{scanned:,}** ({len(files_by_path):,} indexados)")
w(f"- Anexos no Zotero:  **{len(rows):,}**")
w(f"- ✅ Linked OK:      **{len(linked_ok):,}**")
w(f"- 💥 Linked broken:  **{len(linked_broken):,}** (Zotero aponta, arquivo sumiu)")
w(f"- 🟡 Órfãos físicos: **{len(orphan_physical):,}** ({gb(size_of(orphan_physical))})")
w(f"- 🔁 Grupos de hash duplicado: **{len(hash_dups):,}**")
w()

w("## 2. Linked broken (Zotero aponta para arquivo inexistente)")
w()
if linked_broken:
    w("| itemID | título | path esperado | linkMode |")
    w("|---:|--------|---------------|:--------:|")
    for r in linked_broken[:50]:
        t = (r["title"] or "_(sem título)_")[:70].replace("|","\\|")
        p = r["resolved"][:80].replace("|","\\|")
        w(f"| {r['itemID']} | {t} | `{p}` | {r['linkMode']} |")
    if len(linked_broken) > 50:
        w(f"\n_...e mais {len(linked_broken)-50} (ver JSON completo)_")
else:
    w("_Nenhum. Todos os links do Zotero apontam para arquivos existentes._")
w()

w("## 3. Órfãos físicos por categoria")
w()
w("| Categoria | n | Tamanho | Destino sugerido (flat) |")
w("|-----------|--:|--------:|-------------------------|")
DEST_FLAT = {
    "academic_pdf": "raiz (flat)",
    "academic_epub": "raiz (flat)",
    "presentations": "`Presentations/`",
    "syllabi": "`Syllabi/`",
    "cvs": "`CVs/`",
    "documents": "`Documents/`",
    "images": "`_misc/`",
    "archives": "`_misc/`",
    "notes": "`_misc/` (ou Obsidian)",
    "other": "`_misc/`",
}
for cat in sorted(orphan_by_cat.keys()):
    items = orphan_by_cat[cat]
    w(f"| {cat} | {len(items):,} | {gb(size_of(items))} | {DEST_FLAT.get(cat,'?')} |")
w()
w("### Amostra de órfãos PDF (acadêmicos) — primeiros 30")
w()
academic = orphan_by_cat.get("academic_pdf", [])
for o in academic[:30]:
    w(f"- `{o['filename'][:100]}`")
if len(academic) > 30:
    w(f"\n_...e mais {len(academic)-30} (ver JSON)_")
w()

w("## 4. Duplicatas físicas (mesmo conteúdo, paths diferentes)")
w()
if hash_dups:
    sorted_dups = sorted(hash_dups.items(), key=lambda x: -len(x[1]))
    w(f"Total de grupos: **{len(hash_dups):,}**")
    w()
    w("### Top 20 grupos (mais cópias)")
    w()
    for fp, paths in sorted_dups[:20]:
        w(f"- **{len(paths)} cópias** (fp `{fp[:12]}...`):")
        for p in paths:
            rel = os.path.relpath(p, KAMI)
            w(f"  - `{rel[:100]}`")
else:
    w("_Nenhum duplicado detectado._")
w()

w("## 5. Próximas subfases sugeridas")
w()
w("- **6.1 Quick wins** (já feito em 30/05): 20 lock files deletados.")
w("- **6.2 Triagem de órfãos físicos**:")
w("  - Decidir caso-a-caso para os PDFs acadêmicos (importar pro Zotero, arquivar, deletar).")
w("  - PPTX/DOCX/syllabi/CVs → mover pras subpastas tipadas.")
w("- **6.3 Resolver links quebrados**: para cada item da seção 2, buscar arquivo equivalente na pasta (por hash ou título) e reanexar via script JS.")
w("- **6.4 Resolver duplicatas físicas**: manter 1 cópia por hash, deletar/relinkar as outras (pode ser feito em batch via PowerShell + Zotero JS).")
w()

with open(OUT_MD, "w", encoding="utf-8") as fh:
    fh.write("\n".join(L))

print(f"\n[3] Outputs:")
print(f"    {OUT_MD}")
print(f"    {OUT_JSON}")
print()
print("=== RESUMO ===")
print(f"Linked OK:      {len(linked_ok)}")
print(f"Linked broken:  {len(linked_broken)}")
print(f"Órfãos físicos: {len(orphan_physical)} ({gb(size_of(orphan_physical))})")
print(f"Hash dups:      {len(hash_dups)} grupos")
print()
print("Órfãos por categoria:")
for cat, items in sorted(orphan_by_cat.items(), key=lambda x: -len(x[1])):
    print(f"  {cat:20s} {len(items):5d}  {gb(size_of(items))}")
con.close()
