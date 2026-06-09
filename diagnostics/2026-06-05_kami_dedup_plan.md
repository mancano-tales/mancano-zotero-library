# Plano de Dedup — Kami Uploads 2026-06-05

**Destino dos movidos**: `G:\My Drive\[[1]] Kami Uploads\_TRASH_dedup_2026-06-05\` (subpasta de Kami Uploads, você revisa manualmente)

## Resumo

- Grupos de hash com 2+ cópias: **361**
- Grupos com pelo menos 1 cópia linkada no Zotero: **212**
- Grupos que precisam de **repoint do Zotero** (2+ links no mesmo conteúdo): **31**
- Arquivos a mover para `_TRASH_dedup_2026-06-05\`: **402**
- Tamanho a liberar da raiz/subpastas: **1.37 GB**
- Arquivos movidos que estão linkados (precisam repoint): **31**

## Regras aplicadas

1. Se 1+ cópia do grupo é linkada por algum item do Zotero: **canonical = primeira linkada**.
   Se 2+ são linkadas: as demais geram entrada para repoint (script JS auxiliar).
2. Se NENHUMA é linkada: **canonical = na raiz com nome mais curto** (fallback: path mais raso).
3. Movidos vão para subpasta TRASH com nome `<canonical>__dup_N__<original_short>.ext`
   para facilitar comparação visual quando você conferir.

## Top 30 grupos (mais cópias)

| # cópias | Canonical | Linkado? | Subdir canonical |
|---:|-----------|:--------:|------------------|
| 4 | `Wright, E. O. (Ed.). (2005). Approaches to class analysis. Cambridge U` | — | 01_Syllabi |
| 3 | `Barbosa, M. L. de O., & Gandin, . L. A. (2020). Sociologia da educação` | — | (root) |
| 3 | `Kosack - 2012 - The education of nations how the political organizatio` | ✓ | (root) |
| 3 | `Ribeiro - 2011 - Desigualdade de Oportunidades e Resultados Educaciona` | ✓ | (root) |
| 3 | `Theodoro - 2019 - A implementação de uma agenda racial de políticas pú` | ⚠️ 2 | (root) |
| 3 | `Flores - 2017 - A política da política de salário mínimo no Brasil.pdf` | ✓ | (root) |
| 3 | `Diani Mario (1992) The concept of social movement.pdf` | — | (root) |
| 3 | `Clift - 2014 - Comparative Political Economy.pdf` | ✓ | (root) |
| 3 | `Barbosa - 2016 - Desigualdade de Rendimentos do Trabalho no Curto e no` | ✓ | (root) |
| 3 | `Crowley-RushOrganizeExplaining-2001.pdf` | — | (root) |
| 3 | `Manzo - 2010 - Analytical Sociology and Its Critics.pdf` | ⚠️ 2 | (root) |
| 3 | `Mahoney - 2008 - Toward a Unified Theory of Causality.pdf` | ✓ | (root) |
| 3 | `Mahlmeister - 2021 - Quem Paga pelo Estado de Bem-estar.pdf` | ✓ | (root) |
| 3 | `Costa - 2022 - O papel esquecido do Poder Legislativo na trajetória da` | ✓ | (root) |
| 3 | `Frank Dobbin - Stanford's Organization Theory Renaissance, 1970-2000, ` | — | (root) |
| 3 | `Schrank - 2022 - Economic Sociology of Development.epub` | ✓ | (root) |
| 3 | `Schrank, A. (2023). The Economic Sociology of Development.pdf` | — | (root) |
| 3 | `Melo, N. (2023) Diâmetro da agulha_ Alcance de oportunidades acadêmica` | — | (root) |
| 3 | `Page and Gilens - 2017 - Democracy in America.epub` | ✓ | (root) |
| 3 | `Treiman, D. (1970). Industrialization and Social Stratification.pdf` | — | (root) |
| 3 | `Johnson - 2007 - MITI and the Japanese miracle the growth of industria` | ✓ | (root) |
| 3 | `Mahoney and Rueschemeyer - 2003 - Comparative Historical Analysis in t` | ✓ | (root) |
| 3 | `Elster - 2007 - Explaining social behavior more nuts and bolts for the` | ⚠️ 2 | (root) |
| 3 | `Tieben and Wolbers - 2010 - Transitions to post-secondary and tertiary` | ⚠️ 2 | (root) |
| 3 | `Almeida - 2012 - Ampliação do acesso ao ensino superior privado lucrat` | ✓ | (root) |
| 3 | `Boix - 2003 - Democracy and redistribution.pdf` | ✓ | (root) |
| 3 | `Batista da Silva et al. - 2024 - Rethinking Readings About the Past of` | ✓ | (root) |
| 3 | `Spirling and Stewart - 2025 - What Good Is a Regression Inference to t` | ✓ | (root) |
| 3 | `Skocpol - 1980 - Political Response to Capitalist Crisis Neo-Marxist T` | ✓ | (root) |
| 3 | `Deane, G. (1994). The Constant Flux- A Study of Class Mobility in Indu` | — | 01_Syllabi |

## Grupos que precisam de repoint do Zotero

Items abaixo apontam pra cópias que vão pra TRASH. Script `M_kami_dedup_repoint.js` re-aponta esses items pro canonical do grupo.

| itemID(s) | canonical | # cópias |
|---|---|---:|
| 5271 | `Theodoro - 2019 - A implementação de uma agenda racial de políticas pú` | 3 |
| 10866 | `Huber and Stephens - 2024 - Challenging Inequality Variation across Po` | 2 |
| 12516 | `Schwartzman et al. - 2015 - Higher Education in the BRICS Countries In` | 2 |
| 1462 | `Busemeyer and Thelen - 2020 - Institutional Sources of Business Power.` | 2 |
| 2609 | `SOCIAL MOBILITY IN EUROPE; ED_ BY RICHARD BREEN -- Breen, Richard (Edi` | 2 |
| 933 | `Iversen - 2005 - Capitalism, democracy, and welfare.pdf` | 2 |
| 11011 | `Custódio - 2022 - Lei de cotas mudança estrutural em política pública ` | 2 |
| 2616 | `Manzo - 2010 - Analytical Sociology and Its Critics.pdf` | 3 |
| 6380 | `Becker - 1964 - Human Capital A Theoretical and Empirical Analysis, wi` | 2 |
| 6193 | `Goldthorpe - 2006 - On Sociology. Volume One Critique and program.pdf` | 2 |
| 5086 | `Folha de S.Paulo - 2004 - Autores apontam caminhos para a política ind` | 2 |
| 10850 | `Boudon - 1974 - Education, opportunity, and social inequality changing` | 2 |
| 5693 | `Elster - 2007 - Explaining social behavior more nuts and bolts for the` | 3 |
| 7338 | `Tieben and Wolbers - 2010 - Transitions to post-secondary and tertiary` | 3 |
| 7343 | `Dixit - 2023 - The impact of welfare on inter-group relations Caste-ba` | 2 |
| 9678 | `Stevens et al. - 2008 - Sieve, Incubator, Temple, Hub Empirical and Th` | 2 |
| 6893 | `Gjerløw et al. - 2022 - One Road to Riches How State Building and Demo` | 2 |
| 11451 | `Lindvall and Rothstein - 2006 - Sweden The Fall of the Strong State.pd` | 2 |
| 7007 | `King and Nielsen - 2019 - Why Propensity Scores Should Not Be Used for` | 2 |
| 8667 | `de Araujo Alves et al. - 2022 - O percurso histórico do ensino médio b` | 2 |
| 8077 | `Oliveira - 2016 - Coerção e consenso a questão social, o federalismo e` | 2 |
| 11523 | `Ferre - 2023 - Welfare regimes in twenty-first-century Latin America.p` | 2 |
| 11258 | `Seeleib-Kaiser et al. - 2012 - Shifting the Public-Private Mix A New D` | 2 |
| 9779 | `Social Policy in the United States _ Future Possibilities in -- Theda ` | 2 |
| 11535 | `Berger and Prawitz - 2024 - Inventors among the “Impoverished Sophisti` | 2 |
| 9794 | `Palmisano et al. - 2022 - Inequality of Opportunity in Tertiary Educat` | 2 |
| 10823 | `Offe_16294480.pdf` | 2 |
| 11560 | `Tomás and Silveira - 2021 - Expansão do ensino superior no Brasil dive` | 2 |
| 11547 | `Engerman and Sokoloff - 2005 - The Evolution of Suffrage Institutions ` | 2 |
| 11236 | `civil-society-and-financial-regulation-consumer-finance-protection-and` | 2 |
| 11802 | `Haber et al. - 2021 - The Ecological Origins of Economic and Political` | 2 |

## Exemplos de arquivos que serão movidos (primeiros 20)

| Src (subdir) | Dst (nome em TRASH) |
|--------------|---------------------|
| `Parsons, Parsons et al (em português).pdf` | `Parsons, Parsons et al (em português) 1__dup_1__Parsons, Parsons et al (em portu` |
| `Parsons_Talcott(1991)_The Social System_Routledgeundefined (Z-Library).pdf` | `Parsons - The Social System (1991)__dup_1__Parsons_Talcott(1991)_The Social Syst` |
| `Parsons.O sistema-das-sociedades-modernas (1974).pdf` | `Parsons.O sistema-das-sociedades-modernas (1974) 1__dup_1__Parsons.O sistema-das` |
| `Marion Fourcade, Kieran Healy_(2024)_The Ordinal Society_Harvard University Pres` | `Fourcade and Healy - 2024 - The ordinal society__dup_1__Marion Fourcade, Kieran ` |
| `A10 Abbott 2016 Cap. 7 Social Order and Process em Processual Sociology.pdf` | `Abbott - 2016 - Processual Sociology__dup_1__A10 Abbott 2016 Cap. 7 Social Order` |
| `_Fix\Literatura de FLS6101 – Teoria e Metodologia em Ciência Política – Adrian G` | `07b-Mahoney, Kimball, Kendra The Logic of Historical Explanation pt__dup_1__07b-` |
| `Jardim, F. A., & Almeida, W. M. (2016). Expansão recente do ensino superior bras` | `Jardim and Almeida - 2016 - Expansão recente do Ensino Superior brasileiro (novo` |
| `LIPSET notebooklm.google.com-Higher Education Welfare State e Varieties of Capit` | `Lipset and Bendix - 1959 - Social Mobility in Industrial Society 1__dup_1__LIPSE` |
| `Vilela, E. M., Collares, A. C. (2009) Origens e destinos sociais.pdf` | `Vilela and Collares - 2009 - Origens e destinos sociais pode a escola quebrar es` |
| `Gosta Esping-Andersen_(—)_Social Foundations of Postindustrial Economies_OUP Oxf` | `Esping-Andersen - 1999 - Social foundations of postindustrial economies__dup_1__` |
| `Barbosa, & Gandin (2020). Sociologia da educação brasileira- diversidade e quali` | `Barbosa, M. L. de O., & Gandin, . L. A. (2020). Sociologia da educação brasileir` |
| `Barbosa, & Gandin (2020). Sociologia da educação brasileira- diversidade e quali` | `Barbosa, M. L. de O., & Gandin, . L. A. (2020). Sociologia da educação brasileir` |
| `Blossfeld, H. P., & Shavit, Y. (1991). Persisting Barriers- Changes in Education` | `Shavit and Blossfeld - 1993 - Persistent Inequality Changing Educational Attainm` |
| `Parsons, T. (1970). Equality and inequality in modern society, or social stratif` | `Parsons1970 - Equality and Inequality in Modern Society, or Social Stratificatio` |
| `Erikson & Jonsson (1996) (Eds.) Can Education Be Equalized  The Swedish Case in ` | `Erikson and Jonsson - 1996 - Can Education Be Equalized The Swedish Case in Comp` |
| `Blössfeld, H. P., & Shavit, Y. (1992). Persisting barriers- Changes in education` | `Shavit and Blossfeld - 1993 - Persistent Inequality Changing Educational Attainm` |
| `Parsons, T. (1970). Equality and inequality in modern society, or social stratif` | `Parsons - 1970 - Equality and Inequality in Modern Society, or Social Stratifica` |
| `Parsons, T. George M. Platt. (1973). The American University. Harvard University` | `Parsons and Platt - THE AMERICAN UNIVERSITY__dup_1__Parsons, T. George M. Platt.` |
| `Sonia Draibe 1993.pdf` | `CadPesq_08__dup_1__Sonia Draibe 1993.pdf` |
| `Sonia Draibe 3 HÁ TENDÊNCIAS E TEDÊNCIAS- COM QUE ESTADO DE BEM ESTAR SOCIAL HAV` | `CadPesq_10__dup_1__Sonia Draibe 3 HÁ TENDÊNCIAS E TEDÊNCIAS- COM QUE ESTADO DE.p` |