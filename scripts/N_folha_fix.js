// Script N — Folha de S.Paulo fix (fm=0 errado + sem creator)
// Data de criação: 2026-06-05
// Data de execução: PENDENTE
// Status: PENDENTE
// Output esperado: 4 fixes (2 fm=0→fm=1 + 2 sem creator) + lista de URL/date pendente manual
//
// Baseado em diagnostics/2026-06-06_folha_audit.md:
//   FIX fm=0 (2): ids 12442, 12468 — creator 'Folha'/'de S.Paulo' fm=0 → trocar
//   FIX sem creator (2): ids 468, 530 — adicionar 'Folha de S.Paulo' fm=1
//   FIX sem URL (1): id 12432 — só listar, user resolve manual

const lib = Zotero.Libraries.userLibraryID;
const log = [];

// ===== STEP 1: trocar fm=0 → fm=1 (ids 12442, 12468) =====
const fixFm0Ids = [12442, 12468];
for (const id of fixFm0Ids) {
  const item = await Zotero.Items.getAsync(id);
  if (!item) { log.push(`SKIP fm=0 id=${id}: item not found`); continue; }

  const creators = item.getCreators();
  // remove o creator buggy: lastName="de S.Paulo" + firstName="Folha" + fieldMode=0
  const filtered = creators.filter(c =>
    !(c.fieldMode === 0 && (c.lastName || "").trim() === "de S.Paulo" && (c.firstName || "").trim() === "Folha")
  );
  const removed = creators.length - filtered.length;

  if (removed === 0) {
    log.push(`SKIP id=${id}: creator buggy não achado (já corrigido?)`);
    continue;
  }

  // adiciona o creator correto (institucional fm=1) na posição do que foi removido
  filtered.push({
    creatorTypeID: Zotero.CreatorTypes.getID('author'),
    lastName: "Folha de S.Paulo",
    firstName: "",
    fieldMode: 1
  });

  item.setCreators(filtered);
  await item.saveTx();
  log.push(`FIX fm=0 → fm=1 id=${id}: removed ${removed} buggy + added institucional`);
}

// ===== STEP 2: adicionar institucional fm=1 (ids 468, 530) =====
const fixSemCreatorIds = [468, 530];
for (const id of fixSemCreatorIds) {
  const item = await Zotero.Items.getAsync(id);
  if (!item) { log.push(`SKIP sem-creator id=${id}: item not found`); continue; }

  const existing = item.getCreators();
  if (existing.length > 0) {
    log.push(`SKIP id=${id}: já tem ${existing.length} creator(s) (alguém adicionou)`);
    continue;
  }

  item.setCreators([{
    creatorTypeID: Zotero.CreatorTypes.getID('author'),
    lastName: "Folha de S.Paulo",
    firstName: "",
    fieldMode: 1
  }]);
  await item.saveTx();
  log.push(`ADD institucional id=${id}: creator 'Folha de S.Paulo' fm=1`);
}

// ===== STEP 3: reportar item sem URL pra fix manual =====
log.push("");
log.push("=== PENDENTE MANUAL — itens sem URL (user resolve no Zotero UI) ===");
const semUrlIds = [12432];
for (const id of semUrlIds) {
  const item = await Zotero.Items.getAsync(id);
  if (!item) { log.push(`  id=${id}: item not found`); continue; }
  const t = item.getField('title') || '(sem título)';
  const d = item.getField('date') || '(sem data)';
  log.push(`  id=${id}  date=${d}  title="${t.substring(0,60)}"`);
  log.push(`    → adicione URL no campo URL do item (provavelmente folha.uol.com.br/...)`);
}

return log.join('\n') + `\n\nTotal fixes: ${log.filter(l => l.startsWith('FIX') || l.startsWith('ADD')).length}`;
