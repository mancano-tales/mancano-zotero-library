"""
kami_dedup_execute.py — executa o plano de dedup.

Lê: diagnostics/<DATE>_kami_dedup_plan.json
Faz: move arquivos para _TRASH_dedup_<DATE>\, escreve manifest.

Ordem segura:
  1) PRIMEIRO rodar M_kami_dedup_repoint.js no Zotero (re-aponta 31 items pro canonical).
  2) DEPOIS rodar este script (move arquivos).
  3) Verificar que tudo continua linkado no Zotero (script L_verify ou diagnose).

Defensivo:
  - --dry-run: lista o que faria sem mover.
  - Verifica que cada src ainda existe e canonical não foi movido também.
  - Trunca dst_name pra ficar dentro de 240 char (limite NTFS prático).
  - Manifest CSV + MD pra você revisar antes de esvaziar a TRASH.
  - Log completo em diagnostics/.

Uso:
    python kami_dedup_execute.py --dry-run
    python kami_dedup_execute.py --execute   # MOVE de verdade
"""
import json, os, sys, shutil, csv
from datetime import datetime

PROJECT_ROOT = r"C:\Users\Mancano\Documents\MancanoSync\mancano-zotero-library"

# Aceita --date YYYY-MM-DD pra apontar para plano específico (default: hoje)
DATE = datetime.now().strftime("%Y-%m-%d")
if "--date" in sys.argv:
    DATE = sys.argv[sys.argv.index("--date") + 1]
# Auto-fallback: se plano de hoje não existe, pega o mais recente em diagnostics/
import glob
PLAN_JSON = os.path.join(PROJECT_ROOT, "diagnostics", f"{DATE}_kami_dedup_plan.json")
if not os.path.exists(PLAN_JSON):
    candidates = sorted(glob.glob(os.path.join(PROJECT_ROOT, "diagnostics", "*_kami_dedup_plan.json")))
    if candidates:
        PLAN_JSON = candidates[-1]
        DATE = os.path.basename(PLAN_JSON).split("_kami")[0]
        print(f"[auto-fallback] usando plano mais recente: {PLAN_JSON}")
LOG_PATH = os.path.join(PROJECT_ROOT, "diagnostics", f"{DATE}_kami_dedup_execlog.md")

DRY_RUN = "--dry-run" in sys.argv
EXECUTE = "--execute" in sys.argv
if not (DRY_RUN or EXECUTE):
    print("Uso: python kami_dedup_execute.py [--dry-run | --execute] [--date YYYY-MM-DD]"); sys.exit(1)

with open(PLAN_JSON, encoding="utf-8") as f:
    plan_data = json.load(f)
TRASH_DIR = plan_data["trash_dir"]
plan = plan_data["plan"]

# ===== prepara =====
if EXECUTE:
    os.makedirs(TRASH_DIR, exist_ok=True)
manifest_csv = os.path.join(TRASH_DIR, "_manifest.csv")
manifest_md = os.path.join(TRASH_DIR, "_manifest.md")

def trim_name(name, max_total=240):
    """Garante que o filename não passa de max_total chars (NTFS limit ~255)."""
    if len(name) <= max_total: return name
    stem, ext = os.path.splitext(name)
    return stem[:max_total - len(ext)] + ext

log_lines = [f"# Execução dedup — {DATE}", f"**Modo**: {'DRY-RUN' if DRY_RUN else 'EXECUTE'}", ""]
manifest_rows = [["dst_filename", "src_path", "size_bytes", "original_subdir",
                  "was_zotero_linked", "zotero_item_id", "canonical_path"]]
stats = {"moved": 0, "skipped_missing_src": 0, "skipped_dst_exists": 0,
         "skipped_canonical_moved": 0, "errors": 0, "bytes_moved": 0}

# coleta canonicals para checagem
canonical_paths = {entry["canonical"] for entry in plan}

# ===== executa =====
for entry in plan:
    canonical = entry["canonical"]
    for m in entry["to_move"]:
        src = m["src"]
        dst_name = trim_name(os.path.basename(m["dst"]))
        dst = os.path.join(TRASH_DIR, dst_name)

        # checagens
        if not os.path.exists(src):
            stats["skipped_missing_src"] += 1
            log_lines.append(f"- ⊘ SKIP (src sumiu): `{src}`")
            continue
        if src in canonical_paths:
            stats["skipped_canonical_moved"] += 1
            log_lines.append(f"- ⊘ SKIP (src é canonical de outro grupo): `{src}`")
            continue
        if os.path.exists(dst):
            stats["skipped_dst_exists"] += 1
            log_lines.append(f"- ⊘ SKIP (dst existe): `{dst_name}`")
            continue

        # registra no manifest
        manifest_rows.append([dst_name, src, m["size"], m["original_subdir"],
                              "yes" if m["was_zotero_linked"] else "no",
                              m["zotero_item_id"] or "", canonical])
        if DRY_RUN:
            log_lines.append(f"- DRY: `{os.path.relpath(src, plan_data['trash_dir'].rsplit(os.sep,1)[0])}` → `_TRASH/`{dst_name}`")
            stats["moved"] += 1
            stats["bytes_moved"] += m["size"]
        else:
            try:
                shutil.move(src, dst)
                stats["moved"] += 1
                stats["bytes_moved"] += m["size"]
            except Exception as e:
                stats["errors"] += 1
                log_lines.append(f"- ✗ ERR mover `{src}` → `{dst_name}`: {e}")

# ===== escreve manifest (sempre) =====
os.makedirs(os.path.dirname(manifest_csv), exist_ok=True) if EXECUTE else None
if EXECUTE:
    with open(manifest_csv, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(manifest_rows)
    # MD legível
    mlines = [f"# TRASH manifest — {DATE}", "",
              f"Total a revisar: **{stats['moved']:,}** arquivos / **{stats['bytes_moved']/1e9:.2f} GB**.",
              "", "Sort por `dst_filename` agrupa por canonical (prefixo é o nome do arquivo mantido).",
              "", "| dst | src (origem) | tamanho | canonical |",
              "|-----|--------------|--------:|-----------|"]
    for row in manifest_rows[1:]:
        sz = f"{int(row[2])/1e6:.1f} MB" if int(row[2]) > 1e6 else f"{int(row[2])/1024:.1f} KB"
        mlines.append(f"| `{row[0][:60]}` | `{os.path.relpath(row[1], plan_data['trash_dir'].rsplit(os.sep,1)[0])[:60]}` | {sz} | `{os.path.basename(row[6])[:60]}` |")
    with open(manifest_md, "w", encoding="utf-8") as f: f.write("\n".join(mlines))

# ===== escreve log =====
log_lines.insert(2, "## Estatísticas")
log_lines.insert(3, "")
for k, v in stats.items():
    log_lines.insert(4, f"- {k}: {v:,}" + (f" ({v/1e9:.2f} GB)" if k == "bytes_moved" else ""))
log_lines.insert(4 + len(stats), "")
with open(LOG_PATH, "w", encoding="utf-8") as f: f.write("\n".join(log_lines))

# ===== console =====
print(f"=== {'DRY-RUN' if DRY_RUN else 'EXECUTE'} ===")
for k, v in stats.items():
    if 'bytes' in k: print(f"  {k:30s} {v/1e9:.2f} GB")
    else:            print(f"  {k:30s} {v:,}")
print(f"\nLog: {LOG_PATH}")
if EXECUTE:
    print(f"Manifest CSV: {manifest_csv}")
    print(f"Manifest MD:  {manifest_md}")
