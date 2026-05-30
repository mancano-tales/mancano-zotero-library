// Script G — Convenção data-primeiro + recuperar Victor & Trab. Final
// Data de criação: 2026-05-10
// Data de execução: 2026-05-10
// Status: EXECUTADO
// Output esperado: 4 renames + 1 merge (Victor) + 1 SKIP (Trab Final já apagada)
//
// Resultado real (2026-05-10):
//   4 RENAMED (BEPE, Methods, 440B, Hist Educação)
//   MERGED Victor: IC na FFLCH - Victor Alcantara → IC FFLCH — Victor Alcantara (7 items)
//   Trab Final not found

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

// === STEP 1: Renames pra padrão "data-primeiro" ===
const renames = [
  ['BEPE — Tarlau (2026)', '2026 — BEPE Tarlau'],
  ['Methods Workshop (2026)', '2026 — Methods Workshop'],
  ['440B Comparative Political Economy — 2026-1', '2026-1 — 440B Comparative Political Economy'],
  ['História da Educação FEUSP — 2025-2', '2025-2 — História da Educação FEUSP'],
];
for (const [oldN, newN] of renames) {
  const m = Zotero.Collections.getByLibrary(lib, true).find(c => c.name === oldN);
  if (m) {
    m.name = newN; await m.saveTx();
    log.push(`RENAMED: ${oldN} → ${newN}`);
  } else {
    log.push(`SKIP rename: '${oldN}' not found`);
  }
}

// === STEP 2: Victor — diagnóstico + retry merge ===
log.push('\n--- VICTOR ---');
const victors = Zotero.Collections.getByLibrary(lib, true).filter(c => /victor/i.test(c.name));
for (const v of victors) log.push(`  ${fullPath(v)} (items=${v.getChildItems().length})`);
const activeRes = findByName('1. Active Research');
const vTarget = activeRes ? activeRes.getChildCollections().find(c => /victor/i.test(c.name)) : null;
const vSrcs = victors.filter(c => !vTarget || c.id !== vTarget.id);
if (vTarget && vSrcs.length > 0) {
  for (const src of vSrcs) {
    const subs = [...src.getChildCollections()];
    for (const s of subs) { s.parentID = vTarget.id; await s.saveTx(); }
    const items = src.getChildItems();
    for (const it of items) {
      let cids = it.getCollections();
      if (!cids.includes(vTarget.id)) cids.push(vTarget.id);
      cids = cids.filter(id => id !== src.id);
      it.setCollections(cids);
      await it.saveTx();
    }
    if (src.getChildCollections().length === 0 && src.getChildItems().length === 0) {
      await src.eraseTx();
      log.push(`MERGED Victor: ${src.name} → ${vTarget.name} (${items.length} items)`);
    }
  }
}

// === STEP 3: Trab. Final — diagnóstico + retry ===
log.push('\n--- TRAB. FINAL ---');
const trabs = Zotero.Collections.getByLibrary(lib, true).filter(c => /trab.*final|2024.*inst.*desigualdade/i.test(c.name));
for (const t of trabs) log.push(`  ${fullPath(t)} (items=${t.getChildItems().length})`);
const coursework = findByName('4. Coursework');
const trabExisting = coursework ? coursework.getChildCollections().find(c => /trab.*final/i.test(c.name)) : null;
const trabSrcs = trabs.filter(c => !trabExisting || c.id !== trabExisting.id);
if (coursework && trabSrcs.length === 1) {
  const src = trabSrcs[0];
  src.name = '2024-2 — Trab. Final Inst. & Desigualdades';
  src.parentID = coursework.id;
  await src.saveTx();
  log.push(`COURSEWORK: moved + renamed`);
} else if (trabSrcs.length > 1) {
  log.push(`MULTIPLE Trab matches — preciso revisar`);
} else if (trabSrcs.length === 0) {
  log.push(`No Trab Final source found`);
}

return log.join('\n');
