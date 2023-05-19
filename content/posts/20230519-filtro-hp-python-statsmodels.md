---
title: "Como aplicar o filtro HP em séries temporais no Python com o pacote statsmodels"
date: 2023-05-19T10:00:00-03:00
author: Komesu, D. K.
slug: filtro-hp-python-statsmodels
tags: [Python, "Filtro HP", statsmodels, Econometria, Estatística]
katex: true
---

Num texto anterior eu utilizei o Filtro Hodrick-Prescott (HP) para suavizar séries temporais das tarifas municipais de saneamento básico do Brasil. Neste texto vou explicar passo a passo como aplicar o Filtro HP em séries temporais no Python com o pacote statsmodels para analisar ciclos e tendências.

<!--more-->

## O que é o Filtro HP?

O Filtro Hodrick-Prescott (Filtro HP) é uma técnica estatística utilizada para decompor uma série temporal em duas componentes: a tendência de longo prazo e as flutuações de curto prazo. Ele recebe esse nome em homenagem a seus criadores, Robert Hodrick e Edward Prescott.

A ideia por trás do Filtro HP é encontrar uma função de tendência suavizada que minimize a variação das flutuações em relação à tendência. Isso é alcançado através de um processo de minimização de uma função objetivo que leva em consideração tanto a suavidade da tendência quanto a qualidade de ajuste das flutuações.

A equação do filtro HP é dada por:

$$\min_{\tau}\left(\sum_{t=1}^T {(y_t - \tau_t)^2 } + \lambda \sum_{t=2}^{T-1} {[(\tau_{t+1} - \tau_t) - (\tau_t - \tau_{t-1})]^2}\right)$$

onde \\(y_t\\) é o valor da série no período \\(t\\), \\(\tau_t\\) é o valor da série suavizada no período \\(t\\), e \\(\lambda\\) é o parâmetro de suavização.

A primeira parte da equação, \\(\sum_{t=1}^T\left(y_t - \tau_t\right)^2\\), representa a soma dos quadrados dos resíduos entre a série original e a série suavizada. A segunda parte da equação, \\(\sum_{t=2}^{T-1} {[(\tau_{t+1} - \tau_t) - (\tau_t - \tau_{t-1} )]^2 }\\), é chamada de termo de suavização e penaliza as variações das taxas de crescimento da tendência \\(\tau_t\\). O parâmetro \\(\lambda\\) controla o grau de suavização aplicado à série, sendo que quanto maior o valor de \\(\lambda\\), mais suavizada a série ficará.

## Onde o Filtro HP é usado

Uma vez que a série temporal é decomposta em tendência e flutuações de curto prazo, os analistas podem analisar separadamente essas componentes, entendendo melhor os padrões de longo prazo e as variações cíclicas da série. Isso pode ser útil para identificar tendências de crescimento, ciclos econômicos, pontos de virada e anomalias nos dados.

O Filtro Hodrick-Prescott é amplamente utilizado na análise econômica e financeira para separar a tendência subjacente de uma série temporal dos movimentos de curto prazo, também conhecidos como ruído ou flutuações cíclicas. Ele é particularmente aplicado em dados macroeconômicos, como o Produto Interno Bruto (PIB), taxas de desemprego, inflação, entre outros.

É importante ressaltar que o Filtro HP não é uma técnica perfeita e apresenta algumas limitações. A escolha do parâmetro de suavização pode afetar os resultados, e a interpretação das flutuações de curto prazo também requer cuidado, pois podem ser influenciadas por fatores temporários ou eventos não capturados pelo modelo.

## Como usar o filtro HP no Python

### 1. Importe os pacotes necessários

```sh
pip install matplotlib openpyxl pandas statsmodels
```

Os pacotes necessários são pandas, statsmodels, matplotlib e openpyxl.

```python
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
```

### 2. Carregue os dados

Nesse exemplo utilizo os dados da Fundação SEADE de [PIB mensal (com ajuste sazonal) do estado de São Paulo](https://repositorio.seade.gov.br/dataset/pib-mensal/resource/abf25069-ceeb-4115-8945-e0c4d0508588). Para facilitar a leitura dos dados eu coloquei os dados no formato de tabela e salvei num arquivo Excel com o nome _seade-pib-mensal-ajustado.xlsx_.

Então, para carregar os dados em um DataFrame, basta usar a função `read_excel` do pandas. Lembre-se de ter instalado o pacote `openpyxl` para ler arquivos Excel (para instalar, digite no terminal: `pip install openpyxl`)

```python
df = pd.read_excel("seade-pib-mensal-ajustado.xlsx")
print(df)
#           data  pib_mensal_aj
# 0   2002-01-01      72.388618
# 1   2002-02-01      72.776801
# 2   2002-03-01      72.374824
# 3   2002-04-01      73.518364
# 4   2002-05-01      71.596451
# ..         ...            ...
# 249 2022-10-01     114.306663
# 250 2022-11-01     113.682174
# 251 2022-12-01     112.750665
# 252 2023-01-01     112.951585
# 253 2023-02-01     113.378555

# [254 rows x 2 columns]
```

Para aplicar o método do filtro HP do pacote statsmodels é preciso que o DataFrame com a série tenha um índice de datas. Para fazer isso no pandas use o método `set_index` no DataFrame com a sua série, passando o nome da coluna com as datas da série:

```python
df = df.set_index("data")
print(df)
#             pib_mensal_aj
# data
# 2002-01-01      72.388618
# 2002-02-01      72.776801
# 2002-03-01      72.374824
# 2002-04-01      73.518364
# 2002-05-01      71.596451
# ...                   ...
# 2022-10-01     114.306663
# 2022-11-01     113.682174
# 2022-12-01     112.750665
# 2023-01-01     112.951585
# 2023-02-01     113.378555

# [254 rows x 1 columns]
```

### 3. Rode a função `hpfilter`

Para aplicar o filtro HP basta executar a função `sm.tsa.hp_filter.hpfilter`:

```python
ciclo, tendencia = sm.tsa.filters.hpfilter(df["pib_mensal_aj"], 129600)
```

Nesse caso, como a série utilizada é mensal, usou-se como parâmetro de suavização (\\(\lambda = 129600\\)), como recomendado pela literatura (<a target="_blank" href="https://amzn.to/3odsg7B">Livro MODELOS DE SÉRIES TEMPORAIS: Uma introdução com aplicações práticas</a>).

A função retorna duas séries, o ciclo e a tendência.

Vamos visualizar a série de ciclo:

```python
print(ciclo)
# data
# 2002-01-01    3.952369
# 2002-02-01    4.116649
# 2002-03-01    3.490739
# 2002-04-01    4.410253
# 2002-05-01    2.264132
#                 ...
# 2022-10-01    1.699109
# 2022-11-01    0.798916
# 2022-12-01   -0.408279
# 2023-01-01   -0.483037
# 2023-02-01   -0.331743
# Name: pib_mensal_aj_cycle, Length: 254, dtype: float64
```

E a série de tendência:

```python
print(tendencia)
# data
# 2002-01-01     68.436249
# 2002-02-01     68.660152
# 2002-03-01     68.884085
# 2002-04-01     69.108111
# 2002-05-01     69.332319
#                  ...
# 2022-10-01    112.607553
# 2022-11-01    112.883258
# 2022-12-01    113.158944
# 2023-01-01    113.434622
# 2023-02-01    113.710297
# Name: pib_mensal_aj_trend, Length: 254, dtype: float64
```

### 4. Fazendo os gráficos de ciclo e tendência

Para finalizar vamos fazer os gráficos da tendência do PIB paulista e do hiato do produto.

Mas primeiro vamos colocar as séries de ciclo e tendência obtidas pelo filtro HP no DataFrame com os dados originais.

```python
df["ciclo"] = ciclo
df["tendencia"] = tendencia
```

Agora podemos plotar o gráfico de tendência do PIB paulista:

```python
df[["tendencia", "pib_mensal_aj"]].plot()
plt.tight_layout()
plt.show()
```

![](https://images2.imgbox.com/6a/2e/RnIgT5rT_o.png)

E o gráfico de hiato do produto paulista:

```python
df[["ciclo"]].plot()
plt.axhline(y=0, color="grey")
plt.tight_layout()
plt.show()
```

![](https://images2.imgbox.com/5e/95/T8FNq2Xy_o.png)

---

## Referências:

Fundação SEADE. [PIB MENSAL](https://repositorio.seade.gov.br/dataset/pib-mensal/resource/abf25069-ceeb-4115-8945-e0c4d0508588)

KOMESU, D. K. [Visualizando a Evolução das Tarifas Municipais do Saneamento Básico no Brasil](https://dkko.me/posts/saneamento-basico-tarifas-municipais-snis-2021/)

MARGARIDO, M. A. <a target="_blank" href="https://amzn.to/3odsg7B">MODELOS DE SÉRIES TEMPORAIS: Uma introdução com aplicações práticas</a>

Seabold, S., & Perktold, J. (2010). statsmodels: Econometric and statistical modeling with python. In 9th Python in Science Conference.

statsmodels.tsa.filters.hp_filter.hpfilter https://www.statsmodels.org/dev/generated/statsmodels.tsa.filters.hp_filter.hpfilter.html
