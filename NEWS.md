# NEWS — Log cronológico

Histórico de tudo que foi feito no projeto. Entradas mais recentes no topo.

Formato: `YYYY-MM-DD HH:MM` (Brasília) — descrição → resultado/diff

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
