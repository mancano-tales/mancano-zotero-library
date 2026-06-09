// Script K — Mover blogs ABNT/TCC de baixa qualidade para lixeira
// Data de criação: 2026-05-30
// Data de execução: 2026-05-30
// Status: EXECUTADO
// Output esperado: 7 itens movidos para a lixeira (reversível 30 dias).
//
// Contexto:
//   Parte da Fase 0.5. Balde B da triagem (python/classify_problematic.py).
//   Itens são webpages/blogs sobre normas ABNT em sites de baixa qualidade
//   (mettzer, viacarreira, tecnoblog etc.) — não são fonte acadêmica;
//   o user pode buscar a ABNT direto se precisar.
//
// O quê:
//   Mostra confirm() listando os 7 itens; se OK, move tudo para lixeira.
//   Usa trashTx() (reversível por 30 dias, NÃO delete permanente).
//
// Lista (sites identificados como baixa qualidade):
//   373 [webpage]    Margens e espaçamento nas normas ABNT  (blog.mettzer.com)
//   375 [webpage]    Referências                            (normastecnicas.com)
//   376 [blogPost]   Sumário nas Normas da ABNT             (blog.fastformat.co)
//   379 [webpage]    Nota de rodapé no TCC                  (viacarreira.com)
//   382 [webpage]    Como fazer citações no TCC             (viacarreira.com)
//   383 [blogPost]   Como fazer Referência Bibliográfica    (projetoacademico.com.br)
//   388 [webpage]    Como fazer referência de site          (tecnoblog.net)
//
// Resultado real (2026-05-30): ✓ 7 itens movidos para a lixeira.

const IDS = [373, 375, 376, 379, 382, 383, 388];
const TITLES = ["[webpage] Margens e espaçamento nas normas ABNT", "[webpage] Referências", "[blogPost] Sumário nas Normas da ABNT", "[webpage] Nota de rodapé no TCC: como usar? O que diz a ABNT?", "[webpage] Como fazer citações no TCC (Normas ABNT)", "[blogPost] Como fazer Referência Bibliográfica de Site: normas ABNT, TCC e exemplos", "[webpage] Como fazer referência de site nas normas ABNT em trabalhos acadêmicos"];

let log = ["=== BALDE B — candidatos a lixeira ==="];
for (let i = 0; i < IDS.length; i++) {
  log.push(`  [${IDS[i]}] ${TITLES[i]}`);
}
log.push(`Total: ${IDS.length} itens.`);
log.push("");
log.push("Estes itens vão para a LIXEIRA do Zotero (reversível por 30 dias).");
log.push("Para deletar permanentemente depois: clicar com botão direito na lixeira > Empty Trash.");

const proceed = confirm(log.join("\n") + "\n\nMover esses " + IDS.length + " itens para a lixeira?");
if (!proceed) return "Cancelado pelo usuário.";

await Zotero.Items.trashTx(IDS);
return `✓ ${IDS.length} itens movidos para a lixeira.`;
