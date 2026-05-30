# CONVENTIONS — Padrões do projeto

## 1. Nomenclatura de coleções

### Princípio geral: **idioma inglês**, **data primeiro** nas temporalmente específicas

| Tipo de pasta | Formato | Exemplo |
|---------------|---------|---------|
| Raiz numerada | `N. Nome` (N = 1..9) | `1. Active Research`, `9. Archive` |
| Workbench (datado) | `YYYY-MM-DD` puro | `2026-05-03` |
| Workbench (data inferida) | `YYYY-MM-DD-temp` | `2025-06-23-temp` |
| Workbench (colisão de data) | sufixo `-N` | `2025-06-23-temp-2` |
| Coursework | `YYYY-S — Nome do curso` | `2026-1 — 440B Comparative Political Economy` |
| Active Research datado | `YYYY — Nome` | `2026 — BEPE Tarlau` |
| Active Research multi-ano | sem prefixo | `Master's — ProUni & Affirmative Action` |
| Subdivisões de Fields | sem numeração, ordem alfabética | `Welfare States & Social Policy` |
| Sub prioritária dentro de Fields | prefixo `★ ` pra forçar topo | `★ Theory & Methodology` |

### Semestre

`S` em coursework = `1` (primeiro semestre) ou `2` (segundo). Ex: `2024-1` = 1º semestre de 2024.

## 2. Vocabulário de tags

Tags usam **namespace `prefixo:`** pra evitar conflito e habilitar facetamento.

| Namespace | Função | Exemplos |
|-----------|--------|----------|
| `geo:` | país/região do estudo | `geo:brazil`, `geo:nordic`, `geo:sweden`, `geo:korea`, `geo:us`, `geo:la`, `geo:europe` |
| `method:` | método empírico usado pelo paper | `method:process-tracing`, `method:did`, `method:rdd`, `method:ethnography`, `method:survey`, `method:formal`, `method:logistic` |
| `status:` | estado de leitura | `status:inbox`, `status:reading`, `status:done`, `status:wishlist` |
| `priority:` | prioridade no fluxo | `priority:high`, `priority:core` |
| `author-focus:` | autores que você lê em conjunto (substitui pastas-autor) | `author-focus:mahoney`, `author-focus:thelen`, `author-focus:goldthorpe`, `author-focus:gornick`, `author-focus:carnoy` |
| `output:` | trabalho onde será citado | `output:masters-thesis`, `output:prouni-paper`, `output:tarlau` |
| `era:` | classificação temporal | `era:classical`, `era:contemporary` |
| `source:` | fonte institucional | `source:oecd`, `source:scielo` |
| `bureau:` | tipo de documento burocrático | `bureau:cv`, `bureau:syllabus`, `bureau:certificate` |

### Regra ouro: pasta vs tag

- **Coleção** = pertencimento estrutural (item "vive" naquele lugar)
- **Tag** = atributo/faceta (item *tem* essa propriedade)
- Coleção é boa quando há um agrupamento permanente que você navega
- Tag é boa quando há facetas múltiplas que cruzam (geo, método, status, autor)
- Exemplo: paper de Goldthorpe sobre estratificação na Suécia usando logística vive em `Fields/Sociology/Social Stratification & Mobility` + tags `author-focus:goldthorpe` `geo:sweden` `method:logistic`

## 3. Regras de classificação (Theory vs Field)

Pra decidir se um texto vai pra `Theory & Methodology / Theoretical Paradigms` ou pra uma sub-disciplina:

| Vai pra `Theory & Methodology / Theoretical Paradigms` | Fica na disciplina (Economics/PolSci/Sociology) |
|----------------------------------------------------------|--------------------------------------------------|
| Texto que **expõe ou revisa o paradigma** | Texto que **aplica o paradigma a um caso** |
| Mahoney "Path Dependence" (artigo teórico) | Mahoney sobre Guatemala (caso empírico) |
| Hall & Soskice intro do *Varieties of Capitalism* | Madariaga sobre neoliberalismo no Chile |
| Esping-Andersen *Three Worlds* (formulação) | Obinger sobre warfare→welfare em país X |
| Thelen "How Institutions Evolve" (modelo) | Thelen sobre treinamento profissional na Alemanha |

Tag `author-focus:thelen` cruza os dois lados sem duplicar.

## 4. Convenções de scripts

### Scripts JS (Tools → Developer → Run JavaScript no Zotero)

- Nome: `<Letra>_<descrição_curta>.js` em ordem alfabética de execução cronológica
- Header obrigatório (comentário no topo):
  ```javascript
  // Script <Letra> — <descrição>
  // Data de criação: YYYY-MM-DD
  // Data de execução: YYYY-MM-DD (ou "PENDENTE")
  // Status: <PENDENTE | EXECUTADO | FALHOU>
  // Output esperado: <breve descrição do que deve retornar>
  ```
- Sempre `return log.join('\n')` no fim pra Zotero mostrar resultado

### Scripts Python (em `python/`)

- Sempre ler SQLite via URI `?mode=ro` (read-only, não toca o banco)
- Preferir ler `~/Zotero/zotero.sqlite.bak` (cópia estável feita pelo próprio Zotero) sobre o `.sqlite` live (que pode estar locked)
- Output sempre datado: `diagnostics/YYYY-MM-DD_<nome>.md`

## 5. Snapshots e backups

Ver `BACKUPS.md` pra inventário completo e procedimento de restauração.

- Antes de qualquer script JS destrutivo: snapshot rotulado em `diagnostics/`
- Convenção: `zotero_snap_YYYY-MM-DD[_HHMM].sqlite`
- Snapshots imutáveis (não sobrescrever): `zotero_BEFORE_<EVENTO>_YYYY-MM-DD.sqlite`

## 6. Log no NEWS.md

Toda ação significativa entra em `NEWS.md` com:
- Timestamp `YYYY-MM-DD HH:MM` (Brasília)
- Descrição da ação
- Resultado/diff (números antes vs depois)
- Output do script (resumido) ou link pra arquivo completo se for grande

Entradas mais recentes no topo.
