# NEWS — Log cronológico

Histórico de tudo que foi feito no projeto. Entradas mais recentes no topo.

Formato: `YYYY-MM-DD HH:MM` (Brasília) — descrição → resultado/diff

---

## 2026-06-06 — Fase 6.2a executada (dedup completo)

### 2026-06-06 ~09:30 — Move executado com sucesso

- Script M `M_kami_dedup_repoint.js` rodado no Zotero pelo user: **31/31 ✓**, 0 falhas. Todos os items repointados pro canonical.
- `python kami_dedup_execute.py --execute --date 2026-06-05` rodado:
  - **402 arquivos movidos** para `G:\My Drive\[[1]] Kami Uploads\_TRASH_dedup_2026-06-05\`
  - **0 erros**, 0 skips (missing src, dst exists, canonical conflict — todos zero)
  - **1,28 GB realocados** (cálculo planejado era 1,37 GB; diferença por cache do Google Drive)
- Manifest gerado em `_TRASH_dedup_2026-06-05\_manifest.{csv,md}` (177 KB CSV, 80 KB MD): mapeamento `dst_filename ↔ src_path ↔ canonical` pra revisão manual.
- Pasta Kami Uploads agora: **13,66 GB total** (mesmo número porque arquivos foram movidos pra subpasta, não deletados — ainda).
- **Fix do dia 06/06**: `kami_dedup_execute.py` ganhou flag `--date YYYY-MM-DD` + auto-fallback pro plano mais recente, pra evitar problema quando vira a noite entre o plano e a execução.

### 2026-06-06 ~09:25 — Bug fix kami_dedup_execute.py

A virada de data (05→06 entre o plano e a execução) fez o script procurar arquivo `2026-06-06_kami_dedup_plan.json` que não existia. Refatorei pra:
1. Aceitar `--date 2026-06-05` explícito
2. Fallback automático pro plano mais recente em `diagnostics/`

---

## 2026-06-05 — Fase 6 iniciada: Sincronização Kami Uploads ↔ Zotero

### 2026-06-05 ~16:30 — Plano de dedup pronto + dry-run OK

- `python/kami_dedup_plan.py` re-hashou os 4.368 arquivos e gerou plano:
  - **361 grupos de hash com 2+ cópias**
  - 212 grupos com 1+ link Zotero (canonical = a linkada)
  - **31 grupos com 2+ links Zotero** (precisam repoint — Script M gerado)
  - 149 grupos sem nenhum link (canonical = na raiz com nome mais curto)
  - **402 arquivos a mover para `_TRASH_dedup_2026-06-05\`** (1,37 GB)
- Destino: `G:\My Drive\[[1]] Kami Uploads\_TRASH_dedup_2026-06-05\` com nome `<canonical>__dup_N__<original_short>.ext` (decisão do user 06/05 pra facilitar revisão manual)
- `scripts/M_kami_dedup_repoint.js` gerado: 31 items Zotero a repointar pro canonical ANTES do move.
- `python/kami_dedup_execute.py` escrito com `--dry-run` / `--execute`. Dry-run rodado: **402 movimentos planejados, 0 erros, 0 conflitos**.
- Outputs:
  - `diagnostics/2026-06-05_kami_dedup_plan.{md,json}` (plano completo)
  - `diagnostics/2026-06-05_kami_dedup_execlog.md` (log do dry-run)
  - `scripts/M_kami_dedup_repoint.js` (31 items pra repoint)

**Próximo passo**: rodar Script M no Zotero → confirmar 31 ✓ → executar `kami_dedup_execute.py --execute`.

### 2026-06-05 ~16:00 — Análise de subpastas

- `python/kami_subfolder_analysis.py` confirma que `00_Meta\` e `_Fix\` **não são mirrors** da raiz (têm conteúdo único com nomes diferentes; sobreposição é só por hash).
- Subpastas com mais arquivos exclusivos:
  - `_Fix\` (430 files, 1.39 GB)
  - `00_Meta\` (333 files, 800 MB)
  - `01_Syllabi\` (189 files, 512 MB)
- Detectadas **categorias duplicadas** que serão consolidadas em 6.2c:
  - `01_Syllabi\` + `Syllabuses\` → `Syllabi/`
  - `_GovDocuments\` + `02_Documentos_Governamentais\` → `Documents/` (ou novo `GovDocs/`)
  - `Personal-Documents\` → `Documents/`
- `_Emp\` vazia — pode ser deletada quando for hora.
- Output: `diagnostics/2026-06-05_kami_subfolders.json`

### 2026-06-05 ~15:40 — Auditoria Fase 6.0 completa

- `python/kami_audit.py` rodado: cruzou os 4.705 arquivos da pasta Kami Uploads (13,7 GB) com os 2.410 anexos do Zotero (read-only no `.bak`).
- Resultado:
  - ✅ Linked OK: **1.632**
  - 💥 Linked broken: **239** (Zotero aponta, arquivo sumiu — provavelmente em subpasta)
  - 🟡 Órfãos físicos: **2.937** (9,3 GB)
  - 🔁 Grupos hash dup: **555** (versão inicial; refinada depois pra 361 com escopo mais estrito)
- Distribuição dos órfãos:
  - academic_pdf: 2.652 (8,04 GB)
  - academic_epub: 126 (0,51 GB)
  - cvs: 36, presentations: 24, syllabi: 6, etc.
- Outputs: `diagnostics/2026-06-05_kami_audit.{md,json}`

### 2026-06-05 ~15:30 — Quick wins (Fase 6.1)

- 20 lock files `.~lock.*#` (LibreOffice) deletados da raiz do Kami Uploads.
- `.obsidian/` preservado (vault do user).

### 2026-06-05 ~15:00 — Documentação Fase 6

- `PLAN.md` atualizado com Fase 6 completa (subfases 6.0–6.5) e preferências do user:
  - **Flat predominante**; subdivisão só por tipo: `Syllabi/`, `CVs/`, `Documents/`, `Presentations/`, `_misc/`.
  - Textos acadêmicos (PDF/EPUB) ficam na raiz.
  - `.obsidian/` preservado.
- Scripts Python da Fase 6 em `python/`: `kami_audit.py`, `kami_subfolder_analysis.py`, `kami_dedup_plan.py`, `kami_dedup_execute.py`.

---

## 2026-05-30 (tarde) — Resolução da coleção "Problematic - No author" (Scripts J/K/L)

### 2026-05-30 ~19:00 — Triagem em 3 baldes + execução dos 3 scripts

Endereçou simultaneamente as duas anomalias pendentes da Fase 0.5: os **3 itens sem título** e os **112 itens da coleção `Problematic - No author`** (114 itens únicos, 3 ∩ 1).

**Pipeline novo** (em `python/`):
1. `inspect_problematic.py` → dossier completo (`diagnostics/2026-05-30_problematic_inspect.md`, 1063 linhas, 75 KB)
2. `classify_problematic.py` → 4 JSONs (`diagnostics/2026-05-30_balde_{A,B,C,skip}.json`) + `diagnostics/2026-05-30_problematic_triagem.md`
3. `generate_js_scripts.py` → produz `scripts/J_problematic_enrich.js`, `K_problematic_trash.js`, `L_problematic_inst_creator.js`

**Classificação final dos 114:**

| Balde | n | Critério | Script |
|---|--:|---|---|
| SKIP | 2 | `case`/`statute` que usam `caseName`/`nameOfAct` (49=Portaria GR USP, 282=Lei 13.267) — não é bug | — |
| **A — Enrich** | **28** | tem DOI ou ISBN | `J_problematic_enrich.js` |
| **B — Lixo** | **7** | webpage em domínio de baixa qualidade (blogs ABNT/TCC: mettzer, viacarreira, tecnoblog, fastformat, projetoacademico, normastecnicas) | `K_problematic_trash.js` |
| **C — Anônimo legítimo** | **77** | webpage/blog/vídeo sem autor; URL identifica órgão emissor | `L_problematic_inst_creator.js` |

**Mapa domínio → creator** (`python/classify_problematic.py`, dicionário `DOMAIN_CREATOR`):
- Imprensa: Folha (11), Valor (10), G1 (2), IstoÉ (2), Exame (1), Reuters Brasil (1), Marie Claire (1), Jornal de Brasília (1), JOTA (1), Carta Campinas (1), Repórter Brasil (1), Sul21 (1), UOL Economia (1)
- USP: Jornal da USP (2), LabCidade FAU-USP (1), FO-USP (1), ADUSP (1), McMaster (1)
- Gov: Senado Federal (2), Fundo Social SP (1)
- Civis: UNE (3), UBES (3), Levante (1), F. Perseu Abramo (1), WRI Brasil (1), Change.org (1), Politize! (1), O Cafezinho (1), Jornalistas Livres (1), O Joio e o Trigo (1), Monitor das Doações (1), Racismo Ambiental (1)
- Wikis: Wikipédia (2), Wikipedia (2)
- Vídeo: YouTube (9)
- Blog: Sociófilo (1), Political Anthropology (1)
- 1 marcado `needs_review` (id 10172, `NovosEstudos_novembro_2014_FINAL.indb` — provavelmente Novos Estudos CEBRAP nov/2014)

**Decisão pra anônimos legítimos**: criar creator com `fieldMode: 1` (single-field "name only" — CSL trata como corporate author). Documentado em `CONVENTIONS.md §2.1`.

**Resultado real da execução** (user rodou via Run JavaScript, Zotero aberto):
- **Script J** (28 itens): ✓ 11 enriquecidos, 0 falhas, 17 sem mudança
  - Enriqueceram: 151 (publisher), 1054 (numPages+creators), 5045 (creators), 6867/7021/7038/7039 (publicationTitle), 8434 (place+numPages+abstract+creator), 9417 (publisher), 11644 (publisher), 11886 (title)
  - "Sem mudança" = OpenLibrary não tinha dados para ISBNs brasileiros pequenos (esperado; fallback futuro: Google Books ou input manual)
- **Script K** (7 itens): ✓ 7 movidos para lixeira (reversível 30 dias)
- **Script L** (77 itens): ✓ 74 atribuídos, 2 pulados (9291, 9298 já tinham creator), 1 pra revisão manual (10172)

**Diff vs. baseline 30/05 manhã**: ~92 itens resolvidos do total de 114 (81%).
- Pendente manual: 1 item (10172, revisar Retrieve Metadata)
- Pendente sem mudança no Balde A: 17 itens (livros com ISBN BR não encontrados no OpenLibrary)

**Próximo passo concreto**: rodar `python/diagnose_v2.py` pra confirmar o novo "sem autor" (esperado ~245 - 74 = ~171). Depois esvaziar a coleção `Problematic - No author` (snippet sugerido no rodapé do balde A).

### 2026-05-30 ~18:30 — Confirmação de pendência

User confirmou que o Zotero estava aberto e funcionando bem (vs. tarde 30/05 manhã quando havia journal pendurado de uma sessão anterior). Performance principal vinculada ao Better BibTeX com 3 auto-exports de biblioteca-inteira configurados em `prefs.js` (a otimizar em fase futura). Snapshot novo registrado em `BACKUPS.md`.

---

## 2026-05-30 — Formalização do projeto

### 2026-05-30 11:55 — Diagnóstico fresco rodado com sucesso
- Adaptei `python/diagnose_v2.py` pra ler `~/Zotero/zotero.sqlite.bak` (10:24 de hoje) em modo `?mode=ro`
- Saída: `diagnostics/2026-05-30_relatorio.md` (235 linhas)
- **Resumo do diff vs. baseline 09/05/2026:**

| Métrica | 09/05 | 30/05 | Δ |
|---------|------:|------:|---:|
| Itens bibliográficos | 2.337 | 2.348 | +11 |
| Anexos | 2.417 | 2.391 | -26 |
| Notas | 525 | 550 | +25 |
| Coleções | 186 | 227 | +41 (criamos 56, algumas vazias deletadas) |
| Tags | 578 | 581 | +3 |
| Duplicatas DOI | 59 | 60 | +1 |
| Duplicatas ISBN | 43 | 45 | +2 |
| Duplicatas título+ano | 99 | 107 | +8 |
| Sem autor | 288 | **245** | **-43** ✅ |
| Sem ano | 345 | **300** | **-45** ✅ |
| Artigos sem DOI | 274 | 283 | +9 |
| Livros sem ISBN | 98 | 97 | -1 |
| Itens fora de coleção | 157 | **232** | +75 (efeito da reorg — pastas archive deixaram items órfãos) |
| Coleções vazias | 16 | **42** | +26 (sub-pastas vazias da archive + bureaucracy criada) |
| Tags variantes caixa | 14 | 14 | 0 (intacto — Fase 5 pendente) |
| Tags <=1x | 476 | 461 | -15 |
| **Tags com namespace** | 0 | **10** | **+10** ✅ (`author-focus:*` em uso) |

- **Anomalias detectadas no topo (4)** — provavelmente coisas que o user fez manualmente nos últimos 20 dias:
  1. `0. Problem` [14 itens, 1 sub] — pasta NOVA criada pelo user com prefixo `0.`
  2. `2024.2 Trab. Final Instituições e Desigualdades` [41 itens] — voltou no root (estava marcada como apagada em 10/05)
  3. `Methodology` [7 itens, 0 subs] — pasta órfã no root (deveria estar dentro de `★ Theory & Methodology`)
  4. `1. Active Research` só tem **3 subs** (esperado 4) — uma project foi removida (verificar qual)

- **Itens novos importantes**: `Problematic - No author` [112 itens] — pasta nova provavelmente criada pelo user pra agrupar problemas de metadado

### 2026-05-30 11:46 — Setup do working folder
- Criada estrutura `mancano-zotero-library/` em `C:\Users\Mancano\Documents\MancanoSync\`
- Subpastas: `scripts/`, `diagnostics/`, `python/`
- 5 arquivos topo: `README.md`, `PLAN.md`, `NEWS.md`, `CONVENTIONS.md`, `BACKUPS.md`
- 9 scripts JS reconstruídos em `scripts/` (A-I com headers padronizados, data, status, output esperado)
- 6 scripts Python migrados de `~/Zotero/_diagnostico/` pra `python/`
- 2 backups + 2 relatórios migrados pra `diagnostics/`

---

## 2026-05-10 — Reorganização principal (8 scripts JS executados)

### 2026-05-10 ~19:46 — Backup intermediário
- Salvo `zotero_BEFORE_CLEANUP_2026-05-10_1955.sqlite` (24.2 MB) em `_diagnostico/`

### Script H — Arquivamento de containers legados
Movidos pra `9. Archive`:
- `00_Important_reading` (87 itens + 4 subs, incluindo `01_Ver e Classificar`)
- `01_Ongoing_Projects` (10 itens restantes)
- SKIPs (já estavam em Archive): `MancanoLibrary`, `ZZ_Old_Group_libs`
- SKIPs (já apagadas/inexistentes): `Sites e Redes Sociais`, `Bibliografia`, `2024.2 Trab. Final`

Estado final do topo: limpo, só `1.` a `9.` da estrutura nova visíveis.

### Script G — Convenção data-primeiro + recuperar Victor/Trab Final
- Renomeados pra "data primeiro": `BEPE — Tarlau (2026)` → `2026 — BEPE Tarlau`, `Methods Workshop (2026)` → `2026 — Methods Workshop`, `440B... — 2026-1` → `2026-1 — 440B...`, `História da Educação FEUSP — 2025-2` → `2025-2 — História da Educação FEUSP`
- Victor merged: `00_Important_reading/01_Ver e Classificar/IC na FFLCH - Victor Alcantara` → `1. Active Research/IC FFLCH — Victor Alcantara` (7 itens)
- `2024.2 Trab. Final` — não encontrada (já apagada manualmente)

### Script F — Kenworthy + Active Research consolidation
- `dd` promovida a Workbench/`2026-05-07-temp` (17 itens) — eram variados, incluindo George & Bennett "Case Studies and Theory Development" que vai pra `Theory & Methodology/Methodology/Comparative-Historical & Process Tracing` na Fase 4
- Kenworthy dissolvida: 15 itens → `2026-05-03` + tag `author-focus:kenworthy`
- ProUni: 4 subs + 87 itens merged em `Master's — ProUni & Affirmative Action`
- BEPE Tarlau: 35 itens merged em `BEPE — Tarlau (2026)`
- Methods Workshop: 1 sub + 3 itens merged em `Methods Workshop (2026)`

### Script E — Diagnóstico Kenworthy
- Kenworthy tinha subpasta `dd` com 17 itens (incluindo George & Bennett, tese Acir Almeida, etc.)
- Decisão: promover `dd` a Workbench próprio (não era lixo)

### Script D — Workbench migration (32 operações)
- 8 pastas-autor dissolvidas em tags `author-focus:*` (Gornick, Carnoy, Garritzmann, Paglayan, Mançano, Podolny, Hemerick) — Kenworthy skipped (tinha subpasta `dd`)
- 20 pastas temp renomeadas pra `YYYY-MM-DD` e movidas pro `2. Workbench`
- 2 coursework movidos: `2025-10-200 História...` → `História da Educação FEUSP — 2025-2`, `440B...` → `440B Comparative Political Economy — 2026-1`
- `Base para a Linha do Tempo` → sub do projeto Master's
- `Politics and Time` → `Historical Institutionalism`

### Script C — Scan de pastas temp-like
- Identificadas 26 candidatas com data extraída (do nome ou do `dateAdded` do item mais antigo)

### Script B — Criação da estrutura nova (56 coleções)
Árvore consensuada após 5 iterações do plano:
- `1. Active Research` (4 projetos planejados, vazios)
- `2. Workbench` (vazia, pra receber temps)
- `3. Fields` com sub-árvore completa (Theory & Methodology, Economics, Education, Political Science, Sociology — todas com subdivisões temáticas)
- `4. Coursework`, `5. Bureaucracy & Documents` (5 subs), `6. Leisure Reading`, `7. Misc`, `9. Archive`

### Script A — Limpeza inicial
- `references` (127 itens) deletada — itens preservados na biblioteca
- `Talita`, `Eduardo` — não encontradas (já apagadas)
- Tag `zotmoov` removida de **529 anexos** (era resíduo do plugin ZotMoov)

### 2026-05-10 (manhã) — Decisões do plano de organização (v1 → v5)
Iterações do plano de taxonomia com base em diagnóstico temático:
- **v1**: estrutura por tradição teórica
- **v2**: estrutura por área (Educação principal)
- **v3**: educação como projeto de mestrado + disciplinar (PolSci/Sociology/Economics)
- **v4**: inglês + Theory&Methodology como prioritária + Coursework separado + Bureaucracy & Documents
- **v5**: Fields como pasta-mãe + Workbench datado + Education como sub-field interdisciplinar

### Apagadas 7 coleções vazias claramente lixo
`Primo_RIS_Export`, `S0276562416301251`, `citationExport-acrefore-9780190264093-e-1679`, `references.bib`, `Teste`, `@Voice-2025-3-22`, `2025-10-28_Politics-of-Inequality_Marius-Busemeyer`

---

## 2026-05-09 — Diagnóstico inicial

### 2026-05-09 20:00 — Backup imutável
- Salvo `zotero_BEFORE_REORG_2026-05-09.sqlite` (23.5 MB) em `_diagnostico/`

### Diagnóstico via `diagnose.py`
- 2.337 itens bibliográficos, 2.417 anexos, 525 notas
- Distribuição: 1.070 articles, 632 books, 248 webpages, 139 bookSections, 47 theses
- **Problemas encontrados:**
  - 59 grupos duplicados por DOI
  - 43 grupos duplicados por ISBN
  - 99 grupos duplicados por título+ano
  - 274 artigos sem DOI
  - 98 livros sem ISBN
  - 288 itens sem autor
  - 345 sem data
  - 1.330 sem resumo
  - 241 anexos órfãos
  - 157 itens fora de qualquer coleção
  - 14 tags com variantes de caixa (Education/education, Higher education/Higher Education/higher education, etc.)
  - 476 tags usadas <=1x
- Análise temática: top autores (Mahoney 28, Thelen 28, Busemeyer 17, Schneider 17), top temas (educação superior, welfare state, comparative political economy)
