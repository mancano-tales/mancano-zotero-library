# VISION — Onde queremos chegar

> Este documento descreve o **estado final desejado** da biblioteca Zotero do Mançano.
> É a estrela-guia do projeto: toda decisão de organização deve aproximar a biblioteca deste ideal.

---

## 1. Declaração de visão

**Uma biblioteca acadêmica pessoal que funciona como um segundo cérebro**: navegável por disciplina, pesquisável por faceta (método, região, autor, status), com metadados completos o suficiente para gerar bibliografias perfeitas sem revisão manual, e documentada o bastante para que eu — daqui a 5 anos — consiga reconstruir o raciocínio por trás de cada coleção.

---

## 2. Princípios norteadores

| # | Princípio | Implicação prática |
|---|-----------|-------------------|
| 1 | **Um item, um lugar canônico** | Cada referência mora em exatamente uma coleção de Fields (seu "endereço"). Projetos e Workbenches linkam — não duplicam. |
| 2 | **Tags são facetas, coleções são estrutura** | Coleções = hierarquia temática permanente. Tags = atributos cruzados (geo, método, status, autor). Nunca usar coleção pra o que é faceta. |
| 3 | **Metadados primeiro** | A utilidade da biblioteca depende da qualidade dos metadados. DOI, ISBN, autor, ano e resumo são campos inegociáveis. |
| 4 | **Nomenclatura previsível** | Qualquer pessoa (ou script) deve inferir o conteúdo de uma coleção pelo nome. Inglês, data-primeiro, sem prefixos numéricos arbitrários. |
| 5 | **Zero duplicatas toleradas** | Duplicatas desperdiçam tempo, confundem citações e sujam estatísticas. Meta: eliminação total. |
| 6 | **Evolução documentada** | Toda mudança significativa registrada em `NEWS.md`; snapshots em `diagnostics/`. A história da biblioteca é recuperável. |
| 7 | **Automação > trabalho manual** | Preferir scripts reproduzíveis (JS/Python) a cliques repetitivos. Intervenção manual só para decisões semânticas. |

---

## 3. Estado final desejado — a biblioteca ideal

### 3.1 Estrutura de coleções

```
📚 (raiz Zotero — limpa, sem pastas órfãs)
├── 1. Active Research       → Só projetos com prazo ativo (mestrado, BEPE, ICs)
├── 2. Workbench             → Pastas datadas YYYY-MM-DD para triagem temporária
├── 3. Fields                → Conhecimento permanente, completo, bem classificado
│   ├── ★ Theory & Methodology
│   │   ├── Theoretical Paradigms
│   │   ├── Methodology (Comparative-Historical, Process Tracing, QCA, Econometrics…)
│   │   └── Philosophy of Social Science
│   ├── Economics
│   │   ├── Political Economy of Development
│   │   ├── Economics of Education
│   │   ├── Industrial Organization & Antitrust
│   │   └── Economic History
│   ├── Education
│   │   ├── Higher Education — Brazil
│   │   ├── Higher Education — Comparative
│   │   ├── History of Education
│   │   ├── Educational Inequality
│   │   └── Education Policy & Politics
│   ├── Political Science
│   │   ├── Comparative Political Economy
│   │   ├── Welfare States & Social Policy
│   │   ├── State Formation & Historical Institutionalism
│   │   ├── Democratization & Authoritarianism
│   │   └── Latin American Politics
│   └── Sociology
│       ├── Social Stratification & Mobility
│       ├── Sociology of Education
│       ├── Race & Ethnicity
│       └── Social Movements
├── 4. Coursework            → Disciplinas cursadas (YYYY-S — Nome)
├── 5. Bureaucracy & Documents → CVs, syllabi, certificados
├── 6. Leisure Reading       → Leituras de entretenimento intelectual
├── 7. Misc                  → AI Outputs, inclassificáveis
└── 9. Archive               → Legado histórico, frozen, só consulta
```

**Critério de "pronto"**: toda coleção de Fields contém ao menos os itens que lhe pertencem tematicamente. `9. Archive` serve apenas como registro histórico — nenhum item substantivo deve ficar preso lá indefinidamente.

### 3.2 Sistema de tags (vocabulário controlado)

| Namespace | Cobertura-alvo | Estado ideal |
|-----------|---------------|--------------|
| `geo:` | Todo item empírico com foco geográfico | ≥80% dos artigos empíricos tagueados |
| `method:` | Todo item com método explícito | ≥70% dos artigos metodologicamente tagueados |
| `status:` | Todo item na biblioteca | 100% com status de leitura (`inbox`, `reading`, `done`, `wishlist`) |
| `priority:` | Itens de alta relevância para projetos ativos | Aplicado conforme necessidade |
| `author-focus:` | Autores lidos em conjunto (≥5 itens) | Substitui completamente pastas-autor |
| `output:` | Itens que serão citados em trabalhos | Ligado a projetos de `1. Active Research` |
| `era:` | Itens de pensamento clássico vs. contemporâneo | Opcional, aplicado em Theory |

**Meta de consistência**: 0 variantes de caixa, 0 sinônimos não-resolvidos, média ≥3 tags por item.

### 3.3 Metadados — metas quantitativas

| Métrica | Baseline (09/05) | Estado atual (30/05) | **Meta final** |
|---------|------------------:|---------------------:|---------------:|
| Artigos com DOI | 74% (812/1086) | 74% (803/1086) | **≥97%** |
| Livros com ISBN | 85% (538/636) | 85% (539/636) | **≥95%** |
| Itens com autor | 88% | 90% | **≥99%** |
| Itens com ano | 85% | 87% | **≥99%** |
| Itens com resumo | 43% | 43% | **≥75%** |
| Duplicatas DOI | 59 grupos | 60 | **0** |
| Duplicatas ISBN | 43 grupos | 45 | **0** |
| Duplicatas título+ano | 99 grupos | 107 | **<5** (falsos positivos OK) |
| Itens fora de coleção | 157 | 232 | **0** |
| Anexos órfãos | 241 | 237 | **<10** |
| Tags variantes caixa | 14 | 14 | **0** |
| Tags usadas ≤1x | 476 | 461 | **<50** |

### 3.4 Experiência de uso desejada

1. **Encontrar qualquer referência em <30 segundos** — via busca por título, ou navegação por coleção + tag.
2. **Gerar uma bibliografia perfeita** sem editar manualmente — metadados completos = output limpo em qualquer estilo (APA, ABNT, Chicago).
3. **Onboarding de novas referências em <2 minutos** — importar via browser connector → Zotero auto-enriquece metadados → classificar em 1 coleção + 2-4 tags.
4. **Revisão periódica sem surpresas** — rodar diagnóstico trimestral, métricas só melhoram ou estabilizam.

---

## 4. Ferramentas e plugins do ecossistema

Para atingir essa visão, o workflow integra:

| Ferramenta | Função no workflow |
|------------|-------------------|
| **Zotero 7+** | App principal — organização, anotação, sync |
| **Better BibTeX** | Citation keys estáveis para LaTeX/Markdown |
| **Zotero DOI Manager** | Busca automática de DOIs faltantes |
| **Actions & Tags** | Automação de tagging baseada em triggers |
| **ZotMoov** | Renomeação e organização de PDFs |
| **Linter for Zotero** | Padronização de metadados (caixa, HTML) |
| **Scripts JS custom** (este repo) | Operações em massa: migração, diagnóstico, limpeza |
| **Scripts Python** (este repo) | Análise de snapshots SQLite, relatórios quantitativos |
| **Este repositório** | Documentação viva + versionamento do trabalho |

---

## 5. Marcos de sucesso (milestones)

### 🏁 Marco 1 — Estrutura limpa (Fase 0.5 + 1)
- [ ] Zero pastas órfãs no root (apenas `1.` a `9.`)
- [ ] Todas as sub-coleções de Fields populadas
- [ ] `9. Archive` contém apenas legado histórico, não itens "perdidos"

### 🏁 Marco 2 — Duplicatas eliminadas (Fase 2)
- [ ] 0 duplicatas por DOI
- [ ] 0 duplicatas por ISBN
- [ ] <5 grupos ambíguos por título+ano

### 🏁 Marco 3 — Metadados robustos (Fase 3)
- [ ] ≥97% artigos com DOI
- [ ] ≥95% livros com ISBN
- [ ] ≥99% itens com autor e ano
- [ ] ≥75% itens com resumo

### 🏁 Marco 4 — Classificação completa (Fase 4)
- [ ] 0 itens fora de coleção
- [ ] Todo item substantivo do Archive redistribuído para Fields
- [ ] Sistema de tags namespace em uso ativo (≥3 tags/item em média)

### 🏁 Marco 5 — Manutenção contínua (Fase 5 em diante)
- [ ] 0 variantes de caixa em tags
- [ ] <50 tags usadas ≤1x
- [ ] <10 anexos órfãos
- [ ] Diagnóstico trimestral automatizado mostrando estabilidade ou melhoria
- [ ] Workflow de onboarding documentado e praticado

---

## 6. Evolução no tempo — o que documentamos aqui

Este repositório não é apenas sobre a reorganização pontual. Ele serve como **registro vivo da evolução da biblioteca**:

| O que registramos | Onde | Frequência |
|-------------------|------|-----------|
| Cada ação executada (scripts, merges, decisões) | `NEWS.md` | A cada sessão de trabalho |
| Métricas quantitativas (snapshot diagnóstico) | `diagnostics/YYYY-MM-DD_relatorio.md` | Trimestral (ou antes/depois de fases) |
| Plano operacional (o que falta, em que ordem) | `PLAN.md` | Atualizado ao fechar fases |
| Convenções e regras | `CONVENTIONS.md` | Quando novas regras são adotadas |
| Estado dos backups | `BACKUPS.md` | Quando novos snapshots são criados |
| Visão de longo prazo | `VISION.md` (este arquivo) | Revisado anualmente ou após mudanças de escopo |

### Cadência esperada de evolução

```
2026-Q2  ──►  Reorganização estrutural concluída (Marcos 1-2)
2026-Q3  ──►  Metadados enriquecidos, classificação avançada (Marcos 3-4)
2026-Q4  ──►  Limpeza final, workflow estabilizado (Marco 5)
2027+    ──►  Manutenção trimestral: diagnóstico + ajuste fino
```

---

## 7. Critério de "missão cumprida"

A reorganização está **completa** quando:

1. ✅ Todas as métricas da Seção 3.3 atingem suas metas
2. ✅ A estrutura de coleções reflete fielmente a Seção 3.1
3. ✅ O workflow de onboarding de novas referências está documentado e leva <2 min por item
4. ✅ Um diagnóstico trimestral mostra estabilidade (nenhuma métrica regride)
5. ✅ O `9. Archive` contém apenas material genuinamente histórico (graduação, grupos antigos)

A partir desse ponto, o projeto passa de **reorganização** para **manutenção** — e este repositório se torna o guardião dessa manutenção.

---

*Última revisão: 2026-05-30*
