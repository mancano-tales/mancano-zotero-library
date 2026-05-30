# Mançano Zotero Library — Projeto de Reorganização

Repositório de scripts, diagnósticos e documentação do trabalho de reorganização da minha biblioteca pessoal do Zotero (~2.337 itens bibliográficos + 2.417 anexos + 525 notas).

## Por que este projeto existe

Há ~20 dias iniciamos a reorganização da biblioteca Zotero motivada por 3 problemas:

1. **Metadados mal organizados** — múltiplas raízes competindo (`MancanoLibrary`, `00_Important_reading`, `01_Ongoing_Projects`, `ZZ_Old_Group_libs`), prefixos inconsistentes (`00_`, `01_`, `ZZ_`), duplicação semântica (`Mov Estudantil` 360 + `Movimento Estudantil` 57), 14 pastas `Temp/Temp2/.../Temp10` acumuladas, mistura de eixos (tópico + autor + curso + status) num mesmo nível.

2. **Duplicações** — 59 grupos por DOI (um livro Cambridge tinha **7 cópias**!), 43 por ISBN (um livro Oxford com **12 cópias**), 99 por título+ano normalizados.

3. **Metadados incompletos** — 274 artigos sem DOI, 98 livros sem ISBN, 288 itens sem autor, 345 sem data, 1.330 sem resumo.

Em **10/05/2026** executamos 8 scripts JS (A–H) que reorganizaram a estrutura: criamos 56 coleções novas em árvore consensuada (`1. Active Research` → `9. Archive`), migramos pastas temp pro `2. Workbench` com nomenclatura `YYYY-MM-DD`, dissolvemos 8 pastas-autor em tags `author-focus:*`, consolidamos os 4 projetos ativos, arquivamos containers legados inteiros (`MancanoLibrary`, `ZZ_Old_Group_libs`, `00_Important_reading`, `01_Ongoing_Projects`) sob `9. Archive` pra preservação.

**Status atual** (30/05/2026): estrutura nova montada e populada parcialmente. Falta distribuir ~3.000 itens substantivos do archive pras Fields, tratar 200+ duplicatas, e recuperar metadados faltantes.

## Estrutura da nova biblioteca

```
📚 (raiz Zotero)
├── 1. Active Research      Projetos com prazo (Master's, BEPE, IC orientações)
├── 2. Workbench            Pastas datadas YYYY-MM-DD de trabalho ad-hoc
├── 3. Fields               Conhecimento permanente, organizado por disciplina
│   ├── ★ Theory & Methodology   (transversal, prioritário)
│   ├── Economics
│   ├── Education                (interdisciplinar)
│   ├── Political Science
│   └── Sociology
├── 4. Coursework           Disciplinas cursadas, nomeadas YYYY-S — Nome
├── 5. Bureaucracy & Documents   CVs, syllabi, documentos pessoais
├── 6. Leisure Reading      Leituras de entretenimento intelectual
├── 7. Misc                 Inclui AI Outputs (fichamentos gerados por IA)
└── 9. Archive              Legado preservado pra consulta histórica
```

## Como navegar este repositório

| Arquivo | Para quê |
|---------|----------|
| `README.md` | Você está aqui. Visão geral + por que. |
| `PLAN.md` | Plano vivo: o que falta, em que ordem, por quê. |
| `NEWS.md` | Log cronológico com timestamp de cada ação executada. |
| `CONVENTIONS.md` | Padrões: nomenclatura "data-primeiro", vocabulário de tags, regras de classificação. |
| `BACKUPS.md` | Inventário de snapshots SQLite + procedimento de restauração. |
| `scripts/` | Scripts JS pra rodar no Zotero (`Tools → Developer → Run JavaScript`). |
| `diagnostics/` | Snapshots `.sqlite` (read-only) e relatórios `.md` datados. |
| `python/` | Scripts Python pra análise (queries SQL, comparações temporais). |

## Como continuar o trabalho

1. Sempre começar lendo `PLAN.md` pra ver o próximo passo
2. Antes de qualquer operação destrutiva: snapshot pra `diagnostics/` (ver `BACKUPS.md`)
3. Rodar scripts JS via Zotero (`Tools → Developer → Run JavaScript`), colando o conteúdo do arquivo
4. Logar tudo no `NEWS.md` com timestamp + comando + resultado
5. Atualizar `PLAN.md` ao fechar fases

## Convenções de versão

- Scripts JS são nomeados `<Letra>_<descrição>.js` (A_cleanup, B_create_structure, …) em ordem cronológica de execução
- Snapshots `.sqlite` são datados `zotero_snap_YYYY-MM-DD[_HHMM].sqlite`
- Relatórios são datados `YYYY-MM-DD_relatorio.md`
