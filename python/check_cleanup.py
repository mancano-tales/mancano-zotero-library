"""Pre-cleanup check: detalha coleções vazias e contexto da tag zotmoov."""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), "zotero_readonly.sqlite")
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
cur = con.cursor()

print("=" * 70)
print("COLECOES VAZIAS — detalhes")
print("=" * 70)
# Para cada coleção vazia: tem subcoleções? Tem coleção-pai? Quando criada?
rows = cur.execute("""
    SELECT c.collectionID, c.collectionName, c.parentCollectionID,
           (SELECT collectionName FROM collections WHERE collectionID = c.parentCollectionID) AS parent_name,
           (SELECT COUNT(*) FROM collections WHERE parentCollectionID = c.collectionID) AS num_children,
           c.key
    FROM collections c
    WHERE c.collectionID NOT IN (SELECT collectionID FROM collectionItems)
    ORDER BY num_children DESC, c.collectionName
""").fetchall()
for r in rows:
    parent = f" [pai: {r['parent_name']}]" if r['parent_name'] else " [raiz]"
    children = f" (TEM {r['num_children']} subcolecoes)" if r['num_children'] else ""
    print(f"  - {r['collectionName']!r}{parent}{children}  key={r['key']}")

print()
print("=" * 70)
print("TAG 'zotmoov' — contexto")
print("=" * 70)
zm = cur.execute("""
    SELECT t.tagID, t.name, COUNT(it.itemID) AS n
    FROM tags t LEFT JOIN itemTags it ON t.tagID=it.tagID
    WHERE LOWER(t.name) LIKE '%zotmoov%' OR LOWER(t.name) LIKE '%zotfile%'
    GROUP BY t.tagID
""").fetchall()
for r in zm:
    print(f"  tag={r['name']!r}  itens marcados={r['n']}")

# Quantos itens com a tag zotmoov tambem tem PDF anexado?
print()
print("Itens com tag zotmoov e PDF anexado (verificacao):")
n = cur.execute("""
    SELECT COUNT(DISTINCT i.itemID)
    FROM items i
    JOIN itemTags it ON i.itemID = it.itemID
    JOIN tags t ON it.tagID = t.tagID
    JOIN itemAttachments ia ON ia.parentItemID = i.itemID
    WHERE LOWER(t.name) = 'zotmoov'
      AND ia.contentType = 'application/pdf'
""").fetchone()[0]
print(f"  {n} itens marcados com 'zotmoov' que tem ao menos um PDF")
con.close()
