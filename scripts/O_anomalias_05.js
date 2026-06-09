// Script O — Anomalias residuais da Fase 0.5
// Data de criação: 2026-06-05
// Data de execução: PENDENTE
// Status: PENDENTE
// Output esperado: 2 movimentos + diagnóstico da sub faltante de Active Research
//
// Ações:
//   1. Mover `2024.2 Trab. Final Instituições e Desigualdades` → 4. Coursework / 2024-2 — Trab. Final Inst. & Desigualdades
//   2. Mesclar `Methodology` órfã (root) em ★ Theory & Methodology / Methodology
//   3. Listar subs atuais de 1. Active Research + identificar qual sumiu (sem recriar)

const lib = Zotero.Libraries.userLibraryID;
const log = [];

function findByName(name) {
  return Zotero.Collections.getByLibrary(lib, true).find(c => c.name === name && !c.parentID);
}
function findByPath(parts) {
  let p = null;
  for (const n of parts) {
    const cands = p ? p.getChildCollections() : Zotero.Collections.getByLibrary(lib).filter(c => !c.parentID);
    const f = cands.find(c => c.name === n);
    if (!f) return null;
    p = f;
  }
  return p;
}

// ===== STEP 1: 2024.2 Trab. Final → Coursework =====
const trabFinal = findByName('2024.2 Trab. Final Instituições e Desigualdades');
const coursework = findByName('4. Coursework');
if (!trabFinal) {
  log.push('SKIP STEP 1: pasta `2024.2 Trab. Final…` não está no root');
} else if (!coursework) {
  log.push('ERROR STEP 1: `4. Coursework` não encontrada');
} else {
  const nItems = trabFinal.getChildItems().length;
  trabFinal.name = '2024-2 — Trab. Final Inst. & Desigualdades';
  trabFinal.parentID = coursework.id;
  await trabFinal.saveTx();
  log.push(`MOVED: 2024.2 Trab. Final → 4. Coursework / 2024-2 — Trab. Final Inst. & Desigualdades (${nItems} items)`);
}

// ===== STEP 2: Methodology órfã → ★ Theory & Methodology / Methodology =====
const methOrphan = findByName('Methodology');
const methTarget = findByPath(['3. Fields', '★ Theory & Methodology', 'Methodology']);
if (!methOrphan) {
  log.push('SKIP STEP 2: `Methodology` órfã não está no root');
} else if (!methTarget) {
  log.push('ERROR STEP 2: target `Theory & Methodology / Methodology` não encontrada');
} else if (methOrphan.id === methTarget.id) {
  log.push('SKIP STEP 2: source e target são a mesma coleção');
} else {
  const items = methOrphan.getChildItems();
  let moved = 0, skipped = 0;
  for (const it of items) {
    let cids = it.getCollections();
    if (cids.includes(methTarget.id)) {
      skipped++;
    } else {
      cids.push(methTarget.id);
    }
    cids = cids.filter(id => id !== methOrphan.id);
    it.setCollections(cids);
    await it.saveTx();
    moved++;
  }
  // verifica antes de deletar
  if (methOrphan.getChildCollections().length === 0 && methOrphan.getChildItems().length === 0) {
    await methOrphan.eraseTx();
    log.push(`MERGED: Methodology órfã → ★ Theory & Methodology / Methodology (${moved} items, ${skipped} já estavam no target) + deleted órfã`);
  } else {
    log.push(`PARTIAL: Methodology órfã transferiu ${moved} items mas ainda tem ${methOrphan.getChildItems().length} items + ${methOrphan.getChildCollections().length} subs`);
  }
}

// ===== STEP 3: diagnóstico Active Research =====
const activeRes = findByName('1. Active Research');
if (!activeRes) {
  log.push('ERROR STEP 3: `1. Active Research` não encontrada');
} else {
  const subs = activeRes.getChildCollections().map(c => c.name).sort();
  const expected = [
    "Master's — ProUni & Affirmative Action",
    "2026 — BEPE Tarlau",
    "2026 — Methods Workshop",
    "IC FFLCH — Victor Alcantara"
  ];
  log.push('');
  log.push('=== STEP 3 — Active Research subs ===');
  log.push(`Atuais (${subs.length}):`);
  for (const s of subs) log.push(`  ✓ ${s}`);
  const missing = expected.filter(e => !subs.some(s => s === e));
  const unexpected = subs.filter(s => !expected.some(e => e === s));
  if (missing.length) {
    log.push(`Faltam (esperado mas não achei):`);
    for (const m of missing) log.push(`  ✗ ${m}`);
  }
  if (unexpected.length) {
    log.push(`Inesperados (achei mas não estava no esperado):`);
    for (const u of unexpected) log.push(`  ? ${u}`);
  }
  if (!missing.length && !unexpected.length) {
    log.push('OK: 4 subs esperadas todas presentes');
  }
}

return log.join('\n');
