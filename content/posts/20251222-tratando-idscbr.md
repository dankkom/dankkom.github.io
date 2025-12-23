---
title: "Guia Completo: Coletando e Tratando Dados do IDSCBR com R"
date: 2025-12-23T11:00:00-03:00
author: Komesu, D. K.
slug: coletando-tratando-dados-idscbr-r
categories: ["R", "Data Science", "Sustentabilidade"]
tags: ["R", "Data Wrangling", "IDSCBR", "Sustentabilidade", "Análise de Dados"]
description: "Aprenda como coletar, tratar e organizar os dados do Índice de Desenvolvimento Sustentável dos Municípios Brasileiros (IDSCBR) utilizando R. Um guia detalhado para análise eficiente."
---

O **Índice de Desenvolvimento Sustentável dos Municípios Brasileiros (IDSCBR)** é uma métrica essencial para avaliar o progresso sustentável em diferentes regiões do Brasil. Neste artigo, você aprenderá, passo a passo, como coletar e tratar esses dados utilizando a linguagem R, uma ferramenta poderosa para análise de dados.

## Por que o IDSCBR é importante?

O IDSCBR fornece informações valiosas sobre o desempenho dos municípios em relação aos Objetivos de Desenvolvimento Sustentável (ODS). Com esses dados, é possível identificar áreas de melhoria e planejar ações estratégicas para promover o desenvolvimento sustentável.

## O que é o IDSCBR?

O IDSCBR (Índice de Desenvolvimento Sustentável dos Municípios Brasileiros) é uma iniciativa que busca mensurar o progresso dos municípios brasileiros em relação aos Objetivos de Desenvolvimento Sustentável (ODS) da ONU. Ele reúne dados de diversas áreas — saúde, educação, meio ambiente, economia, infraestrutura, entre outras — e permite comparações entre cidades, regiões e estados, auxiliando gestores públicos, pesquisadores e cidadãos na tomada de decisões.

## Fontes dos Dados e Atualização

Os dados do IDSCBR são compilados a partir de fontes oficiais, como IBGE, Ministério da Saúde, INEP, SNIS, entre outros. A atualização periódica garante que as análises reflitam a realidade mais recente dos municípios, tornando o índice uma ferramenta confiável para monitoramento e planejamento.

## Exemplos de Aplicações Práticas

- **Gestão Pública:** Identificação de áreas prioritárias para investimento e políticas públicas.
- **Pesquisa Acadêmica:** Estudos sobre desigualdade, saúde pública, educação, sustentabilidade ambiental, etc.
- **Sociedade Civil:** Monitoramento de indicadores e cobrança de ações dos gestores.

## Pré-requisitos

Antes de começar, certifique-se de ter o R instalado em sua máquina. Além disso, instale os pacotes necessários com o comando abaixo:

```R
install.packages(c("readxl", "dplyr", "tidyr", "stringr", "tibble", "readr", "ggplot2"))
```

## Passo 1: Coletando os Dados

Os dados do IDSCBR estão disponíveis em um arquivo Excel no site oficial. O código abaixo faz o download e prepara os dados para análise:

```R
url <- "https://www.cidadessustentaveis.org.br/arquivos/idsc-br/Base_de_Dados_IDSC-BR_2023.xlsx"
data_raw_dir <- "data-raw"
destfile <- file.path(data_raw_dir, "Base_de_Dados_IDSC-BR_2023.xlsx")
if (!file.exists(destfile)) {
  if (!dir.exists(data_raw_dir)) {
    dir.create(data_raw_dir)
  }
  download.file(url, destfile, mode = "wb")
}
data_dir <- "data"
if (!dir.exists(data_dir)) {
  dir.create(data_dir)
}
```

## Passo 2: Tratando os Dados

### Extraindo Indicadores

O código a seguir organiza os indicadores do IDSCBR:

```R
ods_indicators <- readxl::read_excel(destfile, sheet = "Todos os Dados") |>
  dplyr::select(id, 43:442)

idscbr2023 <- tibble::tibble()

for (i in 1:100) {
  a <- 1 + (i * 4) - 3
  b <- a + 3

  ods_indicator <- ods_indicators |>
    dplyr::select(id, dplyr::all_of(a:b))

  indicator_columns <- names(ods_indicator)

  ods_indicator <- ods_indicator |>
    dplyr::mutate(
      indicator_id = stringr::str_split(indicator_columns[2], ": ")[[1]][1],
      indicator_name = stringr::str_split(indicator_columns[2], ": ")[[1]][2],
    ) |>
    dplyr::rename(
      municipality_id = 1,
      indicator_value = 2,
      year = 3,
      indicator_value_normalized = 4,
      color = 5,
    ) |>
    dplyr::filter(!is.na(indicator_value))

  idscbr2023 <- dplyr::bind_rows(idscbr2023, ods_indicator)
}

readr::write_csv(idscbr2023, "data/idscbr2023.csv")
```

### Análise Temporal

Para análises temporais, utilize o seguinte código:

```R
idscbr2023_ts <- readxl::read_excel(destfile, sheet = "Séries Temporais") |>
  dplyr::select(id, ano, 4:103) |>
  tidyr::pivot_longer(
    cols = -c(id, ano),
    names_to = "indicator",
    values_to = "indicator_value"
  ) |>
  dplyr::rename(
    municipality_id = id,
    year = ano
  ) |>
  dplyr::filter(!is.na(indicator_value))

readr::write_csv(idscbr2023_ts, "data/idscbr2023_ts.csv")
```

### Dados Regionais e Metas

Extraia informações regionais e pontuações de metas com os códigos abaixo:

```R
ods_reg <- readxl::read_excel(destfile, sheet = "Todos os Dados") |>
  dplyr::select(id, 26:42) |>
  tidyr::pivot_longer(
    cols = -id,
    names_to = "ODS reg",
    values_to = "ODS reg Value"
  ) |>
  dplyr::mutate(
    year = 2023,
    `ODS reg` = as.numeric(stringr::str_extract(`ODS reg`, "\\d+"))
  ) |>
  dplyr::rename(
    municipality_id = id
  )

readr::write_csv(ods_reg, "data/ods_reg_2023.csv")
```

```R
goalscores <- readxl::read_excel(destfile, sheet = "Todos os Dados") |>
  dplyr::select(id, 9:25) |>
  tidyr::pivot_longer(
    cols = -id,
    names_to = "Goal Score",
    values_to = "Goal Score Value"
  )

readr::write_csv(goalscores, "data/idscbr2023_goalscores.csv")
```

```R
idscbr2023_municipalities <- readxl::read_excel(destfile, sheet = "Todos os Dados") |>
  dplyr::select(id, 2:8) |>
  dplyr::transmute(
    municipality_id = id,
    municipality_name = `Município`,
    uf_abbrev = `UF`,
    idsc2023 = `Pontuação Indice ODS 2023`,
    classification_idsc2023 = `Classificação 2023`,
    population2023 = `População_2022`,
    missing_values = `Valores faltantes`,
    missing_values_percentage = `Porcentagem valores faltantes`
  )
readr::write_csv(idscbr2023_municipalities, "data/idscbr2023_municipalities.csv")
```

### Dicionário de Indicadores

```R
idscbr2023_dict <- readxl::read_excel(destfile, sheet = "Livro de Códigos") |>
  dplyr::filter(!is.na(Arquivo))

readr::write_csv(idscbr2023_dict, "data/idscbr2023_dict.csv")
```

## Explorando os Dados com Visualizações

Após organizar os dados, é essencial criar visualizações para compreender melhor as informações. Aqui estão algumas sugestões de gráficos que você pode criar utilizando o pacote `ggplot2`:

### Gráfico de Histograma

Primeiro, carregue os dados tratados:

```R
library(ggplot2)
dados <- readr::read_csv("data/idscbr2023.csv")
```

Dando uma olhada nos nomes dos indicadores disponíveis:

```R
unique(dados$indicator_name)
```

```text
  [1] "Famílias inscritas no Cadastro Único para programas sociais (%)"
  [2] "Percentual de pessoas inscritas no Cadastro Único que recebem Bols"
  [3] "Percentual de pessoas abaixo da linha da pobreza no Cadastro Único p"
  [4] "Pessoas com renda de até 1/4 do salário mínimo (%)"
  [5] "Obesidade infantil (%)"
  [6] "Baixo peso ao nascer (%)"
  [7] "Desnutrição infantil (%)"
  [8] "Produtores de agricultura familiar com apoio do PRONAF (%)"
  [9] "Estabelecimentos que praticam agricultura orgânica (%)"
 [10] "Cobertura de vacinas (%)"
 [11] "Mortalidade por suicídio (100 mil habitantes)"
 [12] "Mortalidade infantil (crianças menores de 1 ano) (mil nascidas"
 [13] "Mortalidade materna (mil nascidos vivos)"
 [14] "Mortalidade na infância (crianças menores de 5 anos de idade) (m"
 [15] "Mortalidade neonatal (crianças de 0 a 27 dias) (mil nascidas viv"
 [16] "Mortalidade por Aids (100 mil habitantes)"
 [17] "Incidência de dengue (100 mil habitantes)"
 [18] "Mortalidade por doenças crônicas não-transmissíveis  (100 mil ha"
 [19] "Orçamento municipal para a saúde (em reais, per capita)"
 [20] "População atendida por equipes de saúde da família (%)"
 [21] "Detecção de hepatite ABC (100 mil habitantes)"
 [22] "Pré-natal insuficiente (%)"
 [23] "Unidades Básicas de Saúde (mil habitantes)"
 [24] "Esperança de vida ao nascer (anos)"
 [25] "Gravidez na adolescência (%)"
 [26] "Incidência de tuberculose (100 mil habitantes)"
 [27] "Acesso à internet nas escolas do ensino fundamental (%)"
 [28] "Escolas com dependências adequadas a pessoas com deficiência  ("
 [29] "Escolas com recursos para Atendimento Educacional Especializado"
 [30] "Índice de Desenvolvimento da Educação Básica (IDEB) - anos fina"
 [31] "Índice de Desenvolvimento da Educação Básica (IDEB) - anos inic"
 [32] "Jovens com ensino médio concluído até os 19 anos de idade (%)"
 [33] "Professores com formação em nível superior - Educação Infantil"
 [34] "Professores com formação em nível superior - Ensino Fundamenta"
 [35] "Prova Brasil - Língua portuguesa - Anos Finais do Ensino Funda"
 [36] "Prova Brasil - Língua portuguesa - Anos Iniciais do Ensino Fun"
 [37] "Prova Brasil - Matemática - Anos Finais do Ensino Fundamental -"
 [38] "Prova Brasil - Matemática - Anos Iniciais do Ensino Fundamental"
 [39] "Razão entre o número de alunos e professores na pré-escola (ta"
 [40] "Razão entre o número de alunos e professores no ensino fundame"
 [41] "Adequação idade/ano no Ensino Fundamental (taxa)"
 [42] "Analfabetismo na população com 15 anos ou mais (%)"
 [43] "Centros culturais, casas e espaços de cultura (100 mil habitante"
 [44] "Crianças e jovens de 4 a 17 anos na escola (%)"
 [45] "Mulheres jovens de 15 a 24 anos de idade que não estudam nem t"
 [46] "Presença de vereadoras na Câmara Municipal (%)"
 [47] "Desigualdade de salário por sexo (salário de mulheres / salário"
 [48] "Diferença percentual entre jovens mulheres e homens que não estu"
 [49] "Taxa de feminicídio (100 mil mulheres)"
 [50] "Doenças relacionadas ao saneamento ambiental inadequado (100 mi"
 [51] "Perda de água (IN)"
 [52] "População atendida com serviço de água (%)"
 [53] "População atendida com esgotamento sanitário (%)"
 [54] "Índice de tratamento de esgoto (%)"
 [55] "Domicílios com acesso à energia elétrica (%)"
 [56] "Vulnerabilidade Energética"
 [57] "População ocupada entre 10 e 17 anos (%)"
 [58] "PIB per capita (R$ per capita)"
 [59] "Desemprego (taxa)"
 [60] "Desemprego de jovens (taxa)"
 [61] "Jovens de 15 a 24 anos de idade que não estudam nem trabalham"
 [62] "Ocupação das pessoas com 16 anos de idade ou mais (taxa)"
 [63] "Investimento público em infraestrutura por habitante (R$ per capit"
 [64] "Participação dos empregos em atividades intensivas em conhecimen"
 [65] "Renda municipal apropriada pelos 20% mais pobres (%)"
 [66] "Coeficiente de Gini (IN)"
 [67] "Razão mortalidade infantil (negros/não negros)"
 [68] "Razão Gravidez na Adolescência (negros/não negros)"
 [69] "Taxa de distorção idade-série nos anos iniciais do Ensino Fundame"
 [70] "Risco relativo de homicídios (negros/não negros)"
 [71] "Violência contra a população LGBTQI+ (100 mil habitantes)"
 [72] "Acesso a equipamentos da atenção básica à saúde"
 [73] "Razão do rendimento médio real (negros/não negros)"
 [74] "Taxa de distorção idade-série nos anos finais do Ensino Fundament"
 [75] "Percentual da população de baixa renda com tempo de deslocamento a"
 [76] "Mortes no trânsito (100 mil habitantes)"
 [77] "População residente em aglomerados subnormais (%)"
 [78] "Domicílios em favelas (%)"
 [79] "Equipamentos esportivos (100 mil habitantes)"
 [80] "Percentual da população negra em assentamentos subnormais (%)"
 [81] "Resíduos domiciliares per capita (Ton / Hab / Ano)"
 [82] "Recuperação de resíduos sólidos urbanos coletados seletivamente"
 [83] "População atendida com coleta seletiva (%)"
 [84] "Emissões de CO²e per capita"
 [85] "Concentração de focos de calor"
 [86] "Proporção de estratégias para gestão de riscos e prevenção a desas"
 [87] "Percentual do município desflorestado (%)"
 [88] "Esgoto tratado antes de chegar ao mar, rios e córregos (%)"
 [89] "Taxa de áreas florestadas e naturais"
 [90] "Unidades de conservação de proteção integral e uso sustentável"
 [91] "Grau de maturidade dos instrumentos de financiamento da proteção a"
 [92] "Homicídio juvenil (100 mil habitantes)"
 [93] "Mortes por agressão  (100 mil habitantes)"
 [94] "Mortes por armas de fogo (100 mil habitantes)"
 [95] "Taxa de homicídio (100 mil habitantes)"
 [96] "Grau de estruturação da política de controle interno e combate à corr"
 [97] "Grau de estruturação das políticas de participação e promoção de d"
 [98] "Grau de estruturação das políticas de transparência"
 [99] "Investimento público (R$ per capita)"
[100] "Total de receitas arrecadadas (%)"
```

Temos uma centena de indicadores para explorar!

Vamos criar um histograma para visualizar a distribuição de um indicador específico, por exemplo, "Coeficiente de Gini":

```R
dados |>
  dplyr::filter(indicator_name == "Coeficiente de Gini (IN)") |>
  ggplot(aes(x = indicator_value)) +
  geom_histogram(binwidth = 0.01, fill = "blue", color = "black", alpha = 0.7) +
  labs(title = "Distribuição do Coeficiente de Gini",
       x = "Coeficiente de Gini",
       y = "Frequência") +
  theme_minimal()
```

![Histograma do Coeficiente de Gini](https://images2.imgbox.com/1f/bd/n1PRigzI_o.png)

## Dicas para Análise Avançada

- **Comparações Regionais:** Utilize os dados para comparar municípios de diferentes estados ou regiões, identificando padrões e disparidades.
- **Séries Temporais:** Analise a evolução dos indicadores ao longo dos anos para identificar tendências e avaliar o impacto de políticas públicas.
- **Clusterização:** Agrupe municípios com características semelhantes usando técnicas de machine learning, como k-means, para identificar perfis e necessidades comuns.
- **Mapas Temáticos:** Utilize pacotes como `sf` e `leaflet` para criar mapas interativos que mostram a distribuição espacial dos indicadores.

## Inspiração: Oportunidades de Pesquisa e Impacto

O IDSCBR abre portas para pesquisas inovadoras em áreas como justiça social, saúde coletiva, educação inclusiva, sustentabilidade ambiental e governança. Ao explorar e compartilhar esses dados, você contribui para o desenvolvimento de políticas públicas mais eficazes e para a construção de cidades mais justas e sustentáveis.
