// Script E — Diagnóstico Kenworthy (read-only)
// Data de criação: 2026-05-10
// Data de execução: 2026-05-10
// Status: EXECUTADO (read-only)
// Output esperado: estado de Kenworthy após Script D — itens + subpastas
//
// Resultado real: Kenworthy tinha subpasta `dd` com 17 itens variados
// (incluindo George & Bennett "Case Studies and Theory Development")
// → decidiu-se promover dd a Workbench próprio (Script F)

const lib = Zotero.Libraries.userLibraryID;
function findByPath(pathParts) {
  let p = null;
  for (const n of pathParts) {
    const cands = p ? p.getChildCollections() : Zotero.Collections.getByLibrary(lib).filter(c => !c.parentID);
    const f = cands.find(c => c.name === n);
    if (!f) return null;
    p = f;
  }
  return p;
}

const ken = findByPath(['2. Workbench', '2026-05-03', 'Kenworthy']);
if (!ken) return 'Kenworthy not found at [2. Workbench / 2026-05-03 / Kenworthy]';

const items = ken.getChildItems();
const subs = ken.getChildCollections();
let r = `KENWORTHY:\n  ${items.length} direct items\n  ${subs.length} subcollections:\n`;
for (const s of subs) {
  const si = s.getChildItems();
  r += `\n  ▸ "${s.name}" (${si.length} items)\n`;
  for (const it of si.slice(0, 5)) {
    r += `      • ${it.getDisplayTitle().substring(0, 90)}\n`;
  }
  if (si.length > 5) r += `      … +${si.length - 5} more\n`;
}
return r;
