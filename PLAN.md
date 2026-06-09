# PLAN — Plano vivo

> **Visão geral do projeto**: ver `README.md`. **Histórico**: ver `NEWS.md`.
> Este arquivo é a **fonte da verdade** sobre o que falta fazer e em que ordem.

## Estado atual (diagnóstico: 2026-05-30 — `diagnostics/2026-05-30_relatorio.md`)

Estrutura no topo da biblioteca (11 raízes, vs. 9 esperadas — 4 anomalias):

```
0. Problem                                          [14 itens, 1 sub]  ← NOVA (user criou)
1. Active Research                                  [0 itens, 3 subs]  ← faltando 1 sub (esperado 4)
2. Workbench                                        [0 itens, 21 subs]
2024.2 Trab. Final Instituições e Desigualdades    [41 itens, 0 subs] ← VOLTOU no root (não foi movida em 10/05)
3. Fields                                           [0 itens, 5 subs]
4. Coursework                                       [0 itens, 2 subs]
5. Bureaucracy & Documents                          [0 itens, 5 subs]
6. Leisure Reading                                  [0 itens, 0 subs]
7. Misc                                             [0 itens, 0 subs]
9. Archive                                          [0 itens, 4 subs]
Methodology                                         [7 itens, 0 subs]  ← ÓRFÃ (deveria estar dentro de ★ Theory & Methodology)
```

**Métricas — diff vs. baseline + meta:**

| Métrica | 09/05 (baseline) | 30/05 (atual) | Meta |
|---------|-----------------:|--------------:|-----:|
| Itens bibliográficos | 2.337 | 2.348 | — |
| Duplicatas DOI | 59 | 60 | <5 |
| Duplicatas ISBN | 43 | 45 | <5 |
| Duplicatas título+ano | 99 | 107 | <10 |
| Artigos sem DOI | 274 | 283 | <30 |
| Livros sem ISBN | 98 | 97 | <20 |
| Itens fora de coleção | 157 | 232 | <50 |
| Tags variantes caixa | 14 | 14 | 0 |
| Anexos órfãos | 241 | 237 | <30 |
| Sem autor | 288 | **245** ✅ | — |
| Sem ano | 345 | **300** ✅ | — |
| **Tags com namespace** | 0 | **10** ✅ | — |

**Sinais positivos**: sem autor caiu 43, sem ano caiu 45, tags `author-focus:*` em uso (gornick=18, kenworthy=15, garritzmann=11, carnoy=10, hemerick=10, podolny=9, paglayan=8, mancano=6).

**Sinais negativos**: itens sem coleção subiu 75 (efeito esperado da reorg — itens dos containers archive ficaram órfãos quando arquivamos). Duplicatas levemente aumentaram (+1 DOI, +2 ISBN, +8 T+A — provavelmente novos imports do user).

---

## Checklist de fases

### ✅ Fase Concluída — Reorganização estrutural (Scripts A-H, 10/05/2026)

- [x] Limpeza inicial (Script A): `references`, `Talita`, `Eduardo`, tag `zotmoov`
- [x] Criação da estrutura nova (Script B): 56 coleções
- [x] Scan de pastas temp (Script C)
- [x] Migração Workbench + autores → tags (Script D): 32 operações
- [x] Diagnóstico Kenworthy (Script E)
- [x] Kenworthy/dd resolvidos + Active Research consolidado (Script F)
- [x] Convenção data-primeiro + Victor recovered (Script G)
- [x] Arquivamento de containers legados (Script H)

### ✅ Fase 0 — Setup do working folder + diagnóstico fresco (CONCLUÍDA 30/05)

- [x] Criar estrutura de pastas em `mancano-zotero-library/`
- [x] Criar `README.md`, `NEWS.md`, `CONVENTIONS.md`, `BACKUPS.md`, `PLAN.md`
- [x] Copiar artefatos de `~/Zotero/_diagnostico/` pras subpastas (`*.py` → `python/`, `*.md` + `.sqlite` → `diagnostics/`)
- [x] Reconstruir scripts JS A-I em `scripts/` (com headers de status/output)
- [x] Adaptar `python/diagnose_v2.py` pra ler `.bak` em `mode=ro` (sem precisar copiar)
- [x] Rodar diagnóstico → `diagnostics/2026-05-30_relatorio.md`
- [x] Atualizar este `PLAN.md` com números reais de 30/05

### 🔜 Fase 0.5 — Resolver 4 anomalias do topo (preciso decisão do user)

- [ ] **`0. Problem`** [14 itens, 1 sub] — pasta nova do user. **Pergunta**: manter como raiz, mover pra dentro de outra (`7. Misc`?), ou converter em tag `priority:problem`?
- [ ] **`2024.2 Trab. Final Instituições e Desigualdades`** [41 itens] — voltou no root. Reaplicar Script G STEP 3: renomear pra `2024-2 — Trab. Final Inst. & Desigualdades` e mover pra `4. Coursework`
- [ ] **`Methodology`** órfã [7 itens] no root — mover pra `3. Fields/★ Theory & Methodology/Methodology` (mesclar conteúdo)
- [ ] **`1. Active Research` faltando 1 sub** — verificar qual foi removida (esperado: Master's ProUni, 2026—BEPE, 2026—Methods, IC FFLCH Victor) e decidir se recria ou se foi remoção intencional
- [x] **`Problematic - No author`** [112 itens] — **RESOLVIDO 2026-05-30** via Scripts J/K/L (triagem em 3 baldes):
  - J (enrich via DOI/ISBN): 11 itens enriquecidos, 17 sem mudança (ISBNs BR não no OpenLibrary)
  - K (lixo de baixa qualidade): 7 itens movidos para lixeira
  - L (creator institucional fieldMode=1): 74 atribuídos, 2 pulados, 1 pendente revisão manual (id 10172)
  - **Total: 92 de 114 resolvidos automaticamente.** Ver `NEWS.md` 2026-05-30 (tarde) e `diagnostics/2026-05-30_problematic_triagem.md`.
  - **Pendências individuais**: (a) item 10172 (`NovosEstudos_novembro_2014_FINAL.indb`) — revisar manualmente, (b) 17 itens sem mudança no balde A — usar Retrieve Metadata do Zotero ou Google Books.
  - **Cleanup pendente**: esvaziar e deletar a coleção `Problematic - No author` (todos os itens agora têm creator).

### 🔜 Fase 1 — Verificar/concluir Script I

- [ ] Diagnóstico via JS: estão populadas `4. Coursework`, `5. Bureaucracy/CVs`, `5. Bureaucracy/My Documents`, `6. Leisure Reading`, `7. Misc / AI Outputs`?
- [ ] Se não: rodar Script I (em `scripts/I_populate_secondary.js`)
- [ ] Log no `NEWS.md`

### 📋 Fase 2 — Resolver duplicatas (~1-2h interativo)

**Razão pra vir antes da Fase 4**: distribuir itens duplicados multiplica retrabalho.

- [ ] Script Python lê snapshot → gera `diagnostics/duplicates_priority.md` ordenado por # de cópias
- [ ] DOI/ISBN idênticos (102 grupos): mesclar via **Find Duplicates** do Zotero (UI gráfica preserva master)
- [ ] Título+ano ambíguos (99 grupos): decisão caso-a-caso
- [ ] Script JS auxiliar produz lista clicável `zotero://select/library/items/{itemKey}`
- [ ] Meta: <10 grupos restantes

### 📋 Fase 3 — Recuperar metadados faltantes (~30min lote + revisão)

- [ ] Selecionar 274 artigos sem DOI → "Retrieve Metadata for PDF" (Crossref)
- [ ] Artigos restantes sem DOI: input manual ou Zotero DOI Manager
- [ ] 98 livros sem ISBN: idem com OpenLibrary/Google Books
- [ ] Meta: >90% artigos com DOI, >80% livros com ISBN

### 📋 Fase 4 — Distribuir itens substantivos do archive pras Fields (longo, gradual)

Subfases — cada uma com script M/N/O dedicado e snapshot pré/pós (J/K/L foram usadas em 30/05 pra resolução de `Problematic - No author`):

- [ ] **M1** — Mapeamento 1-to-1 óbvio (~15-20 pastas archive→Fields)
  - `Archive/MancanoLibrary/0. Education/7.2 Educação Superior no Brasil` → `Fields/Education/Higher Education — Brazil`
  - `Archive/MancanoLibrary/7.1 Estado de Bem-Estar` → `Fields/Political Science/Welfare States & Social Policy`
  - `Archive/MancanoLibrary/5. Antitrust as Industrial Policy` → `Fields/Economics/Industrial Organization & Antitrust`
  - lista completa a ser gerada após diagnóstico fresco
- [ ] **M2** — Dissolver pastas-autor restantes (Mahoney, Thelen, Goldthorpe, Sokoloff, Breen, Acemoglu, Florestan, Grusky, Ribeiro, Meritocracy, Bourdieusianismo, etc.): tag `author-focus:*` + itens vão pro Field correto (regra: tema do item, não só autor)
- [ ] **M3** — Itens órfãos / pastas ambíguas: item-a-item, com participação ativa do usuário
  - Casos conhecidos: `1930 e Vargas` (historiografia brasileira — em `2025-10-17` Workbench)

### 📋 Fase 5 — Limpeza final

- [ ] Normalizar 14 tags com variantes de caixa (script JS automatizado)
- [ ] Revisar 476 tags usadas <=1x — apagar as que forem ruído
- [ ] Reattach ou descartar 241 anexos órfãos
- [ ] Decidir destino do `9. Archive`: esvaziar gradualmente ou manter como histórico
- [ ] Atualizar `README.md` e `CONVENTIONS.md` com estado final

### 🔜 Fase 6 — Sincronização Zotero ↔ G:\My Drive\[[1]] Kami Uploads

**Contexto**: a pasta Kami Uploads (13.7 GB, ~4.400 arquivos) é o `baseAttachmentPath` configurado em `prefs.js`. ZotMoov auto-move PDFs pra lá. Cruzar filesystem ↔ banco do Zotero pra detectar órfãos, links quebrados e duplicatas físicas.

**Preferências do user** (definidas em 30/05):
- **Estrutura predominantemente flat** na raiz da pasta.
- Subdivisão **apenas por tipo de arquivo**: `Syllabi/`, `CVs/`, `Documents/`, `Presentations/`, `_misc/`. **Textos acadêmicos (PDF/EPUB) ficam todos na raiz.**
- **Obsidian vault** (`.obsidian/`) preservar — é do user, não tocar.

**Subfases**:

- [x] **6.0 Mapeamento** (read-only, 06/05) — `python/kami_audit.py` cruzou 4.705 arquivos com 2.410 anexos Zotero. Saída: 1.632 OK, 239 broken, 2.937 órfãos físicos (9,3 GB), 555 grupos hash dup.
- [x] **6.1 Quick wins** (06/05) — 20 lock files `.~lock.*#` deletados.
- [x] **6.0b Análise de subpastas** (06/05) — `00_Meta\` e `_Fix\` NÃO são mirrors; têm conteúdo único com nomes diferentes. Saída: `diagnostics/2026-06-05_kami_subfolders.json`.
- [x] **6.2a Dedup por hash** (concluído 06/06):
  - [x] Plano gerado (06/05): 361 grupos, 402 arquivos a mover, 1,37 GB a liberar
  - [x] Dry-run OK (0 erros, 0 conflitos)
  - [x] `scripts/M_kami_dedup_repoint.js` gerado (31 items Zotero a repointar)
  - [x] Script M rodado no Zotero (06/06): 31/31 ✓
  - [x] `python/kami_dedup_execute.py --execute` (06/06): **402 movidos, 0 erros, 1,28 GB**
  - [ ] **Próximo (manual)**: user revisa `_TRASH_dedup_2026-06-05\_manifest.md`
  - [ ] Após confirmação, esvaziar TRASH definitivamente (recupera 1,28 GB do Drive)
- [ ] **6.2b Recuperar 239 links quebrados**: para cada item Zotero com `linkMode=LINKED_FILE` apontando pra arquivo inexistente, buscar match por hash/título e reanexar via JS Runner. Provável que muitos resolvam-se sozinhos após 6.2a (canonical já está no path que Zotero esperava).
- [ ] **6.2c Reorganização flat-com-tipos**:
  - `_Fix\` (430 files) → raiz (após dedup já tirou parte)
  - `00_Meta\` (333 files) → raiz (após dedup)
  - `_Mov-Estud\`, `_Learn-Causal-Mixtape\` → raiz
  - `01_Syllabi\` + `Syllabuses\` → `Syllabi/`
  - `_GovDocuments\` + `02_Documentos_Governamentais\` + `Personal-Documents\` → `Documents/`
  - Deletar `_Emp\` (vazia)
  - Atualizar `itemAttachments.path` no Zotero pra todos que mudaram de lugar (via JS Runner)
- [ ] **6.2d Triagem dos órfãos físicos restantes** (~1.700 PDFs após 6.2a/c):
  - Importar pro Zotero, arquivar separado, ou deletar
- [ ] **6.5 (futuro)** Renomeação consistente — `autoRenameFiles.done=false` em `prefs.js`; usar pattern BBT-style `{authors} - {year} - {title}.pdf`. Adiar até estar tudo linkado.

---

## Próxima ação concreta

`Problematic - No author` ✅ resolvida em 30/05 (Scripts J/K/L). Restam **4 anomalias** da Fase 0.5: `0. Problem`, `2024.2 Trab. Final`, `Methodology` órfã, sub faltante de `1. Active Research`.

**Próximo passo imediato**: rodar `python/diagnose_v2.py` pra confirmar diff pós-J/K/L (expectativa: "sem autor" cai de 245 → ~170).

Depois disso, em ordem: terminar Fase 0.5 (4 anomalias) → Fase 1 (verificar Script I) → Fase 2 (duplicatas) → Fase 3 (metadados) → Fase 4 (distribuição de itens, scripts M/N/O) → Fase 5 (limpeza final).
