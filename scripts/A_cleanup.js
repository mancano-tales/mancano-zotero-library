// Script A — Limpeza inicial
// Data de criação: 2026-05-10
// Data de execução: 2026-05-10
// Status: EXECUTADO
// Output esperado: report de coleções deletadas + contagem de itens com tag removida
//
// Resultado real (2026-05-10):
//   Deleted 'references' (127 items kept in library)
//   'Talita': not found
//   'Eduardo': not found
//   Removed 'zotmoov' tag from 529 items
//
// Roda em Tools → Developer → Run JavaScript

const lib = Zotero.Libraries.userLibraryID;
const all = Zotero.Collections.getByLibrary(lib, true);
const report = [];

const namesToDelete = ['references', 'Talita', 'Eduardo'];
for (const target of namesToDelete) {
  const matches = all.filter(c => c.name === target);
  if (!matches.length) { report.push(`'${target}': not found`); continue; }
  for (const c of matches) {
    if (c.getChildCollections().length > 0) {
      report.push(`'${c.name}' has subcollections — SKIPPED`); continue;
    }
    const n = c.getChildItems().length;
    await c.eraseTx();
    report.push(`Deleted '${c.name}' (${n} items kept in library)`);
  }
}

const s = new Zotero.Search();
s.libraryID = lib;
s.addCondition('tag', 'is', 'zotmoov');
const ids = await s.search();
let removed = 0;
for (const id of ids) {
  const it = await Zotero.Items.getAsync(id);
  if (it.hasTag('zotmoov')) {
    it.removeTag('zotmoov');
    await it.saveTx();
    removed++;
  }
}
report.push(`Removed 'zotmoov' tag from ${removed} items`);

return report.join('\n');
