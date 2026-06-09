# 📁 Plano de Organização — Biblioteca Zotero (`[[1]] Kami Uploads`)

> **Data:** 10 de maio de 2026  
> **Autor:** Tales Mançano (com assistência de Antigravity AI)  
> **Local:** `g:\My Drive\[[1]] Kami Uploads`

---

## 1. Diagnóstico do Estado Atual

### 1.1 Visão Geral

| Métrica | Valor estimado |
|:--------|:---------------|
| Arquivos na raiz (nível 0) | **~1.500+** |
| Subpastas existentes | Apenas **1** significativa (`0_4_Syllabuses`) + `.obsidian` |
| Tipos predominantes | `.pdf` (~85%), `.epub`, `.docx`, `.pptx`, `.xlsx`, `.mp3/.wav` |
| Lock files (`.~lock.*`) | ~20+ arquivos-lixo do LibreOffice |
| Duplicatas identificadas | ~50+ (sufixos `(1).pdf`, versões `pt_Br` repetidas) |

### 1.2 Problemas Identificados

| # | Problema | Exemplo |
|:-:|:---------|:--------|
| 1 | **Tudo na raiz** — nenhuma estrutura temática | 1.500+ arquivos em uma única pasta |
| 2 | **Documentos pessoais misturados com acadêmicos** | CVs, comprovantes de voo, cartões de ID, formulários |
| 3 | **Duplicatas** | `067335engo.pdf` e `067335engo (1).pdf` |
| 4 | **Nomenclatura inconsistente** | Alguns: `Autor - Ano - Título.pdf`; outros: `1-s2.0-S001449832400010X-main.pdf` |
| 5 | **Lock files do LibreOffice** | `.~lock.Busemeyer - 2014 - Skills and Inequality.pdf#` |
| 6 | **Materiais de aula misturados** | Slides `.pptx`, programas de disciplina |
| 7 | **Múltiplos formatos do mesmo livro** | `.pdf` + `.epub` do mesmo título |
| 8 | **Sem indexação ou metadados** | Nenhum catálogo, nenhum README, nenhum arquivo de navegação |

---

## 2. Proposta de Taxonomia de Pastas

> [!IMPORTANT]  
> A taxonomia proposta é **alinhada às categorias do repositório [Annotated-Bibliography](https://mancano-tales.github.io/Annotated-Bibliography)** (Layer B — Substantive themes), permitindo interoperabilidade entre a biblioteca de PDFs e os fichamentos.

### 2.1 Estrutura Proposta

```
[[1]] Kami Uploads/
│
├── 00_Meta/                          # Documentação e indexação
│   ├── README.md                     # Descrição da biblioteca para humanos
│   ├── CLAUDE.md                     # Instruções para agentes de IA
│   ├── CATALOG.md                    # Índice geral (gerado automaticamente)
│   └── CONVENTIONS.md                # Regras de nomenclatura e organização
│
├── Political-Economy/                # Economia política comparada
│   ├── Welfare-States/               # Regimes de bem-estar social
│   ├── Varieties-of-Capitalism/      # Variedades de capitalismo
│   ├── Growth-Models/                # Modelos de crescimento
│   └── Labor-Markets/                # Mercados de trabalho e skills
│
├── Education/                        # Educação como policy area
│   ├── Higher-Education/             # Ensino superior (geral + Brasil)
│   │   ├── Access-and-Expansion/     # Expansão, acesso, PROUNI, FIES
│   │   ├── Affirmative-Action/       # Cotas e ação afirmativa
│   │   ├── Private-Sector/           # Setor privado, financeirização
│   │   └── Quality-and-Rankings/     # Qualidade, rankings, avaliação
│   ├── Educational-Inequality/       # Desigualdade educacional
│   ├── Skills-and-Training/          # Skill formation, VET
│   ├── Sociology-of-Education/       # Sociologia da educação
│   └── History-of-Education/         # História da educação
│
├── Inequality/                       # Desigualdade (renda, riqueza, oportunidade)
│   ├── Social-Stratification/        # Estratificação, mobilidade social
│   ├── Intergenerational-Mobility/   # Mobilidade intergeracional
│   └── Redistribution/               # Redistribuição, taxação
│
├── Brazilian-Politics/               # Política brasileira
│   ├── Social-Policy/                # Políticas sociais no Brasil
│   ├── State-and-Bureaucracy/        # Estado, burocracia, reforma administrativa
│   ├── Elections-and-Parties/        # Eleições, partidos, coalizões
│   ├── Federalism/                   # Federalismo, coordenação
│   └── Historical-Formation/         # Formação histórica (colonial → República)
│
├── Development/                      # Desenvolvimento econômico e social
│   ├── Latin-America/                # América Latina geral
│   ├── East-Asia/                    # Leste Asiático
│   ├── Industrial-Policy/            # Política industrial, antitrust
│   └── State-Capitalism/             # Capitalismo de estado, campeões nacionais
│
├── Methodology/                      # Métodos de pesquisa
│   ├── Quantitative/                 # Econometria, causalidade, DiD, RDD
│   ├── Qualitative/                  # Process tracing, estudos de caso
│   ├── Comparative/                  # Método comparado, QCA
│   └── Philosophy-of-Science/        # Filosofia da ciência, epistemologia
│
├── Historical-Institutionalism/      # Institucionalismo histórico
│   ├── Institutional-Change/         # Mudança institucional
│   ├── Path-Dependence/              # Path dependence, critical junctures
│   └── Historical-PE/                # Historical political economy
│
├── Sociology-and-Theory/             # Teoria sociológica e social
│   ├── Classic-Theory/               # Weber, Durkheim, Marx, Bourdieu
│   ├── Organizations/                # Sociologia das organizações
│   ├── Economic-Sociology/           # Sociologia econômica
│   └── Quantification/               # Sociologia da quantificação
│
├── Democracy-and-Representation/     # Democracia e representação
│   ├── Democratic-Theory/            # Teoria democrática
│   ├── Populism/                     # Populismo, polarização
│   └── Political-Behavior/           # Comportamento político
│
├── Books-and-Literature/             # Livros completos (não-acadêmicos), literatura
│
├── Syllabuses/                       # Programas de disciplinas
│
├── Course-Materials/                 # Slides, handouts, materiais de aula
│
├── Personal-Documents/               # CVs, comprovantes, formulários, declarações
│
├── Thesis-Materials/                 # Materiais da própria dissertação
│   ├── Drafts/                       # Rascunhos, versões
│   ├── Presentations/                # Apresentações do MA
│   └── Administrative/               # Formulários FAPESP, relatórios
│
└── _Archive/                         # Duplicatas e arquivos a revisar
    ├── Duplicates/                   # Duplicatas confirmadas
    └── To-Review/                    # Arquivos não classificados
```

### 2.2 Regras de Classificação

> [!NOTE]
> Quando um arquivo se encaixa em múltiplas categorias, usar a seguinte regra de prioridade:
> 1. **Tema primário** do artigo (questão de pesquisa principal)
> 2. **Policy area** quando é sobre educação → sempre `02_Education/`
> 3. **País/região** quando o paper é primariamente empírico e localizado
> 4. Em caso de dúvida → `_Archive/To-Review/`

---

## 3. Convenções de Nomenclatura

### 3.1 Padrão para PDFs Acadêmicos

```
Sobrenome[_et-al] - Ano - Título Curto.pdf
```

**Exemplos:**
- `Busemeyer - 2014 - Skills and Inequality.pdf`
- `Acemoglu_et-al - 2001 - Colonial Origins of Comparative Development.pdf`
- `Arretche - 2019 - Paths of Inequality in Brazil.pdf`

### 3.2 Padrão para Livros Completos

```
Sobrenome - Ano - Título Completo.[pdf|epub]
```

### 3.3 Arquivos a NÃO Renomear

- Arquivos com nomes que já seguem o padrão `Autor - Ano - Título`
- Livros `.epub` baixados de bibliotecas (nomes longos OK)

---

## 4. Fases de Implementação

### Fase 0: Preparação (30 min)
- [ ] Criar a estrutura de pastas (script automatizado)
- [ ] Criar os arquivos `README.md`, `CLAUDE.md`, `CONVENTIONS.md`
- [ ] Remover **todos os lock files** (`.~lock.*`)

### Fase 1: Limpeza Inicial (1–2h)
- [ ] Identificar e mover **duplicatas** para `_Archive/Duplicates/`
- [ ] Mover **documentos pessoais** para `13_Personal-Documents/`
- [ ] Mover **slides e materiais de aula** para `12_Course-Materials/`
- [ ] Mover **syllabuses** para `11_Syllabuses/` (fusão com `0_4_Syllabuses`)
- [ ] Mover **materiais da dissertação** para `14_Thesis-Materials/`

### Fase 2: Classificação Temática (sessões de 1h)
- [ ] Classificar PDFs acadêmicos nas pastas temáticas (01–09)
- [ ] Priorizar: começar pelos autores mais citados na dissertação
- [ ] Usar o Zotero como referência cruzada (tags e coleções)

### Fase 3: Indexação e Catálogo (1h)
- [ ] Gerar `CATALOG.md` com lista dos arquivos por pasta
- [ ] Cruzar com `references.bib` do Annotated-Bibliography

### Fase 4: Automação Futura (opcional)
- [ ] Script Python/R para gerar `CATALOG.md` automaticamente
- [ ] Script para detectar duplicatas por hash MD5
- [ ] Integração com Zotero Export para manter sincronizado

---

## 5. Riscos e Restrições

> [!WARNING]
> **Google Drive Sync:** Mover muitos arquivos de uma vez no Google Drive pode causar problemas de sincronização. Recomenda-se fazer as mudanças em lotes de ~50 arquivos por sessão.

> [!CAUTION]
> **Zotero Links:** Se o Zotero referencia arquivos por caminho absoluto (não pelo hash), mover os PDFs pode **quebrar os links no Zotero**. Verificar antes nas preferências do Zotero se o linked file storage aponta para esta pasta.

> [!TIP]
> **Estratégia segura:** Criar as pastas e **copiar** (não mover) os primeiros 20 arquivos para testar se o Zotero continua funcionando. Só depois fazer a migração em massa.

---

## 6. Documentação para Agentes de IA

Três arquivos MD serão criados na pasta `00_Meta/`:

| Arquivo | Propósito | Audiência |
|:--------|:----------|:----------|
| `README.md` | Visão geral da biblioteca, taxonomia, convenções | Humanos + IA |
| `CLAUDE.md` | Instruções operacionais para agentes de IA | Agentes de IA |
| `CONVENTIONS.md` | Regras detalhadas de nomenclatura e classificação | Humanos + IA |

---

## Próximos Passos

1. **Revisar este plano** — confirmar se a taxonomia faz sentido para o seu uso
2. **Verificar Zotero** — checar como os linked files são referenciados
3. **Criar a estrutura de pastas** — posso gerar um script PowerShell para isso
4. **Criar os MDs** — `README.md`, `CLAUDE.md`, `CONVENTIONS.md`
5. **Iniciar a Fase 1** — limpeza inicial (posso ajudar com scripts)
