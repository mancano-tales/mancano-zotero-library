// Script F — Resolver Kenworthy + consolidar Active Research projects
// Data de criação: 2026-05-10
// Data de execução: 2026-05-10
// Status: EXECUTADO
// Output esperado: 7 operações (dd promovida, Kenworthy dissolvida, 4 projects merged, Trab Final)
//
// Resultado real (2026-05-10):
//   DD: promoted to 2026-05-07-temp (17 items)
//   KENWORTHY: 15 items → tag + dissolved
//   MERGED ProUni: 4 subs + 87 items
//   MERGED BEPE Tarlau: 35 items
//   MERGED Methods: 1 sub + 3 items
//   SKIP Victor (path errado — resolvido em Script G)
//   SKIP 2024.2 Trab. Final (já apagada)

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
const workbench = findByName('2. Workbench');
const coursework = findByName('4. Coursework');
if (!workbench || !coursework) return 'ERROR: targets missing';

// 1. dd → promote to Workbench
const dd = findByPath(['2. Workbench', '2026-05-03', 'Kenworthy', 'dd']);
if (dd) {
  const n = dd.getChildItems().length;
  dd.name = '2026-05-07-temp';
  dd.parentID = workbench.id;
  await dd.saveTx();
  log.push(`DD: promoted to 2026-05-07-temp (${n} items)`);
}

// 2. Kenworthy → tags + dissolve
const ken = findByPath(['2. Workbench', '2026-05-03', 'Kenworthy']);
if (ken) {
  if (ken.getChildCollections().length > 0) {
    log.push('KENWORTHY: still has subs, SKIP');
  } else {
    const items = ken.getChildItems();
    const pid = ken.parentID;
    for (const it of items) {
      it.addTag('author-focus:kenworthy');
      let cids = it.getCollections();
      if (pid && !cids.includes(pid)) cids.push(pid);
      cids = cids.filter(id => id !== ken.id);
      it.setCollections(cids);
      await it.saveTx();
    }
    await ken.eraseTx();
    log.push(`KENWORTHY: ${items.length} items → tag + dissolved`);
  }
}

// helper for merge
async function mergeInto(srcPath, dstPath) {
  const src = findByPath(srcPath);
  const dst = findByPath(dstPath);
  if (!src) return `SKIP: src ${srcPath.slice(-1)[0]} not found`;
  if (!dst) return `SKIP: dst ${dstPath.slice(-1)[0]} not found`;
  const subs = [...src.getChildCollections()];
  for (const s of subs) {
    s.parentID = dst.id;
    await s.saveTx();
  }
  const items = src.getChildItems();
  for (const it of items) {
    let cids = it.getCollections();
    if (!cids.includes(dst.id)) cids.push(dst.id);
    cids = cids.filter(id => id !== src.id);
    it.setCollections(cids);
    await it.saveTx();
  }
  const remainingSubs = src.getChildCollections().length;
  const remainingItems = src.getChildItems().length;
  if (remainingSubs === 0 && remainingItems === 0) {
    await src.eraseTx();
    return `MERGED: ${srcPath.slice(-1)[0]} → ${dstPath.slice(-1)[0]} (${subs.length} subs + ${items.length} items)`;
  }
  return `PARTIAL: ${srcPath.slice(-1)[0]} → ${dstPath.slice(-1)[0]} (${remainingSubs} subs, ${remainingItems} items remain in src)`;
}

// 3. Consolidate Active Research projects
log.push(await mergeInto(
  ['01_Ongoing_Projects', '2026_01_ProUni_Cotas_Policy_Process'],
  ['1. Active Research', "Master's — ProUni & Affirmative Action"]
));
log.push(await mergeInto(
  ['01_Ongoing_Projects', 'BEPE Tarlau'],
  ['1. Active Research', 'BEPE — Tarlau (2026)']
));
log.push(await mergeInto(
  ['01_Ongoing_Projects', '2026_05 Research Methods'],
  ['1. Active Research', 'Methods Workshop (2026)']
));
log.push(await mergeInto(
  ['01_Ver e Classificar as Novidades', 'IC na FFLCH - Victor Alcantara'],
  ['1. Active Research', 'IC FFLCH — Victor Alcantara']
));

// 4. 2024.2 Trab. Final → Coursework
const tf = findByPath(['2024.2 Trab. Final Instituições e Desigualdades']);
if (tf) {
  tf.name = 'Trab. Final — Inst. & Desigualdades — 2024-2';
  tf.parentID = coursework.id;
  await tf.saveTx();
  log.push('COURSEWORK: 2024.2 Trab. Final → moved + renamed');
} else {
  log.push('SKIP: 2024.2 Trab. Final not found');
}

return log.join('\n') + `\n\nTotal: ${log.length} operations`;
