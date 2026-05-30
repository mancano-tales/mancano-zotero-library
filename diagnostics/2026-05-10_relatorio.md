# Diagnóstico da Biblioteca Zotero

Banco analisado: `C:\Users\Mancano\Zotero\_diagnostico\zotero_readonly.sqlite`  
(cópia read-only de `zotero.sqlite.bak` — biblioteca ativa NÃO foi tocada)

## 1. Visão geral

- **Itens bibliográficos** (excl. anexos/notas/lixeira): **2,337**
- **Anexos** (PDFs, links, etc.): **2,417**
- **Notas**: **525**
- **Itens na lixeira**: **45**
- **Coleções**: **186**
- **Tags distintas**: **578**

### Distribuição por tipo de item

| Tipo | Quantidade |
|------|-----------:|
| journalArticle | 1,070 |
| book | 632 |
| webpage | 248 |
| bookSection | 139 |
| document | 58 |
| blogPost | 58 |
| thesis | 47 |
| report | 19 |
| preprint | 16 |
| presentation | 12 |
| videoRecording | 10 |
| manuscript | 10 |
| encyclopediaArticle | 5 |
| newspaperArticle | 4 |
| dataset | 3 |
| computerProgram | 2 |
| statute | 1 |
| film | 1 |
| conferencePaper | 1 |
| case | 1 |

## 2. Metadados incompletos

| Problema | Itens afetados |
|----------|---------------:|
| Sem título | 3 |
| Sem nenhum autor/creator | 288 |
| Sem data/ano | 345 |
| Artigos sem `publicationTitle` (journal) | 185 |
| Artigos sem DOI | 274 |
| Livros sem ISBN | 98 |
| Livros sem editora | 18 |
| Sem resumo (abstractNote) | 1,330 |

## 3. Duplicatas suspeitas

### Por DOI: **59** grupos duplicados

| DOI | # cópias | itemIDs |
|-----|---------:|---------|
| `10.1017/CBO9780511510175` | 7 | 8861,11864,11861,11860,11857,11859,11863 |
| `https://doi.org/10.1093/oso/9780197817094.001.0001` | 3 | 12136,12137,12140 |
| `10.4337/9781035371341` | 3 | 11882,11885,11886 |
| `10.1590/0102-4698162030` | 3 | 10219,11729,11771 |
| `10.11606/T.8.2022.tde-22092022-152626` | 3 | 734,11911,11912 |
| `10.1017/ics.2023.16` | 3 | 8845,11603,11784 |
| `10.9771/ccrh.v38i0.65098` | 2 | 11872,11878 |
| `10.9771/ccrh.v38i0.65016` | 2 | 11871,11879 |
| `10.7476/9788575114797` | 2 | 584,585 |
| `10.7476/9786550190071` | 2 | 8440,8443 |
| `10.48550/ARXIV.2107.02637` | 2 | 6905,6907 |
| `10.4337/9781789909432` | 2 | 11144,11145 |
| `10.3982/ECTA8121` | 2 | 9417,9424 |
| `10.3386/w31492` | 2 | 10830,11835 |
| `10.20336/rbs.836` | 2 | 872,6254 |
| `10.20336/rbs.781` | 2 | 11141,11638 |
| `10.17666/3088129-143/2015` | 2 | 825,831 |
| `10.1590/s1414-40772017000200002` | 2 | 419,431 |
| `10.1590/S0103-40141994000300043` | 2 | 9383,9407 |
| `10.1590/s0102-699220183302008` | 2 | 149,3718 |

_…e mais 39 grupos_


### Por ISBN: **43** grupos duplicados

| ISBN | # cópias | itemIDs |
|------|---------:|---------|
| `978-0-19-780318-9 978-0-19-780321-9` | 12 | 7749,7750,7751,7752,7753,7754,7760,7762,7763,7764,7765,7766 |
| `978-0-521-88725-0` | 6 | 11863,11861,11860,11859,11864,11857 |
| `978-1-78990-943-2 978-1-78990-942-5` | 5 | 11143,11144,11145,11146,11147 |
| `978-0-521-41780-8 978-0-521-42830-9 978-0-511-52812-5` | 5 | 736,738,739,936,937 |
| `978-0-19-954846-0 978-0-19-157742-0` | 5 | 1012,1013,1014,1016,1017 |
| `978-1-107-11002-1 978-1-316-27310-4 978-1-107-52563-4` | 4 | 5022,5023,5285,8374 |
| `978-1-0353-7134-1` | 4 | 11873,11882,11885,11886 |
| `978-0-521-11883-5 978-0-521-13432-3 978-0-511-80641-4` | 4 | 760,761,5281,5337 |
| `978-0-19-882838-9 978-0-19-186699-9` | 4 | 588,677,826,8883 |
| `978-85-9546-365-3` | 3 | 47,48,575 |
| `978-65-5019-007-1` | 3 | 8437,8440,8443 |
| `978-1-009-42868-2 978-1-009-42864-4 978-1-009-42863-7` | 3 | 10309,10852,11764 |
| `978-0-691-22089-5` | 3 | 11487,11488,11489 |
| `978-0-521-84304-1 978-0-521-60381-2 978-0-511-48890-0` | 3 | 1061,1083,1129 |
| `978-0-521-81610-6 978-0-521-01645-2 978-0-511-80396-3` | 3 | 762,1011,8385 |
| `978-0-19-924775-2 978-0-19-159634-6` | 3 | 730,731,869 |
| `978-0-19-775885-4 978-0-19-775889-2` | 3 | 868,1149,11475 |
| `978-85-7811-277-6` | 2 | 755,756 |
| `978-85-7511-479-7` | 2 | 584,585 |
| `978-85-7001-024-7` | 2 | 8016,8058 |

_…e mais 23 grupos_


### Por título+ano normalizados: **99** grupos

| Título (truncado) | Ano | # cópias | itemIDs |
|-------------------|-----|---------:|---------|
| agents of reform: child labor and the origins of the welfare state | 2021 | 4 | 11487,11488,11489,11595 |
| lei de cotas: mudança estrutural em política pública e vitória suprapartidária d | 2022 | 3 | 734,11911,11912 |
| o ponto a que chegamos: duzentos anos de atraso educacional e seu impacto nas po | 2022 | 3 | 11477,11631,11632 |
| polÍtica de expansÃo da educaÇÃo superior no brasil - o prouni e o fies como fin | 2016 | 3 | 10219,11729,11771 |
| redistributing tertiary education? | ? | 3 | 11779,11780,11781 |
| welfare regimes in twenty-first-century latin america | 2023 | 3 | 8845,11603,11784 |
| 1.2 orientador/supervisor: | ? | 2 | 10832,11600 |
| a formação do mst no brasil | 2000 | 2 | 11870,11880 |
| a new history of modern computing | 2021 | 2 | 7235,7236 |
| a trajetória da assistência estudantil na educação superior brasileira | 2017 | 2 | 438,440 |
| affirmative action and the choice of schools | 2023 | 2 | 5446,10161 |
| affirmative action in brazilian universities: effects on the enrollment of targe | 2019 | 2 | 5517,10804 |
| african slavery and the reckoning of brazil | ? | 2 | 11464,11465 |
| american bonds: how credit markets shaped a nation | 2021 | 2 | 11285,11303 |
| analytical sociology and its critics | 2010 | 2 | 995,1006 |
| antropologia da solidariedade | 2007 | 2 | 166,3706 |
| at which age is education the great equalizer? a causal mediation analysis of th | 2022 | 2 | 5513,7319 |
| caixa robusto será mantido a despeito da queda do juro | 2012 | 2 | 9221,9273 |
| campanhas e ações dos territórios | ? | 2 | 141,3769 |
| careless people | ? | 2 | 12126,12201 |
| coerção e consenso: a questão social, o federalismo e o legislar sobre o trabalh | 2016 | 2 | 8060,8670 |
| collective skill systems, wage bargaining, and labor market stratification | 2011 | 2 | 238,508 |
| comparative capitalism, growth models and emerging markets: the development of t | 2020 | 2 | 352,486 |
| conclusion: if “class” is the answer, what is the question? | 2005 | 2 | 1061,1083 |
| covid 19 | ? | 2 | 159,3704 |
| cuba's academic advantage: why students in cuba do better in school | 2007 | 2 | 11174,11193 |
| departamento de ciência política | 1994 | 2 | 9383,9407 |
| diferenciação institucional e desigualdades no ensino superior | 2015 | 2 | 825,831 |
| diversifying society’s leaders? the determinants and causal effects of admission | 2023 | 2 | 10830,11835 |
| does it matter which institution you choose? a case study of brazilian graduate  | 2025 | 2 | 11811,11836 |

_…e mais 69 grupos_


## 4. Anexos e PDFs

- **Itens sem nenhum anexo**: 398
- **Anexos órfãos** (sem item-pai): 241

### Tipos de anexo

| contentType | n |
|-------------|---:|
| application/pdf | 1,864 |
| text/html | 330 |
| application/epub+zip | 196 |
| _(vazio)_ | 11 |
| application/vnd.openxmlformats-officedocument.presentationml.presentation | 7 |
| application/octet-stream | 4 |
| application/vnd.openxmlformats-officedocument.wordprocessingml.document | 3 |
| image/jpeg | 1 |
| image/png | 1 |

## 5. Coleções

- **Itens fora de qualquer coleção**: 157

### Top 15 coleções por tamanho

| Coleção | Itens |
|---------|------:|
| Mov Estudantil | 360 |
| z99_Graduação | 358 |
| references | 127 |
| Temp6 | 90 |
| 00_Important_reading | 89 |
| 2026_01_ProUni_Cotas_Policy_Process | 88 |
| ZZ_Old_Group_libs | 83 |
| Empresariado | 83 |
| Topicos de Política Comparada | 80 |
| Miscelanea | 73 |
| Leituras Engajantes | 71 |
| Temp | 68 |
| 7.3NiHistorical - Theory and Genesis | 62 |
| Movimento Estudantil | 57 |
| 01_Ver e Classificar as Novidades | 56 |

### Coleções vazias: **16**

- S0276562416301251
- Teste
- Primo_RIS_Export
- Florestan Fernandes
- Sociology Education/Stratification
- @Voice-2025-3-22
- references.bib
- 8 Disciplinas
- Causality
- citationExport-acrefore-9780190264093-e-1679
- 3. Topics & Contries
- Talita
- Mixtape Sessions
- Important Handbooks to Stay Aware of
- 2025-10-28_Politics-of-Inequality_Marius-Busemeyer
- Class 6

## 6. Tags

- **Tags usadas 1x ou menos**: 476

- **Tags com variantes de caixa/espaço** (mesmo lower(): diferentes originais): 14

| Forma normalizada | Variantes |
|-------------------|-----------|
| `authoritarianism` | `Authoritarianism` / `authoritarianism` |
| `political science / history & theory` | `POLITICAL SCIENCE / History & Theory` / `Political Science / History & Theory` |
| `social policy` | `Social policy` / `Social Policy` |
| `political science / general` | `Political Science / General` / `POLITICAL SCIENCE / General` |
| `education` | `Education` / `education` |
| `covid-19` | `COVID-19` / `covid-19` |
| `desigualdade` | `Desigualdade` / `desigualdade` |
| `higher education` | `higher education` / `Higher education` / `Higher Education` |
| `politics and government` | `Politics and government` / `Politics and Government` |
| `political science` | `Political science` / `Political Science` |
| `human capital` | `Human capital` / `human capital` |
| `social sciences` | `Social sciences` / `Social Sciences` |
| `democracia` | `democracia` / `Democracia` |
| `democracy` | `Democracy` / `democracy` |

### Top 20 tags mais usadas

| Tag | n |
|-----|---:|
| zotmoov | 530 |
| History | 20 |
| United States | 16 |
| Social sciences | 16 |
| Philosophy | 12 |
| Ciência política | 11 |
| Methodology | 11 |
| Brazil | 10 |
| Educação | 10 |
| /done | 9 |
| Politics and government | 9 |
| Education | 7 |
| Education and state | 7 |
| Economics | 7 |
| Research | 7 |
| Democracy | 7 |
| 20th century | 6 |
| Social policy | 6 |
| Economic aspects | 6 |
| Equality | 6 |

## 7. Better BibTeX (citation keys)

- Arquivo `better-bibtex.sqlite` não encontrado (talvez ainda não inicializado)

## 8. Resumo executivo

| Categoria | Quantidade |
|-----------|-----------:|
| Duplicatas (DOI) | 59 |
| Duplicatas (ISBN) | 43 |
| Duplicatas (título+ano) | 99 |
| Sem autor | 288 |
| Sem ano | 345 |
| Artigos sem DOI | 274 |
| Livros sem ISBN | 98 |
| Itens sem anexo | 398 |
| Anexos órfãos | 241 |
| Itens fora de coleção | 157 |
| Tags com variantes de caixa | 14 |
| Tags usadas <=1x | 476 |
