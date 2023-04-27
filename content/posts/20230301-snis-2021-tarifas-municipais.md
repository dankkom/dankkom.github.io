---
title: "Visualizando a Evolução das Tarifas Municipais do Saneamento Básico no Brasil"
date: 2023-03-01T08:00:00-03:00
author: Komesu, D. K.
slug: saneamento-basico-tarifas-municipais-snis-2021
tags: ["Saneamento Básico", "Visualização de Dados", Economia]
katex: true
---

![](https://images2.imgbox.com/ab/bd/xArPPcUW_o.gif)

Nos últimos anos, o saneamento básico tem sido um dos principais temas discutidos no Brasil. Com o objetivo de promover o acesso universal aos serviços de abastecimento de água e esgotamento sanitário, o governo brasileiro vem implementando políticas públicas para garantir o acesso à água tratada e ao tratamento de esgoto em todo o país. No entanto, apesar dos esforços, ainda existem muitos desafios a serem enfrentados nessa área.

<!--more-->

Uma das questões mais importantes em relação ao saneamento básico é o acesso à informação sobre as tarifas cobradas pelos serviços. Afinal, para entender melhor os desafios que ainda precisam ser superados e promover uma gestão mais eficiente do setor, é fundamental conhecer os valores praticados pelas concessionárias de serviços públicos.

Nesse contexto, a visualização de dados pode ser uma ferramenta valiosa. Por meio de gráficos, tabelas e mapas, é possível entender melhor a evolução das tarifas ao longo do tempo, bem como comparar os valores praticados em diferentes regiões do país. Neste artigo, vamos explorar uma visualização de dados que apresenta as tarifas médias municipais de saneamento básico no Brasil entre 1995 e 2021.

## Dados

Para este texto foram utilizados os seguintes conjuntos de dados:

- **SNIS Série Histórica - Água e Esgoto - Desagregado**: O Sistema Nacional de Informações sobre Saneamento (SNIS) é um importante instrumento de gestão para o setor de saneamento básico no Brasil. Ele é responsável por coletar, armazenar e disseminar informações sobre o acesso à água potável, esgotamento sanitário e limpeza urbana em todo o país. Os dados do SNIS, semi-processados, são disponibilizados no repositório [viridis-data/snis-rawdata](https://github.com/viridis-data/snis-rawdata), no Github, facilitando o download. A página de *releases* do repositório disponibiliza links para downloads de arquivos ZIP contendo os dados no formato *Comma Separated Values* (CSV). Neste texto será utilizado o release 2022.12.b, que contém dados de 1995 a 2021.
- **Shapefiles dos Municípios**: Para a criação de mapas coropléticos é necessário a malha da divisão administrativa dos municípios brasileiros. Felizmente o Instituto Brasileiro de Geografia e Estatística (IBGE) fornece os arquivos *shapefile* das divisões do território nacional na sua [página de downloads](https://www.ibge.gov.br/geociencias/downloads-geociencias.html). Para este texto utilizou-se a divisão territorial de 2021.
- **Índice de Preços ao Consumidor Amplo (IPCA) do IBGE**: Como serão analisados dados de preços que se estendem por um longo período de tempo (26 anos), faz-se necessário o ajuste pela inflação. O IBGE calcula o IPCA, que é o índice de inflação oficial do país. Para obter esses dados, o Sistema IBGE de Recuperação Automática (SIDRA) fornece uma API para facilitar a coleta. Os dados do IPCA estão disponíveis na [tabela 1737 do SIDRA](https://sidra.ibge.gov.br/tabela/1737). Para a coleta desses dados, utilizou-se o pacote `sidrapy`.
- **Tabela de Municípios - Diretórios Brasileiros - Base dos Dados**: Para facilitar o trabalho com dados geográficos utilizou-se essa tabela para o join entre os shapefiles do IBGE e os dados do SNIS. Fonte: [Base dos Dados](https://basedosdados.org/dataset/br-bd-diretorios-brasil?bdm_table=municipio)

## Tratamento

### Tarifa média por região

Ao longo dos tempo a fórmula de cálculo de vários indicadores do SNIS mudou. Segundo a documentação no site do SNIS, a tarifa média é calculada pelas fórmulas a seguir.

Para o ano de 1995:

$$tm = \frac{FN001}{(AG011 + ES007) \times 1000}$$

Para os anos de 1996-1997:

$$tm = \frac{FN002 + FN003}{(AG011 + ES007) \times 1000}$$

Para os anos de 1998-2006:

$$tm = \frac{FN002 + FN003 + FN007}{(AG011 + ES007) \times 1000}$$

Para os anos de 2007-2021:

$$tm = \frac{FN002 + FN003 + FN007 + FN038}{(AG011 + ES007) \times 1000}$$

Onde:

- \\(tm\\) é a tarifa média em R\$/m³;
- \\(FN001\\) é a Receita operacional direta total em R\$/ano;
- \\(FN002\\) é a Receita operacional direta de água em R\$/ano;
- \\(FN003\\) é a Receita operacional direta de esgoto em R\$/ano;
- \\(FN007\\) é a Receita operacional direta de água exportada (bruta ou tratada) em R\$/ano;
- \\(FN038\\) é a Receita operacional direta - esgoto bruto importado em R\$/ano;
- \\(AG011\\) é o Volume de água faturado em 1.000 m³/ano;
- \\(ES007\\) é o Volume de esgotos faturado em 1.000 m³/ano.

### Remoção de *outliers* pelo método do intervalo interquartil

As tarifas médias por municípios apresentam alta dispersão, por isso, para apresentar os dados num mapa, por exemplo, foram removidos valores outliers.

O método do intervalo interquartil é um método comumente usado para identificar e remover outliers em um conjunto de dados. Ele é baseado na diferença entre o primeiro e o terceiro quartis de um conjunto de dados. O primeiro quartil é o valor que divide os dados em duas partes iguais, onde 25% dos dados são menores que esse valor, enquanto o terceiro quartil é o valor que divide os dados em duas partes iguais, onde 75% dos dados são menores que esse valor.

Para aplicar o método do intervalo interquartil, primeiro precisamos calcular o primeiro e o terceiro quartis dos dados. Em seguida, calculamos a diferença entre esses dois valores, que é chamada de "amplitude interquartil" ou IQR.

O Intervalo Interquartil é definido como:

$$IQR = Q_3 - Q_1$$

Onde \\(Q_1\\) e \\(Q_3\\) são o primeiro e o terceiro quartis da distribuição. Depois, calculamos o limite inferior (\\(L_{inf}\\)) e o limite superior (\\(L_{sup}\\)), que são dados por:

$$L_{inf} = Q_1 - 1.5 \times IQR$$

$$L_{sup} = Q_3 + 1.5 \times IQR$$

Qualquer valor que esteja fora desse intervalo é considerado um outlier. Então, podemos remover esses valores do conjunto de dados e trabalhar apenas com os dados que estão dentro do intervalo. É importante observar que esses limites são apenas um guia e que, em alguns casos, eles podem não ser os mais apropriados para identificar outliers. É sempre importante analisar os dados e usar o bom senso na aplicação desse método.

### Filtro Hodrick-Prescott

Além da alta variância intra-anual, os valores de tarifa média municipal também apresentam alta volatilidade, ou seja, alta variância ao longo do tempo. Para eliminar esse ruído optou-se por suavizar as séries com o Filtro Hodrick–Prescott.

O [filtro Hodrick-Prescott (HP)](https://en.wikipedia.org/wiki/Hodrick%E2%80%93Prescott_filter) é um método utilizado para suavizar séries temporais, como séries de dados econômicos. Ele é chamado de filtro porque remove a componente cíclica de uma série temporal, deixando apenas a componente tendencial. Isso é útil quando se deseja obter uma representação mais clara da tendência subjacente em uma série temporal, ao invés de ser distraído pelos movimentos cíclicos mais curtos.

O filtro HP é implementado através de uma técnica de minimização de quadrados, onde se minimiza a soma dos quadrados dos resíduos entre a série original e a série suavizada. O parâmetro de suavização é um hiperparâmetro que controla o grau de suavização aplicado à série. Quanto maior o valor do parâmetro de suavização, mais suavizada a série ficará, mas também haverá um maior atraso na transmissão da tendência subjacente. Portanto, é importante escolher um valor adequado para o parâmetro de suavização de acordo com as necessidades específicas da análise.

A equação do filtro HP é dada por:

$$\min_{\tau}\left(\sum_{t=1}^T {(y_t - \tau_t)^2 } + \lambda \sum_{t=2}^{T-1} {[(\tau_{t+1} - \tau_t) - (\tau_t - \tau_{t-1})]^2}\right)$$

onde \\(y_t\\) é o valor da série no período \\(t\\), \\(\tau_t\\) é o valor da série suavizada no período \\(t\\), e \\(\lambda\\) é o parâmetro de suavização.

A primeira parte da equação, \\(\sum_{t=1}^T\left(y_t - \tau_t\right)^2\\), representa a soma dos quadrados dos resíduos entre a série original e a série suavizada. A segunda parte da equação, \\(\sum_{t=2}^{T-1} {[(\tau_{t+1} - \tau_t) - (\tau_t - \tau_{t-1} )]^2 }\\), é chamada de termo de suavização e penaliza as variações das taxas de crescimento da tendência \\(\tau_t\\). O parâmetro \\(\lambda\\) controla o grau de suavização aplicado à série, sendo que quanto maior o valor de \\(\lambda\\), mais suavizada a série ficará.

O objetivo da equação do filtro HP é minimizar a soma dos quadrados dos resíduos e, ao mesmo tempo, manter a suavização da série através do termo de suavização. Isso é alcançado através da otimização dos valores de \\(a_t\\), que são os valores da série suavizada.

O filtro HP é amplamente utilizado em análises econômicas, mas também pode ser útil em outros contextos onde se deseja suavizar séries temporais para obter uma representação mais clara da tendência subjacente. Ele é uma ferramenta valiosa para a análise de séries temporais, pois permite identificar tendências e padrões subjacentes que podem ser obscurecidos por flutuações cíclicas.

Neste texto foi utilizado o parâmetro \\(\lambda=1\\). [O recomendado pela literatura](https://amzn.to/3KJGxl5) é que se utilize \\(\lambda=1/7\\) para séries com frequência anual, porém, como as séries do SNIS apresentam muita volatilidade, optou-se por um valor maior.

## Análise das Tarifas Médias de Água e Esgoto

Antes de plotar as séries temporais, é sempre bom dar uma olhada em como estão os dados fazendo uma análise exploratória.

### Boxplot das Tarifas Médias Municipais por Grande Região do Brasil (2021)

O Gráfico 1 mostra os boxplots das distribuições de tarifa média municipais por Unidade Federativa em 2021 em ordem crescente do valor mediano. A mediana mais baixa é do estado do Amazonas, seguido de Mato Grosso, Acre, Amapá, Pará e Roraima. São Paulo, sem dúvidas o estado mais representativo, aparece em sétimo lugar nesse *ranking*.

No outro extremo, o estado do Rio Grande do Sul apresenta a mediana mais alta de todas, além da maior amplitude. O estado é seguido por Santa Catarina, Goiás, Distrito Federal (este apenas com Brasília), Paraná, Alagoas e Rio de Janeiro.

Gráfico 1 - Boxplot das tarifas médias municipais por Unidade Federativa, 2021

![](https://images2.imgbox.com/0d/46/eBCA8wq1_o.png)

Fonte: Elaborado com dados do SNIS

### Mapa da Tarifa Média Municipal (2021)

O mapa no Gráfico 2 mostra as tarifas médias de água e esgoto nos municípios brasileiros em 2021. Alguns municípios, que apresentaram valores muito acima da média foram omitidos para não prejudicar a visualização.

Gráfico 2 - Mapa das Tarifas Médias Municipais, 2021

![](https://images2.imgbox.com/d9/36/0EchmLuX_o.png)

Fonte: Elaborado com dados do SNIS

Observa-se que é possível distinguir a fronteira de alguns estados apenas pelo contraste das cores. Notadamente, essa distinção é melhor observada para os estados de São Paulo e Rio Grande do Sul.

Por exemplo, São Paulo têm os municípios as tarífas médias municipais baixas em comparação aos estados vizinhos, o que faz com que o contraste destaque claramente a divisão territorial paulista.

O estado do Rio Grande do Sul, por outro lado, por ter os municípios com tarifas médias mais altas do Brasil, é claramente distinguível no mapa.

Essa diferença de tarifas médias entre municípios vizinhos, porém de estados diferentes, pode ser atribuída ao modo como os governos estaduais regulam o setor de saneamento básico, o que interfere diretamente nas tarifas.

### Tendências das Tarifas Médias Municipais (2002-2021)

A seguir são apresentados os gráficos para as séries temporais das tarifas médias municipais de água e esgoto, de 2002 a 2021. Optou-se não apresentar os dados antes de 2002 por esse período apresentar muita variação e outliers, prejudicando a visualização dos dados.

Gráfico 3 - Tendências das Tarifas Médias Municipais, 2002-2021, Região Norte, deflacionado

![](https://images2.imgbox.com/3f/71/VVtySHUj_o.png)

Fonte: Elaborado com dados do SNIS

A região Norte apresenta três grupos de séries temporias que divergiram ao longo dos anos.

Gráfico 4 - Tendências das Tarifas Médias Municipais, 2002-2021, Região Nordeste, deflacionado

![](https://images2.imgbox.com/54/36/es5Xb2vy_o.png)

Fonte: Elaborado com dados do SNIS

As tarifas médias dos municípios da região Nordeste são as que mais "andam juntas" de todas as regiões. Olhando somente para esses dados é possível dizer que os prestadores da região têm uma estrutura de saneamento básico bastante similar entre si.

Gráfico 5 - Tendências das Tarifas Médias Municipais, 2002-2021, Região Centro-Oeste, deflacionado

![](https://images2.imgbox.com/a7/24/9pddVjSP_o.png)

Fonte: Elaborado com dados do SNIS

O Centro-Oeste tem apenas um grupo de séries temporais que andam juntas.

Gráfico 6 - Tendências das Tarifas Médias Municipais, 2002-2021, Região Sudeste, deflacionado

![](https://images2.imgbox.com/c9/76/e5lZg7Hu_o.png)

Fonte: Elaborado com dados do SNIS

As tarifas municipais na região Sudeste apresentam dois grupos de séries temporais que "andam juntas".

Gráfico 7 - Tendências das Tarifas Médias Municipais, 2002-2021, Região Sul, deflacionado

![](https://images2.imgbox.com/72/21/VlJBLhut_o.png)

Fonte: Elaborado com dados do SNIS

As tarifas municipais da região Sul apresentam grande dispersão, com três grupos de séries temporais observáveis, coincidindo com o número de estados. Os municípios do Rio Grande do Sul apresentam as tarifas mais caras.

## Conclusão

Os dados do **SNIS - Série Histórica** são uma importante fonte de informação para o desenho de políticas públicas baseadas em evidências. Apesar da qualidade desses dados, o fato de existir e estar em acesso público é importante para que os gestores públicos e pesquisadores que querem avaliar a qualidade dos serviços de saneamento básico no país.

O Brasil ainda enfrenta desafios significativos no que diz respeito ao saneamento básico universal. De acordo com os dados do SNIS, cerca de 93,86 milhões de pessoas no país ainda não têm acesso a serviços de esgoto tratado, o que representa cerca de 44,18% da população. Além disso, cerca de 33,2 milhões de pessoas, ou 15,8% da população, ainda não têm acesso a água potável. Essa falta de acesso a serviços de saneamento básico adequados tem impactos negativos na saúde das pessoas, na qualidade de vida e no meio ambiente. Portanto, é crucial que o Brasil avance na agenda do saneamento básico universal, para garantir que todos tenham acesso a serviços de água e esgoto de qualidade. Isso pode ser alcançado através de investimentos em infraestrutura, políticas públicas eficazes e parcerias com a iniciativa privada.

A análise exploratória mostrou que os municípios do estado de São Paulo têm tarifas médias mais baixas do que seus vizinhos de outros estados. Por outro lado, os municípios do Rio Grande do Sul têm as tarifas médias mais altas do Brasil.

Os contrastes observados no mapa, que coincidem com a divisão dos estados brasileiros, indicam que o modo como o governo de cada estado atua sobre o setor de saneamento básico tem grande importância na definição das tarifas.

Os gráficos das tendências das tarifas municipais mostram que existem municípios que seguem um tendência em comum, possivelmente refletindo fatores ambientais ou regulatórios da região.

---

[Repositório git no GitHub com os notebooks dessa análise](https://github.com/dankkom/snis-analysis-2021)
