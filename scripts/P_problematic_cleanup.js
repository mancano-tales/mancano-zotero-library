// Script P — Cleanup da coleção `Problematic - No author`
// Data de criação: 2026-06-05
// Data de execução: PENDENTE
// Status: PENDENTE
// Output esperado: itens com creator removidos da coleção; coleção deletada se sobrar 0
//
// Decisão do user (06/05): "Remover de Problematic (sai do radar)" — itens resolvidos
// são removidos da coleção. Se sobrar 0, apago. Se sobrar Y > 0, mantém + lista.

const lib = Zotero.Libraries.userLibraryID;
const log = [];

const all = Zotero.Collections.getByLibrary(lib, true);
const probColl = all.find(c => c.name === 'Problematic - No author');
if (!probColl) {
  return 'SKIP: coleção `Problematic - No author` não existe (já removida).';
}

const items = probColl.getChildItems();
log.push(`Coleção "Problematic - No author" (id=${probColl.id}): ${items.length} itens`);

let removed = 0;
const residuais = [];
for (const it of items) {
  const creators = it.getCreators();
  if (creators.length > 0) {
    // resolvido — remove desta coleção
    let cids = it.getCollections().filter(id => id !== probColl.id);
    it.setCollections(cids);
    await it.saveTx();
    removed++;
  } else {
    // ainda sem creator — listar
    const title = (it.getField('title') || '(sem título)').substring(0, 70);
    residuais.push({ id: it.id, key: it.key, title: title });
  }
}

log.push(`Removidos (com creator): ${removed}`);
log.push(`Residuais (ainda sem creator): ${residuais.length}`);

if (residuais.length === 0) {
  await probColl.eraseTx();
  log.push(`✓ Coleção esvaziada e DELETADA`);
} else {
  log.push('');
  log.push('=== ITENS RESIDUAIS (sem creator — precisam do user) ===');
  for (const r of residuais) {
    log.push(`  id=${r.id} key=${r.key} title="${r.title}"`);
  }
  log.push('');
  log.push(`Coleção mantida com ${residuais.length} itens. Revisar no Zotero pela UI.`);
}

return log.join('\n');
