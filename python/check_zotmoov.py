"""Onde a tag zotmoov esta exatamente?"""
import sqlite3, os
DB = os.path.join(os.path.dirname(__file__), "zotero_readonly.sqlite")
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
cur = con.cursor()

# Tipo dos itens marcados com zotmoov
print("Tipo dos 530 itens com tag 'zotmoov':")
for row in cur.execute("""
    SELECT it.typeName, COUNT(*) AS n
    FROM items i
    JOIN itemTags itag ON i.itemID = itag.itemID
    JOIN tags t ON itag.tagID = t.tagID
    JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
    WHERE LOWER(t.name) = 'zotmoov'
    GROUP BY it.typeName
    ORDER BY n DESC
"""):
    print(f"  {row[0]}: {row[1]}")

# Quantos sao anexos com parent
print("\nDos anexos marcados zotmoov:")
n = cur.execute("""
    SELECT COUNT(*) FROM itemAttachments ia
    JOIN itemTags it ON ia.itemID = it.itemID
    JOIN tags t ON it.tagID = t.tagID
    WHERE LOWER(t.name) = 'zotmoov' AND ia.parentItemID IS NOT NULL
""").fetchone()[0]
print(f"  Com item-pai: {n}")
n = cur.execute("""
    SELECT COUNT(*) FROM itemAttachments ia
    JOIN itemTags it ON ia.itemID = it.itemID
    JOIN tags t ON it.tagID = t.tagID
    WHERE LOWER(t.name) = 'zotmoov' AND ia.parentItemID IS NULL
""").fetchone()[0]
print(f"  Orfaos: {n}")
con.close()
