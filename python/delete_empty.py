"""Apaga 7 colecoes vazias claramente lixo. Faz backup antes."""
import sqlite3, os, shutil, datetime, sys

ZOT_DIR = os.path.expanduser("~/Zotero")
DB = os.path.join(ZOT_DIR, "zotero.sqlite")
JOURNAL = DB + "-journal"
WAL = DB + "-wal"

# Verificacao final: Zotero realmente fechado?
if os.path.exists(JOURNAL) and os.path.getsize(JOURNAL) > 0:
    print("ABORTANDO: zotero.sqlite-journal nao vazio. Zotero pode estar aberto.")
    sys.exit(1)

# Backup extra rotulado
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup = os.path.join(ZOT_DIR, "_diagnostico", f"zotero_pre_cleanup_{ts}.sqlite")
shutil.copy2(DB, backup)
print(f"Backup criado: {backup}")

# Keys das 7 colecoes a apagar (do diagnostico)
keys_to_delete = [
    "227E83NN",  # Primo_RIS_Export
    "GCDI6QGW",  # S0276562416301251
    "HZKNZGK6",  # citationExport-acrefore-9780190264093-e-1679
    "GT99ELV3",  # references.bib
    "9BSUEM9G",  # Teste
    "SHD46Q8A",  # @Voice-2025-3-22
    "GBW285IK",  # 2025-10-28_Politics-of-Inequality_Marius-Busemeyer
]

con = sqlite3.connect(DB)
cur = con.cursor()

# Mostrar o que será apagado (confirmacao final)
print("\nColecoes alvo:")
for k in keys_to_delete:
    r = cur.execute("""
        SELECT collectionID, collectionName,
               (SELECT COUNT(*) FROM collectionItems WHERE collectionID=c.collectionID) AS n_items,
               (SELECT COUNT(*) FROM collections WHERE parentCollectionID=c.collectionID) AS n_sub
        FROM collections c WHERE key=?
    """, (k,)).fetchone()
    if r is None:
        print(f"  {k}: NAO ENCONTRADA")
    else:
        cid, name, ni, ns = r
        flag = " [BLOQUEADA]" if (ni>0 or ns>0) else ""
        print(f"  {k}: '{name}' (id={cid}, itens={ni}, subcols={ns}){flag}")

# Salvaguarda: nao apagar se tiver itens ou subcolecoes
safe_keys = []
for k in keys_to_delete:
    r = cur.execute("""
        SELECT collectionID,
               (SELECT COUNT(*) FROM collectionItems WHERE collectionID=c.collectionID),
               (SELECT COUNT(*) FROM collections WHERE parentCollectionID=c.collectionID)
        FROM collections c WHERE key=?
    """, (k,)).fetchone()
    if r and r[1] == 0 and r[2] == 0:
        safe_keys.append(k)

print(f"\n{len(safe_keys)} de {len(keys_to_delete)} aprovadas para delecao")

# Para o Zotero registrar como apagada e sincronizar:
# - precisamos inserir entrada na tabela syncDeleteLog (libraryID, key, timestamp)
# - e remover a linha de collections
# Isto faz com que o sync remova nos demais devices

now_int = int(datetime.datetime.now().timestamp())

for k in safe_keys:
    # buscar libraryID e collectionID
    row = cur.execute("SELECT collectionID, libraryID FROM collections WHERE key=?", (k,)).fetchone()
    if not row:
        continue
    cid, lib = row
    # registrar exclusao para sync (syncDeleteLogKeys, schema atual >5)
    try:
        cur.execute("""INSERT OR IGNORE INTO syncDeleteLogKeys
                       (libraryID, key, syncObjectTypeID, dateDeleted)
                       VALUES (?, ?, (SELECT syncObjectTypeID FROM syncObjectTypes WHERE name='collection'), datetime('now'))""",
                    (lib, k))
    except sqlite3.OperationalError as e:
        print(f"  aviso syncLog: {e}")
    # apagar relacoes (nao deveria ter, mas por seguranca)
    cur.execute("DELETE FROM collectionItems WHERE collectionID=?", (cid,))
    # apagar a colecao em si
    cur.execute("DELETE FROM collections WHERE collectionID=?", (cid,))

con.commit()

# verificar
remaining = cur.execute("""
    SELECT key, collectionName FROM collections WHERE key IN ({})
""".format(",".join("?"*len(keys_to_delete))), keys_to_delete).fetchall()
print(f"\nRestantes na DB com essas keys: {len(remaining)} (esperado: 0)")
for r in remaining:
    print(f"  ainda existe: {r}")

con.close()
print("\nDONE.")
