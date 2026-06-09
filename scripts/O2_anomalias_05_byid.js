// Script O2 — Anomalias residuais (versão por ID — corrige falha do Script O)
// Data de criação: 2026-06-05
// Data de execução: PENDENTE
// Status: PENDENTE
// Output esperado: 2 movimentos + diagnóstico Active Research
//
// O Script O original buscava por nome e falhou (provavelmente Unicode mismatch
// no 'ç' de "Instituições" ou 'Methodology' com whitespace).
// Esta versão usa collectionID direto, descobertos via SQL na live DB:
//   - 2024.2 Trab. Final: id=5 (root) → mover pra 4. Coursework (id=262)
//   - Methodology órfã: id=275 (root) → mesclar em 3. Fields/★ T&M/Methodology (id=233)
//   - Active Research: id=216

const COURSEWORK_ID = 262;
const TRAB_FINAL_ID = 5;
const METH_ORPHAN_ID = 275;
const METH_TARGET_ID = 233;
const ACTIVE_RES_ID = 216;

const log = [];

// ===== STEP 1: 2024.2 Trab Final → 4. Coursework =====
const trabFinal = Zotero.Collections.get(TRAB_FINAL_ID);
const coursework = Zotero.Collections.get(COURSEWORK_ID);
if (!trabFinal) {
  log.push(`SKIP STEP 1: collection id=${TRAB_FINAL_ID} não encontrada`);
} else {
  const nItems = trabFinal.getChildItems().length;
  const oldName = trabFinal.name;
  trabFinal.name = '2024-2 — Trab. Final Inst. & Desigualdades';
  trabFinal.parentID = coursework.id;
  await trabFinal.saveTx();
  log.push(`MOVED: "${oldName}" (${nItems} items) → 4. Coursework / "${trabFinal.name}"`);
}

// ===== STEP 2: Methodology órfã → ★ T&M / Methodology =====
const methOrphan = Zotero.Collections.get(METH_ORPHAN_ID);
const methTarget = Zotero.Collections.get(METH_TARGET_ID);
if (!methOrphan || !methTarget) {
  log.push(`SKIP STEP 2: orphan=${!!methOrphan} target=${!!methTarget}`);
} else if (methOrphan.id === methTarget.id) {
  log.push('SKIP STEP 2: source e target são a mesma coleção');
} else {
  const items = methOrphan.getChildItems();
  let moved = 0, alreadyIn = 0;
  for (const it of items) {
    let cids = it.getCollections();
    if (!cids.includes(methTarget.id)) {
      cids.push(methTarget.id);
    } else {
      alreadyIn++;
    }
    cids = cids.filter(id => id !== methOrphan.id);
    it.setCollections(cids);
    await it.saveTx();
    moved++;
  }
  // Verifica antes de deletar
  if (methOrphan.getChildCollections().length === 0 && methOrphan.getChildItems().length === 0) {
    await methOrphan.eraseTx();
    log.push(`MERGED: Methodology órfã (${items.length} items, ${alreadyIn} já estavam no target) → deleted órfã`);
  } else {
    log.push(`PARTIAL: Methodology órfã: ${methOrphan.getChildItems().length} items + ${methOrphan.getChildCollections().length} subs residuais`);
  }
}

// ===== STEP 3: diagnóstico Active Research =====
const activeRes = Zotero.Collections.get(ACTIVE_RES_ID);
if (!activeRes) {
  log.push(`ERROR STEP 3: Active Research id=${ACTIVE_RES_ID} not found`);
} else {
  const subs = activeRes.getChildCollections().map(c => c.name).sort();
  log.push('');
  log.push('=== STEP 3 — 1. Active Research subs ===');
  log.push(`Atuais (${subs.length}):`);
  for (const s of subs) log.push(`  ✓ ${s}`);

  // BEPE foi movido pra dentro de Master's ProUni (visto na query SQL)
  // Então o esperado mudou. Vamos só listar.
  log.push('');
  log.push('Nota: na query SQL pré-execução, "2026 — BEPE Tarlau" estava em');
  log.push('1. Active Research / Master\'s — ProUni & Affirmative Action / 2026 — BEPE Tarlau');
  log.push('(provavelmente movido manualmente). Confirmar se é proposital.');
}

return log.join('\n');
