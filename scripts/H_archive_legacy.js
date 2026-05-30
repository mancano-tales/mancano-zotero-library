// Script H — Diagnóstico topo + arquivar containers legados
// Data de criação: 2026-05-10
// Data de execução: 2026-05-10
// Status: EXECUTADO
// Output esperado: estado pré + arquivamento de 6+ containers + estado pós
//
// Resultado real (2026-05-10):
//   ARCHIVED 00_Important_reading (87 items + 4 subs)
//   ARCHIVED 01_Ongoing_Projects (10 items)
//   SKIPs (já não estavam no root): MancanoLibrary, ZZ_Old_Group_libs, 01_Ver, Sites, Bibliografia, Trab Final
//   Estado final: topo limpo só com pastas 1.-9. da nova estrutura

const lib = Zotero.Libraries.userLibraryID;
function findByName(n) {
  return Zotero.Collections.getByLibrary(lib, true).find(c => c.name === n && !c.parentID);
}
function fullPath(c) {
  const parts = [c.name];
  let p = c.parentID;
  while (p) {
    const par = Zotero.Collections.get(p);
    if (!par) break;
    parts.unshift(par.name);
    p = par.parentID;
  }
  return parts.join(' / ');
}

const log = [];
const archive = findByName('9. Archive');
if (!archive) return 'ERROR: 9. Archive not found';

const all = Zotero.Collections.getByLibrary(lib, true);

// === Diagnostic: top-level state ===
log.push('=== Top-level collections (current state) ===');
const allTop = Zotero.Collections.getByLibrary(lib)
  .filter(c => !c.parentID)
  .sort((a, b) => a.name.localeCompare(b.name));
for (const c of allTop) {
  log.push(`  ${c.name} [items=${c.getChildItems().length}, subs=${c.getChildCollections().length}]`);
}

// === Search Trab Final ===
log.push('\n=== Searching "Trab", "Final", "Instit", "Desigualdade" anywhere ===');
const trabSearch = all.filter(c => /trab|final|instit|desigualdade/i.test(c.name));
if (trabSearch.length === 0) {
  log.push('  (nothing matched)');
} else {
  for (const c of trabSearch) log.push(`  ${fullPath(c)}`);
}

// === ARCHIVE MOVES ===
log.push('\n=== ARCHIVE MOVES ===');
const toArchive = [
  'MancanoLibrary',
  'ZZ_Old_Group_libs',
  '00_Important_reading',
  '01_Ongoing_Projects',
  '01_Ver e Classificar as Novidades',
  'Sites e Redes Sociais',
  'Bibliografia',
  '2024.2 Trab. Final Instituições e Desigualdades',
];
for (const name of toArchive) {
  const c = findByName(name);
  if (!c) {
    log.push(`  SKIP ${name}: not at root`);
    continue;
  }
  c.parentID = archive.id;
  await c.saveTx();
  log.push(`  ARCHIVED: ${name} (items=${c.getChildItems().length}, subs=${c.getChildCollections().length})`);
}

// === Final state ===
log.push('\n=== Top-level AFTER archive ===');
const finalTop = Zotero.Collections.getByLibrary(lib)
  .filter(c => !c.parentID)
  .sort((a, b) => a.name.localeCompare(b.name));
for (const c of finalTop) {
  log.push(`  ${c.name} [items=${c.getChildItems().length}, subs=${c.getChildCollections().length}]`);
}

return log.join('\n');
