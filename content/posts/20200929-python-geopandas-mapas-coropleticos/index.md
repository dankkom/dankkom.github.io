---
title: "Como criar mapas coropléticos em Python com matplotlib e geopandas"
date: 2020-09-29
author: Komesu, D. K.
slug: python-geopandas-mapas-coropleticos
aliases:
    - /python-geopandas-mapas-coropleticos
    - /posts/20200929-python-geopandas-mapas-coropleticos/index.html
tags: ["Programação", "Python", "Mapas", "Visualização de Dados"]
---

Frequentemente um mapa colorido é o mais adequado para comunicar alguma informação que pode ser agregada geograficamente. Neste texto eu descrevo o passo-a-passo para criar um *mapa coroplético* básico em Python usando os pacotes **matplotlib** e o **geopandas**. Além desses dois pacotes, vou utilizar o **geobr** desenvolvido pelo IPEA para baixar dados geoespaciais do Brasil para plotar os mapas.

<!--more-->

- [mapa coroplético](https://pt.wikipedia.org/wiki/Mapa_coroplético)
- [matplotlib](https://matplotlib.org)
- [geopandas](https://geopandas.org)
- [geobr](https://github.com/ipeaGIT/geobr)

Instalando os pacotes necessários:

```sh
pip install matplotlib geopandas geobr
```

Pacotes instalados sem erros, basta importá-los no script Python.

Dica: use o [Google Colab](https://colab.research.google.com/) caso tenha problemas ao tentar instalar o geopandas.

```python
import pandas as pd
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import geob
```

Primeiro é preciso obter os dados que desejamos visualizar através de mapas.

Para este exemplo eu vou utilizar os dados de área plantada de milho por unidade da federação publicados pelo IBGE.

No código a seguir os dados são obtidos através do Sistema IBGE de Recuperação Automática (SIDRA) pela URL que contém os parâmetros para a API da consulta. Essa URL pode ser obtida através do site do SIDRA ([tabela 839](https://sidra.ibge.gov.br/tabela/839)).

### Obtendo os dados

Podemos carregar a tabela apenas passando a URL ao método [read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html) do Pandas.

A URL baixa um arquivo CSV com algumas linhas que podemos ignorar (metadados). Para isso utilizamos os argumentos `skiprows` e `skipfooter`.

```python
url = "https://sidra.ibge.gov.br/geratabela?format=us.csv&amp;name=tabela839.csv&amp;terr=NC&amp;rank=-&amp;query=t/839/n3/all/v/109/p/last%201/c81/31693/l/,v,p%2Bt%2Bc81"
d = pd.read_csv(
    url,
    skiprows=2, # Ignora as duas primeiras linhas do arquivo
    skipfooter=16, # Ignora as últimas 16 linhas do arquivo
)
d.head()
```

<table>
    <thead>
        <tr><th></th><th>ANO</th><th>CÓD.</th><th>UNIDADE DA FEDERAÇÃO</th><th>PRODUTO DAS LAVOURAS TEMPORÁRIAS</th><th>ÁREA PLANTADA (HECTARES)</th></tr>
    </thead>
    <tbody>
        <tr><th>0</th><td>2018</td><td>11</td><td>Rondônia</td><td>Total</td><td>185413</td></tr>
        <tr><th>1</th><td>2018</td><td>12</td><td>Acre</td><td>Total</td><td>30140</td></tr>
        <tr><th>2</th><td>2018</td><td>13</td><td>Amazonas</td><td>Total</td><td>3612</td></tr>
        <tr><th>3</th><td>2018</td><td>14</td><td>Roraima</td><td>Total</td><td>9155</td></tr>
        <tr><th>4</th><td>2018</td><td>15</td><td>Pará</td><td>Total</td><td>226708</td></tr>
    </tbody>
</table>

Das colunas presentes na tabela precisamos apenas de duas: o código da unidade de federação (`Cód.`) e a coluna com as áreas plantadas (`Área plantada (Hectares)`). Para fazermos o [merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html) dessa tabela com o dataframe com as geometrias obtidos com o `geobr` vamos renomear a coluna `Cód.`.

```python
# Seleciona apenas as colunas de interesse
d = d[["Cód.", "Área plantada (Hectares)"]]
# Renomeia a coluna 'Cód.' para 'code_state' para juntar com a tabela de
# geometria das UFs
d = d.rename(columns={"Cód.": "code_state"})
d.head()
```

<table>
    <thead>
        <tr><th></th><th>CODE_STATE</th><th>ÁREA PLANTADA (HECTARES)</th></tr>
    </thead>
    <tbody>
        <tr><th>0</th><td>11</td><td>185413</td></tr>
        <tr><th>1</th><td>12</td><td>30140</td></tr>
        <tr><th>2</th><td>13</td><td>3612</td></tr>
        <tr><th>3</th><td>14</td><td>9155</td></tr>
        <tr><th>4</th><td>15</td><td>226708</td></tr>
    </tbody>
</table>

### Obtendo as geometrias

O pacote `geobr` desenvolvido pelo IPEA permite baixar programaticamente dados geoespaciais do Brasil.

Para baixar os contornos dos estados brasileiros usamos o método `read_state`.

```python
# Baixa o GeoDataFrame com os estados do Brasil e DF
br_uf = geobr.read_state()
br_uf.head()
```

<table>
    <thead>
        <tr><th>CODE_STATE</th><th>ABBREV_STATE</th><th>NAME_STATE</th><th>CODE_REGION</th><th>NAME_REGION</th><th>GEOMETRY</th></tr>
    </thead>
    <tbody>
        <tr><th>0</th><td>11.0</td><td>RO</td><td>Rondônia</td><td>1.0</td><td>Norte</td><td>MULTIPOLYGON (((-63.32721 -7.97672, -62.86662 ...</td></tr>
        <tr><th>1</th><td>12.0</td><td>AC</td><td>Acre</td><td>1.0</td><td>Norte</td><td>MULTIPOLYGON (((-73.18253 -7.33550, -72.58477 ...</td></tr>
        <tr><th>2</th><td>13.0</td><td>AM</td><td>Amazonas</td><td>1.0</td><td>Norte</td><td>MULTIPOLYGON (((-67.32609 2.02971, -67.31682 2...</td></tr>
        <tr><th>3</th><td>14.0</td><td>RR</td><td>Roraima</td><td>1.0</td><td>Norte</td><td>MULTIPOLYGON (((-60.20051 5.26434, -60.19273 5...</td></tr>
        <tr><th>4</th><td>15.0</td><td>PA</td><td>Pará</td><td>1.0</td><td>Norte</td><td>MULTIPOLYGON (((-54.95431 2.58369, -54.93542 2...</td></tr>
    </tbody>
</table>

### Fazendo merge

Com o método [merge](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html) podemos juntar os dois dataframes através da coluna `code_state`. Depois selecionamos apenas as colunas necessárias.

```python
br_uf_d = br_uf.merge(d)
br_uf_d = br_uf_d[["geometry", "Área plantada (Hectares)"]]
br_uf_d.head()
```

<table>
    <thead>
        <tr><th></th><th>GEOMETRY</th><th>ÁREA PLANTADA (HECTARES)</th></tr>
    </thead>
    <tbody>
        <tr><th>0</th><td>MULTIPOLYGON (((-63.32721 -7.97672, -62.86662 ...</td><td>185413</td></tr>
        <tr><th>1</th><td>MULTIPOLYGON (((-73.18253 -7.33550, -72.58477 ...</td><td>30140</td></tr>
        <tr><th>2</th><td>MULTIPOLYGON (((-67.32609 2.02971, -67.31682 2...</td><td>3612</td></tr>
        <tr><th>3</th><td>MULTIPOLYGON (((-60.20051 5.26434, -60.19273 5...</td><td>9155</td></tr>
        <tr><th>4</th><td>MULTIPOLYGON (((-54.95431 2.58369, -54.93542 2...</td><td>226708</td></tr>
    </tbody>
</table>

### Finalmente plotando o mapa

Criar um mapa estático com `geopandas` é bastante simples. Basta dar um `plot` passando o nome da coluna que se deseja usar para colorir o mapa.

Para esse mapa eu escolhi `Greens` como as cores do mapa veja [Colormaps](https://matplotlib.org/tutorials/colors/colormaps.html) para outras cores).

```python
f, ax = plt.subplots()
f.set_size_inches(16, 16)
br_uf_d.plot(
    ax=ax, # Axis de destino do gráfico
    column="Área plantada (Hectares)", # Coluna com os valores usados para colorir o mapa
    cmap="Greens", # Mapa de cores
    edgecolor="black", # Cor dos contornos
    linewidth=0.25, # Espessura dos contornos
)
```

![](https://images2.imgbox.com/1a/44/u9mDM6J8_o.png)

Temos um mapa coroplético básico agora, mas faltam algumas coisas para estar completo. Não temos ideia dos valores que as cores representam, por isso uma escala de cores (colorbar) é imprescindível.

O código a seguir faz o mesmo mapa adicionando uma escala de cores na figura.

```python
f, ax = plt.subplots()
f.set_size_inches(16, 16)

br_uf_d.plot(
    ax=ax,                              # Axis de destino do gráfico
    column="Área plantada (Hectares)",  # Coluna com os valores usados para colorir o mapa
    cmap="Greens",                      # Mapa de cores
    edgecolor="black",                  # Cor dos contornos
    linewidth=0.25,                     # Espessura dos contornos
)

# Adiciona escala Colorbar (https://stackoverflow.com/a/36080553)
# Cria um Axis usado para fazer o Colorbar
cax = f.add_axes(
    [
        0.82,    # posicao x (entre 0.0 e 1.0)
        0.18,    # posicao y (entre 0.0 e 1.0)
        0.03,    # largura x
        0.40,    # altura y
    ]
)

sm = plt.cm.ScalarMappable(
    cmap="Greens",                                       # Usa o mesmo cmap do mapa
    norm=plt.Normalize(
        vmin=br_uf_d["Área plantada (Hectares)"].min(),  # Valor mínimo
        vmax=br_uf_d["Área plantada (Hectares)"].max(),  # Valor máximo
    ),
)
# Põe o Axis com Colorbar na mesma figura do mapa
f.colorbar(sm, cax=cax)
```

![](https://images2.imgbox.com/1e/47/WdrHOi7i_o.png)

Temos uma escala de cores, mas o formato dos valores não estão como desejados. Além disso, essas bordas com as coordenadas geográficas são desnecessárias e ficam feias para colocar numa publicação.

### Aparando as arestas e polindo

Para que o mapa fique digno de uma publicação respeitável vamos fazer alguns ajustes.

Primeiro, vamos arrumar os números da escala da barra de cores. Segundo, um gráfico deve ter um título descritivo. Terceiro, devemos colocar a fonte dos dados. E por último, vamos remover as bordas.

```python
f, ax = plt.subplots()
f.set_size_inches(16, 16)

br_uf_d.plot(
    ax=ax,                              # Axis de destino do gráfico
    column="Área plantada (Hectares)",  # Coluna com os valores usados para colorir o mapa
    cmap="Greens",                      # Mapa de cores
    edgecolor="black",                  # Cor dos contornos
    linewidth=0.25,                     # Espessura dos contornos
)

# Adiciona escala Colorbar (referência: https://stackoverflow.com/a/36080553)
# Cria um Axis usado para fazer o Colorbar
cax = f.add_axes(
    [
        0.82,    # posicao x (entre 0.0 e 1.0)
        0.18,    # posicao y (entre 0.0 e 1.0)
        0.03,    # largura x
        0.40,    # altura y
    ]
)

sm = plt.cm.ScalarMappable(
    cmap="Greens",                                       # Usa o mesmo cmap do mapa
    norm=plt.Normalize(
        vmin=br_uf_d["Área plantada (Hectares)"].min(),  # Valor mínimo
        vmax=br_uf_d["Área plantada (Hectares)"].max(),  # Valor máximo
    ),
)
# Põe o Axis com Colorbar na mesma figura do mapa
f.colorbar(
    sm,
    cax=cax,
    # Formata a escala do Colorbar
    format=ticker.FuncFormatter(lambda x, pos: f"{x/1000: >10,.0f} mil ha"),
)

# Adiciona um título ao mapa
ax.set_title(
    "Área plantada de Milho por Estado em 2018",
    fontdict={"fontsize": 20},
)

# Adiciona a fonte como nota de rodapé
f.text(
    0.15,                  # Posição x
    0.20,                  # Posição y
    "Fonte: IBGE (2020)."  # Texto
)

ax.axis("off")          # Remove os eixos
```

![](https://images2.imgbox.com/0f/81/bSVKCAMa_o.png)
