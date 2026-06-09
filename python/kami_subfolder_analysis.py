"""
Analisa relação de subpastas (`00_Meta\\`, `_Fix\\`, etc.) com a raiz.
Pergunta: o conteúdo dessas subpastas é redundante com a raiz?
Usa o JSON do kami_audit já gerado.
"""
import json, os
from collections import defaultdict
from datetime import datetime

PROJECT_ROOT = r"C:\Users\Mancano\Documents\MancanoSync\mancano-zotero-library"
DATE = datetime.now().strftime("%Y-%m-%d")
AUDIT_JSON = os.path.join(PROJECT_ROOT, "diagnostics", f"{DATE}_kami_audit.json")

with open(AUDIT_JSON, encoding="utf-8") as f:
    data = json.load(f)

# A auditoria não persistiu todos os arquivos no JSON — só órfãos.
# Vou re-varrer pra ter visão completa: filename → set(subdirs onde aparece)
import os
KAMI = r"G:\My Drive\[[1]] Kami Uploads"

# por (filename, size) → list of subdirs
file_locations = defaultdict(set)
file_sizes = {}
total = 0
for root, dirs, names in os.walk(KAMI):
    # ignora .obsidian
    dirs[:] = [d for d in dirs if d != ".obsidian"]
    rel_root = os.path.relpath(root, KAMI)
    subdir = rel_root.split(os.sep)[0] if rel_root != "." else "(root)"
    for n in names:
        full = os.path.join(root, n)
        try: sz = os.path.getsize(full)
        except: continue
        file_locations[(n.lower(), sz)].add(subdir)
        file_sizes[(n.lower(), sz)] = sz
        total += 1

# para cada subdir, conta:
#   - quantos arquivos seus EXISTEM também na raiz com mesmo (nome, tamanho)
#   - quantos são exclusivos
subdir_stats = defaultdict(lambda: {"shared_with_root": 0, "exclusive": 0, "shared_size": 0, "exclusive_size": 0})
for key, locs in file_locations.items():
    sz = file_sizes[key]
    if "(root)" in locs:
        for loc in locs:
            if loc != "(root)":
                subdir_stats[loc]["shared_with_root"] += 1
                subdir_stats[loc]["shared_size"] += sz
    else:
        for loc in locs:
            if loc != "(root)":
                subdir_stats[loc]["exclusive"] += 1
                subdir_stats[loc]["exclusive_size"] += sz

print(f"Total arquivos varridos: {total}")
print(f"Total (filename,size) únicos: {len(file_locations)}")
print()
print(f"{'Subpasta':<35} {'Compart. raiz':>15} {'Exclusivos':>15} {'Compart MB':>12} {'Exclus MB':>12}")
print("-" * 95)
for s, st in sorted(subdir_stats.items(), key=lambda x: -(x[1]["shared_with_root"] + x[1]["exclusive"])):
    if s == "(root)": continue
    print(f"{s:<35} {st['shared_with_root']:>15} {st['exclusive']:>15} "
          f"{st['shared_size']/1e6:>12.1f} {st['exclusive_size']/1e6:>12.1f}")

# samples por subdir
print()
for target in ["00_Meta", "_Fix"]:
    if target not in subdir_stats: continue
    print(f"\n=== Amostra de exclusivos em {target}\\ ===")
    n_shown = 0
    for key, locs in file_locations.items():
        if target in locs and "(root)" not in locs and n_shown < 15:
            name = [k for k in file_locations.keys() if k == key][0][0]
            print(f"  {name[:100]}")
            n_shown += 1
    if n_shown == 0:
        print("  (nenhum — TODOS os arquivos desta subpasta têm cópia na raiz)")

# arquivos da raiz que NÃO estão em nenhuma subpasta de tipo (estes são candidatos a ficar como estão)
# ...skip for brevity

# salva JSON
out = {
    "date": DATE,
    "subdir_stats": dict(subdir_stats),
    "summary": {
        s: {
            "shared_with_root": st["shared_with_root"],
            "exclusive": st["exclusive"],
            "shared_size_mb": round(st["shared_size"]/1e6, 1),
            "exclusive_size_mb": round(st["exclusive_size"]/1e6, 1),
            "is_likely_mirror": st["shared_with_root"] > 0 and st["exclusive"] == 0,
        }
        for s, st in subdir_stats.items()
    }
}
out_path = os.path.join(PROJECT_ROOT, "diagnostics", f"{DATE}_kami_subfolders.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f"\nJSON: {out_path}")
