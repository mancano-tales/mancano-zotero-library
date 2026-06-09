// Script P2 — Cleanup `Problematic - No author` (versão batched + por ID)
// Data de criação: 2026-06-05
// Data de execução: PENDENTE
// Status: PENDENTE
// Output esperado: remove até 50 itens com creator (parcial — rodar 2x se necessário)
//
// Bug do Script P: rodou 35 itens e parou (provavelmente lentidão acumulada com
// 76+ saveTx em sequência fazendo Zotero ficar irresponsivo).
// Estado atual (LIVE DB):
//   Problematic - No author (id=272): 76 itens, 49 com creator, 27 sem
// Esperado: este script remove ~49 com creator. Se houver mais que BATCH_SIZE,
// rodar de novo.

const PROB_COLL_ID = 272;
const BATCH_SIZE = 50;  // processa até 50 itens por execução

const coll = Zotero.Collections.get(PROB_COLL_ID);
if (!coll) return `SKIP: collection id=${PROB_COLL_ID} não encontrada`;

const items = coll.getChildItems();
const log = [];
log.push(`Coleção "Problematic - No author" (id=${PROB_COLL_ID}): ${items.length} itens totais`);

let removed = 0;
let semCreator = 0;
let processed = 0;

for (const it of items) {
  if (processed >= BATCH_SIZE) {
    log.push('');
    log.push(`⏸ BATCH LIMIT atingido (${BATCH_SIZE}). Rode o script de novo pra continuar.`);
    break;
  }
  const nCreators = it.getCreators().length;
  if (nCreators > 0) {
    // resolvido — remove desta coleção
    let cids = it.getCollections().filter(id => id !== PROB_COLL_ID);
    it.setCollections(cids);
    await it.saveTx();
    removed++;
  } else {
    semCreator++;
  }
  processed++;
}

// re-fetch contagem
const after = coll.getChildItems().length;
log.push(`Processados nesta rodada: ${processed}`);
log.push(`  Removidos (com creator): ${removed}`);
log.push(`  Mantidos (sem creator, ignorados): ${semCreator}`);
log.push(`Itens restantes na coleção: ${after}`);

if (after === 0) {
  await coll.eraseTx();
  log.push('');
  log.push('✓ Coleção esvaziada e DELETADA');
} else if (after < 30) {
  // listar residuais (provável que sejam só os sem-creator)
  log.push('');
  log.push('=== Residuais (rodar de novo se houver removíveis ainda) ===');
  const stillThere = coll.getChildItems();
  for (const it of stillThere.slice(0, 30)) {
    const nc = it.getCreators().length;
    const title = (it.getField('title') || '(sem título)').substring(0, 60);
    log.push(`  id=${it.id} creators=${nc} title="${title}"`);
  }
  if (stillThere.length > 30) log.push(`  ... e mais ${stillThere.length - 30}`);
}

return log.join('\n');
