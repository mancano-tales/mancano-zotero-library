// Script D — Migração Workbench + autores + coursework + reposicionamentos
// Data de criação: 2026-05-10
// Data de execução: 2026-05-10
// Status: EXECUTADO
// Output esperado: ~32 operações (8 autores + 20 renames + 2 coursework + 1 project + 1 theme)
//
// Resultado real (2026-05-10):
//   - Kenworthy SKIPPED (subpasta dd) — resolvido depois em Script E/F
//   - Demais 31 ops bem-sucedidas
//
// Reversibilidade: renames são triviais; eraseTx vai pra lixeira (30 dias)

const lib = Zotero.Libraries.userLibraryID;

function findByPath(pathParts) {
  let parent = null;
  for (const partName of pathParts) {
    const candidates = parent
      ? parent.getChildCollections()
      : Zotero.Collections.getByLibrary(lib).filter(c => !c.parentID);
    const found = candidates.find(c => c.name === partName);
    if (!found) return null;
    parent = found;
  }
  return parent;
}
function findByName(name) {
  return Zotero.Collections.getByLibrary(lib, true).find(c => c.name === name && !c.parentID);
}

const log = [];
const workbench = findByName('2. Workbench');
const coursework = findByName('4. Coursework');
const histInst = findByPath(['3. Fields', '★ Theory & Methodology', 'Theory', 'Theoretical Paradigms', 'Historical Institutionalism']);
const masterProj = findByPath(['1. Active Research', "Master's — ProUni & Affirmative Action"]);

if (!workbench || !coursework || !histInst || !masterProj) {
  return `ERROR: missing target. workbench=${!!workbench} coursework=${!!coursework} histInst=${!!histInst} masterProj=${!!masterProj}`;
}

// === STEP 1: Author folders → tags ===
const authorOps = [
  {path: ['01_Ver e Classificar as Novidades', 'Janet Gornick'], tag: 'author-focus:gornick'},
  {path: ['01_Ver e Classificar as Novidades', '00_2025-10-17', 'Carnoy'], tag: 'author-focus:carnoy'},
  {path: ['01_Ver e Classificar as Novidades', '00_2025-10-17', 'Julian'], tag: 'author-focus:garritzmann'},
  {path: ['01_Ver e Classificar as Novidades', '00_2025-10-17', '00_2025-12-15', 'Agustina Paglayan'], tag: 'author-focus:paglayan'},
  {path: ['01_Ver e Classificar as Novidades', '00_2025-10-17', '00_2025-12-15', 'Bernardo Mançano'], tag: 'author-focus:mancano'},
  {path: ['00_Important_reading', 'Temp', '2026-05-03', 'Kenworthy'], tag: 'author-focus:kenworthy'},
  {path: ['00_Important_reading', 'Temp', 'Temp6', 'Podolny'], tag: 'author-focus:podolny'},
  {path: ['00_Important_reading', 'Temp', '2026-04-23', 'Hemerick'], tag: 'author-focus:hemerick'},
];
for (const op of authorOps) {
  const c = findByPath(op.path);
  if (!c) { log.push(`SKIP author ${op.path.slice(-1)[0]}: not found`); continue; }
  if (c.getChildCollections().length > 0) {
    log.push(`SKIP author ${c.name}: still has subcollections`); continue;
  }
  const parentId = c.parentID;
  const items = c.getChildItems();
  for (const it of items) {
    it.addTag(op.tag);
    let cids = it.getCollections();
    if (parentId && !cids.includes(parentId)) cids.push(parentId);
    cids = cids.filter(id => id !== c.id);
    it.setCollections(cids);
    await it.saveTx();
  }
  await c.eraseTx();
  log.push(`AUTHOR: ${c.name} (${items.length} items) → tag ${op.tag}`);
}

// === STEP 2: Rename + reparent temp folders to Workbench ===
const renameOps = [
  {path: ['01_Ver e Classificar as Novidades', '00_2025-10-17'], newName: '2025-10-17'},
  {path: ['01_Ver e Classificar as Novidades', '00_2025-10-17', '00_2025-12-15'], newName: '2025-12-15'},
  {path: ['01_Ver e Classificar as Novidades', '00_2025-10-17', '2025-11-24'], newName: '2025-11-24'},
  {path: ['01_Ver e Classificar as Novidades', '00_2025-10-17', '2026-01-02'], newName: '2026-01-02'},
  {path: ['01_Ver e Classificar as Novidades', '00_2025-10-17', '2026-01-13'], newName: '2026-01-13'},
  {path: ['00_Important_reading', 'Temp', 'temp3-2026-03-03'], newName: '2026-03-03'},
  {path: ['00_Important_reading', 'Temp', 'temp5-2026-03-24'], newName: '2026-03-24'},
  {path: ['00_Important_reading', 'Temp', '2026-04-23'], newName: '2026-04-23'},
  {path: ['00_Important_reading', 'Temp', '2026-05-03'], newName: '2026-05-03'},
  {path: ['00_Important_reading', 'Temp', '2026-05-07-Temp10'], newName: '2026-05-07'},
  {path: ['MancanoLibrary', 'Temp', 'Temp2'], newName: '2025-06-23-temp'},
  {path: ['MancanoLibrary', 'Temp'], newName: '2025-06-23-temp-2'},
  {path: ['MancanoLibrary', 'Temp', 'temp5-18'], newName: '2025-05-20-temp'},
  {path: ['00_Important_reading', 'Temp'], newName: '2026-02-22-temp'},
  {path: ['00_Important_reading', 'Temp', 'Temp2'], newName: '2026-03-05-temp'},
  {path: ['00_Important_reading', 'Temp', 'Temp4'], newName: '2026-03-13-temp'},
  {path: ['00_Important_reading', 'Temp', 'Temp6'], newName: '2026-04-23-temp'},
  {path: ['00_Important_reading', 'Temp', 'Temp6', 'Temp6'], newName: '2026-04-19-temp'},
  {path: ['00_Important_reading', 'Temp', 'Temp7'], newName: '2026-04-20-temp'},
  {path: ['00_Important_reading', 'Temp', '2026-04-23', 'Temp9'], newName: '2026-05-02-temp'},
];
for (const op of renameOps) {
  const c = findByPath(op.path);
  op.id = c ? c.id : null;
}
for (const op of renameOps) {
  if (!op.id) { log.push(`SKIP rename ${op.path.slice(-1)[0]}: not found`); continue; }
  const c = Zotero.Collections.get(op.id);
  const oldName = c.name;
  c.name = op.newName;
  c.parentID = workbench.id;
  await c.saveTx();
  log.push(`WORKBENCH: ${oldName} → ${op.newName}`);
}

// === STEP 3: Coursework moves ===
const courseOps = [
  {path: ['MancanoLibrary', '0. Education', '2025-10-200 História da Educação no Brasil FEUSP'],
   newName: 'História da Educação FEUSP — 2025-2'},
  {path: ['2. Workbench', '2025-10-17', '440B Comparative Political Economi'],
   newName: '440B Comparative Political Economy — 2026-1'},
];
for (const op of courseOps) {
  const c = findByPath(op.path);
  if (!c) { log.push(`SKIP course ${op.path.slice(-1)[0]}: not found`); continue; }
  const oldName = c.name;
  c.name = op.newName;
  c.parentID = coursework.id;
  await c.saveTx();
  log.push(`COURSEWORK: ${oldName} → ${op.newName}`);
}

// === STEP 4: Project subfolder ===
const baseLinha = findByPath(['01_Ongoing_Projects', '2026_01_ProUni_Cotas_Policy_Process', 'Base para a Linha do Tempo']);
if (baseLinha) {
  baseLinha.parentID = masterProj.id;
  await baseLinha.saveTx();
  log.push(`PROJECT: Base para a Linha do Tempo → Master's project`);
}

// === STEP 5: Theme move ===
const politicsTime = findByPath(['2. Workbench', '2025-10-17', 'Politics and Time']);
if (politicsTime) {
  politicsTime.parentID = histInst.id;
  await politicsTime.saveTx();
  log.push(`THEME: Politics and Time → Historical Institutionalism`);
}

return log.join('\n') + `\n\nTotal: ${log.length} operations`;
