// Script I — Popular Coursework, Bureaucracy, Leisure Reading + criar AI Outputs
// Data de criação: 2026-05-10
// Data de execução: PENDENTE (não foi rodado em 10/05; verificar em 30/05 se ainda relevante)
// Status: PENDENTE
// Output esperado: ~7 operações (TMCP, AI Outputs, 2 Leisure Reading, 2 Bureaucracy merges)
//
// O quê:
//   - TMCP (Adrian Lavalle) → 4. Coursework / 2024-1 — TMCP (Adrian Lavalle)
//   - AI Pages → 7. Misc / AI Outputs
//   - Leituras Engajantes → 6. Leisure Reading
//   - Literatura e Jornalismo (com Piaui) → 6. Leisure Reading
//   - CVs (1 item) → 5. Bureaucracy & Documents / CVs
//   - Documentos (2 itens) → 5. Bureaucracy & Documents / My Documents
//
// Atenção: paths assumem estado pós-Script H (containers legados sob 9. Archive).
// Se algum SKIP aparecer, é porque o user já moveu/apagou manualmente.

const lib = Zotero.Libraries.userLibraryID;
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
function findByName(n) {
  return Zotero.Collections.getByLibrary(lib, true).find(c => c.name === n && !c.parentID);
}

const log = [];

const coursework = findByName('4. Coursework');
const leisure = findByName('6. Leisure Reading');
const misc = findByName('7. Misc');
const bureauCVs = findByPath(['5. Bureaucracy & Documents', 'CVs']);
const bureauMyDocs = findByPath(['5. Bureaucracy & Documents', 'My Documents']);
if (!coursework || !leisure || !misc || !bureauCVs || !bureauMyDocs) {
  return `ERROR targets: cw=${!!coursework} lr=${!!leisure} misc=${!!misc} cvs=${!!bureauCVs} md=${!!bureauMyDocs}`;
}

async function moveCol(srcPath, newName, newParent) {
  const c = findByPath(srcPath);
  if (!c) { log.push(`SKIP move: ${srcPath.slice(-1)[0]} not found`); return null; }
  const oldName = c.name;
  if (newName) c.name = newName;
  c.parentID = newParent.id;
  await c.saveTx();
  log.push(`MOVED: ${oldName} → ${c.name} (under ${newParent.name})`);
  return c;
}

async function mergeItems(srcPath, dst, deleteSrc) {
  const src = findByPath(srcPath);
  if (!src) { log.push(`SKIP merge: ${srcPath.slice(-1)[0]} not found`); return; }
  const items = src.getChildItems();
  for (const it of items) {
    let cids = it.getCollections();
    if (!cids.includes(dst.id)) cids.push(dst.id);
    cids = cids.filter(id => id !== src.id);
    it.setCollections(cids);
    await it.saveTx();
  }
  if (deleteSrc && src.getChildCollections().length === 0 && src.getChildItems().length === 0) {
    await src.eraseTx();
    log.push(`MERGED+DEL: ${srcPath.slice(-1)[0]} → ${dst.name} (${items.length} items)`);
  } else {
    log.push(`MERGED: ${srcPath.slice(-1)[0]} → ${dst.name} (${items.length} items)`);
  }
}

// === Coursework ===
await moveCol(
  ['9. Archive', 'MancanoLibrary', '8 Disciplinas', 'TMCP - Adrian Lavalle'],
  '2024-1 — TMCP (Adrian Lavalle)',
  coursework
);

// === AI Outputs (novo subfolder em Misc) ===
await moveCol(
  ['9. Archive', 'MancanoLibrary', '8 Disciplinas', 'AI Pages'],
  'AI Outputs',
  misc
);

// === Leisure Reading ===
await moveCol(
  ['9. Archive', 'MancanoLibrary', '3. Topics & Contries', 'Leituras Engajantes'],
  null,
  leisure
);
await moveCol(
  ['9. Archive', 'MancanoLibrary', 'Literatura e Jornalismo'],
  null,
  leisure
);

// === Bureaucracy ===
await mergeItems(
  ['9. Archive', 'MancanoLibrary', 'Miscelanea', 'CVs'],
  bureauCVs, true
);
await mergeItems(
  ['9. Archive', '00_Important_reading', '01_Ver e Classificar as Novidades', 'Documentos'],
  bureauMyDocs, true
);

return log.join('\n') + `\n\nTotal: ${log.length} ops`;
