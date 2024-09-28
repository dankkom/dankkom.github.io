---
title: "Coletando e Tratando os Dados Climáticos do INMET-BDMEP"
date: 2024-09-28T19:00:00-03:00
author: Komesu, D. K.
slug: coleta-tratamento-inmet-bdmep
tags: [
    Python,
    INMET-BDMEP,
    "Dados Climáticos",
    Data
]
description: "Neste texto explico como coletar e tratar os dados meteorológicos do INMET-BDMEP."
cover:
  image: https://images2.imgbox.com/7b/72/TiwgwbbH_o.jpg
  alt: "Temperatura horária e média diária em São Paulo em 2023"
ShowToc: true
TocOpen: true
draft: true
---

Os dados climáticos desempenham um papel crucial em diversos setores, auxiliando em estudos e previsões que impactam áreas como agricultura, planejamento urbano, e gestão de recursos naturais.

O Instituto Nacional de Meteorologia (INMET) oferece, mensalmente, o Banco de Dados Meteorológicos (BDMEP) em seu site. Este banco de dados contém uma série histórica de informações climáticas coletadas por centenas de estações de medição distribuídas por todo o Brasil. No BDMEP, você encontrará dados detalhados sobre pluviometria, temperatura, umidade do ar e velocidade do vento.

Com atualizações horárias, esses dados são bastante volumosos, proporcionando uma base rica para análises detalhadas e tomadas de decisão informadas.

Neste post vou mostrar como coletar e tratar os dados climáticos do INMET-BDMEP. Vamos coletar os arquivos de dados brutos disponíveis no [site do INMET](https://portal.inmet.gov.br/dadoshistoricos) e depois vamos tratar esses dados para facilitar a análise.

## 1. Pacotes Python necessários

Para alcançar os objetivos mencionados será preciso ter instalado apenas três pacotes:

- **httpx** para fazer as requisições HTTP
- **Pandas** para a leitura e tratamento dos dados
- **tqdm** para mostrar uma barra de progresso amigável no terminal enquanto o programa baixa ou lê os arquivos

Para instalar os pacotes necessários execute o seguinte comando no terminal:

```sh
pip install httpx pandas tqdm
```

Se estiver usando um ambiente virtual (`venv`) com poetry, por exemplo, use o seguinte comando:

```sh
poetry add httpx pandas tqdm
```

## 2. Coleta dos arquivos

### 2.1 Padrão da URL dos arquivos

O endereço dos arquivos de dados do BDMEP seguem um padrão bem simples. O padrão é o seguinte:

	https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip

A única parte que muda é o nome do arquivo que é, simplesmente, o ano de referência dos dados. Mensalmente, o arquivo para o ano mais recente (corrente) é substituído com dados atualizados.

Assim fica fácil criar um código para coletar automaticamente os arquivos de dados de todos os anos disponíveis.

Aliás, a série histórica disponível começa no ano 2000.

### 2.2 Estratégia de coleta

Para a coleta dos arquivos de dados do INMET-BDMEP vamos usar a biblioteca `httpx` para fazer as requisições HTTP e a biblioteca `tqdm` para mostrar uma barra de progresso amigável no terminal.

Primeiro, vamos importar os pacotes necessários:

```python
import datetime as dt
from pathlib import Path

import httpx
from tqdm import tqdm
```

Já identificamos o padrão da URL dos arquivos de dados do INMET-BDMEP. Agora vamos criar uma função que aceita um ano como argumento e devolve a URL do arquivo referente a esse ano.

```python
def build_url(year):
    return f"https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip"
```

Para checar se o arquivo da URL foi atualizado podemos utilizar a informação presente no cabeçalho retornado por uma requisição HTTP. Em servidores bem configurados, podemos pedir apenas esse cabeçalho com o método HEAD. Nesse o servidor foi bem configurado e podemos usar desse método.

A resposta à requisição HEAD terá o seguinte formato:

    Mon, 01 Sep 2024 00:01:00 GMT

Para parsear essa data/hora fiz a seguinte função em Python, que aceita uma _string_ e devolve um objeto `datetime`:

```python
def parse_last_modified(last_modified: str) -> dt.datetime:
    return dt.datetime.strptime(
    	last_modified,
    	"%a, %d %b %Y %H:%M:%S %Z"
    )
```

Assim, podemos usar a data/hora da última modificação para incluir no nome do arquivo que vamos baixar, usando interpolação de strings (f-strings):

```python
def build_local_filename(year: int, last_modified: dt.datetime) -> str:
    return f"inmet-bdmep_{year}_{last_modified:%Y%m%d}.zip"
```

Dessa forma, é possível verificar facilmente se o arquivo com os dados mais recentes já existe no nosso sistema de arquivos local. Se o arquivo já existir, o programa pode ser encerrado; caso contrário, devemos prosseguir com a coleta do arquivo, fazendo a requisição ao servidor.

A função `download_year` abaixo faz o download do arquivo referente a um ano específico. Se o arquivo já existe no diretório de destino, a função simplesmente retorna sem fazer nada.

Note como usamos o `tqdm` para mostrar uma barra de progresso amigável no terminal enquanto o arquivo é baixado.

```python
def download_year(
    year: int,
    destdirpath: Path,
    blocksize: int = 2048,
) -> None:

    if not destdirpath.exists():
        destdirpath.mkdir(parents=True)

    url = build_url(year)

    headers = httpx.head(url).headers
    last_modified = parse_last_modified(headers["Last-Modified"])
    file_size = int(headers.get("Content-Length", 0))

    destfilename = build_local_filename(year, last_modified)
    destfilepath = destdirpath / destfilename
    if destfilepath.exists():
        return

    with httpx.stream("GET", url) as r:
        pb = tqdm(
            desc=f"{year}",
            dynamic_ncols=True,
            leave=True,
            total=file_size,
            unit="iB",
            unit_scale=True,
        )
        with open(destfilepath, "wb") as f:
            for data in r.iter_bytes(blocksize):
                f.write(data)
                pb.update(len(data))
        pb.close()
```

### 2.3 Coleta dos arquivos

Agora que temos todas as funções necessárias, podemos fazer a coleta dos arquivos de dados do INMET-BDMEP.

Usando um loop `for` podemos baixar os arquivos de todos os anos disponíveis. O código a seguir faz exatamente isso. Começando do ano 2000 até o ano corrente.

```python
destdirpath = Path("data")
for year in range(2000, dt.datetime.now().year + 1):
    download_year(year, destdirpath)
```

## 3. Leitura e tratamento dos dados

Com os arquivos de dados brutos do INMET-BDMEP baixados, agora podemos fazer a leitura e o tratamento dos dados.

Vamos importar os pacotes necessários:

```python
import csv
import datetime as dt
import io
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm
```

### 3.1 Estrutura dos arquivos

Dentro do arquivo ZIP disponibilizado pelo INMET encontramos diversos arquivos CSV, um para cada estação meteorológica.

Porém, nas primeiras linhas desses arquivos CSV encontramos informações sobre a estação, como a região, a unidade federativa, o nome da estação, o código WMO, as coordenadas geográficas (latitude e longitude), a altitude e a data de fundação. Vamos extrair essas informações para usar como metadados.

### 3.2 Leitura dos dados com pandas

A leitura dos arquivos será feita em duas partes: [primeiro, será feita a leitura dos metadados das estações meteorológicas](#321-metadados); [depois, será feita a leitura dos dados históricos propriamente ditos](#322-dados-históricos).

#### 3.2.1 Metadados

Para extrair os metadados nas primeiras 8 linhas do arquivo CSV vamos usar o pacote embutido `csv` do Python.

Para entender a função a seguir é necessário ter um conhecimento um pouco mais avançado de como funciona handlers de arquivos (`open`), iteradores (`next`) e expressões regulares (`re.match`).

```python
def read_metadata(filepath: Path | zipfile.ZipExtFile) -> dict[str, str]:
    if isinstance(filepath, zipfile.ZipExtFile):
        f = io.TextIOWrapper(filepath, encoding="latin-1")
    else:
        f = open(filepath, "r", encoding="latin-1")
    reader = csv.reader(f, delimiter=";")
    _, regiao = next(reader)
    _, uf = next(reader)
    _, estacao = next(reader)
    _, codigo_wmo = next(reader)
    _, latitude = next(reader)
    try:
        latitude = float(latitude.replace(",", "."))
    except:
        latitude = np.nan
    _, longitude = next(reader)
    try:
        longitude = float(longitude.replace(",", "."))
    except:
        longitude = np.nan
    _, altitude = next(reader)
    try:
        altitude = float(altitude.replace(",", "."))
    except:
        altitude = np.nan
    _, data_fundacao = next(reader)
    if re.match("[0-9]{4}-[0-9]{2}-[0-9]{2}", data_fundacao):
        data_fundacao = dt.datetime.strptime(
            data_fundacao,
            "%Y-%m-%d",
        )
    elif re.match("[0-9]{2}/[0-9]{2}/[0-9]{2}", data_fundacao):
        data_fundacao = dt.datetime.strptime(
            data_fundacao,
            "%d/%m/%y",
        )
    f.close()
    return {
        "regiao": regiao,
        "uf": uf,
        "estacao": estacao,
        "codigo_wmo": codigo_wmo,
        "latitude": latitude,
        "longitude": longitude,
        "altitude": altitude,
        "data_fundacao": data_fundacao,
    }
```

Em resumo, a função `read_metadata` definida acima lê as primeiras oito linhas do arquivo, processa os dados e retorna um dicionário com as informações extraídas.

#### 3.2.2 Dados históricos

Aqui, finalmente, veremos como fazer a leitura do arquivo CSV. Na verdade é bastante simples. Basta usar a função `read_csv` do Pandas com os argumentos certos.

A seguir está exposto a chamada da função com os argumentos que eu determinei para a correta leitura do arquivo.

```python
pd.read_csv(
    "arquivo.csv",
    sep=";",
    decimal=",",
    na_values="-9999",
    encoding="latin-1",
    skiprows=8,
    usecols=range(19),
)
```

Primeiro é preciso dizer que o caractere separador das colunas é o ponto-e-vírgula (;), o separador de número decimal é a vírgula (,) e o encoding é `latin-1`, muito comum no Brasil.

Também é preciso dizer para pular as 8 primeiras linhas do arquivo (`skiprows=8`), que contém os metadados da estação), e usar apenas as 19 primeiras colunas (`usecols=range(19)`).

Por fim, vamos considerar o valor -9999 como sendo nulo (`na_values="-9999"`).

### 3.3 Tratamento dos dados

Os nomes das colunas dos arquivos CSV do INMET-BDMEP são bem descritivos, mas um pouco longos. E os nomes não são consistentes entre os arquivos e ao longo do tempo. Vamos renomear as colunas para padronizar os nomes e facilitar a manipulação dos dados.

A seguinte função será usada para renomear as colunas usando expressões regulares (RegEx):

```python
def columns_renamer(name: str) -> str:
    name = name.lower()
    if re.match(r"data", name):
        return "data"
    if re.match(r"hora", name):
        return "hora"
    if re.match(r"precipita[çc][ãa]o", name):
        return "precipitacao"
    if re.match(r"press[ãa]o atmosf[ée]rica ao n[íi]vel", name):
        return "pressao_atmosferica"
    if re.match(r"press[ãa]o atmosf[ée]rica m[áa]x", name):
        return "pressao_atmosferica_maxima"
    if re.match(r"press[ãa]o atmosf[ée]rica m[íi]n", name):
        return "pressao_atmosferica_minima"
    if re.match(r"radia[çc][ãa]o", name):
        return "radiacao"
    if re.match(r"temperatura do ar", name):
        return "temperatura_ar"
    if re.match(r"temperatura do ponto de orvalho", name):
        return "temperatura_orvalho"
    if re.match(r"temperatura m[áa]x", name):
        return "temperatura_maxima"
    if re.match(r"temperatura m[íi]n", name):
        return "temperatura_minima"
    if re.match(r"temperatura orvalho m[áa]x", name):
        return "temperatura_orvalho_maxima"
    if re.match(r"temperatura orvalho m[íi]n", name):
        return "temperatura_orvalho_minima"
    if re.match(r"umidade rel\. m[áa]x", name):
        return "umidade_relativa_maxima"
    if re.match(r"umidade rel\. m[íi]n", name):
        return "umidade_relativa_minima"
    if re.match(r"umidade relativa do ar", name):
        return "umidade_relativa"
    if re.match(r"vento, dire[çc][ãa]o", name):
        return "vento_direcao"
    if re.match(r"vento, rajada", name):
        return "vento_rajada"
    if re.match(r"vento, velocidade", name):
        return "vento_velocidade"
```

Agora que temos os nomes das colunas padronizados, vamos tratar a data/hora. Os arquivos CSV do INMET-BDMEP têm duas colunas separadas para data e hora. Isso é inconveniente, pois é mais prático ter uma única coluna de data/hora. Além disso existem inconsistências nos horários, que às vezes têm minutos e às vezes não.

As três funções a seguir serão usadas para criar uma única coluna de data/hora:

```python
def convert_dates(dates: pd.Series) -> pd.DataFrame:
    dates = dates.str.replace("/", "-")
    return dates


def convert_hours(hours: pd.Series) -> pd.DataFrame:

    def fix_hour_string(hour: str) -> str:
        if re.match(r"^\d{2}\:\d{2}$", hour):
            return hour
        else:
            return hour[:2] + ":00"

    hours = hours.apply(fix_hour_string)
    return hours


def fix_data_hora(d: pd.DataFrame) -> pd.DataFrame:
    d = d.assign(
        data_hora=pd.to_datetime(
            convert_dates(d["data"]) + " " + convert_hours(d["hora"]),
            format="%Y-%m-%d %H:%M",
        ),
    )
    d = d.drop(columns=["data", "hora"])
    return d
```

Existe um problema com os dados do INMET-BDMEP que é a presença de linhas vazias. Vamos remover essas linhas vazias para evitar problemas futuros. O código a seguir faz isso:

```python
# Remove empty rows
empty_columns = [
    "precipitacao",
    "pressao_atmosferica",
    "pressao_atmosferica_maxima",
    "pressao_atmosferica_minima",
    "radiacao",
    "temperatura_ar",
    "temperatura_orvalho",
    "temperatura_maxima",
    "temperatura_minima",
    "temperatura_orvalho_maxima",
    "temperatura_orvalho_minima",
    "umidade_relativa_maxima",
    "umidade_relativa_minima",
    "umidade_relativa",
    "vento_direcao",
    "vento_rajada",
    "vento_velocidade",
]
empty_rows = data[empty_columns].isnull().all(axis=1)
data = data.loc[~empty_rows]
```

Problema resolvido! (•̀ᴗ•́)و ̑̑

### 3.4 Encapsulando em funções

Para finalizar esta seção vamos encapsular o código de leitura e tratamento em funções.

Primeiro uma função para a leitura do arquivo CSV contino no arquivo comprimido.

```python
def read_data(filepath: Path) -> pd.DataFrame:
    d = pd.read_csv(
        filepath,
        sep=";",
        decimal=",",
        na_values="-9999",
        encoding="latin-1",
        skiprows=8,
        usecols=range(19),
    )
    d = d.rename(columns=columns_renamer)

    # Remove empty rows
    empty_columns = [
        "precipitacao",
        "pressao_atmosferica",
        "pressao_atmosferica_maxima",
        "pressao_atmosferica_minima",
        "radiacao",
        "temperatura_ar",
        "temperatura_orvalho",
        "temperatura_maxima",
        "temperatura_minima",
        "temperatura_orvalho_maxima",
        "temperatura_orvalho_minima",
        "umidade_relativa_maxima",
        "umidade_relativa_minima",
        "umidade_relativa",
        "vento_direcao",
        "vento_rajada",
        "vento_velocidade",
    ]
    empty_rows = d[empty_columns].isnull().all(axis=1)
    d = d.loc[~empty_rows]

    d = fix_data_hora(d)

    return d
```

Tem um problema com a função acima. Ela não lida com arquivos ZIP.

Criamos, então, a função `read_zipfile` para a leitura de todos os arquivos contidos no arquivo ZIP. Essa função itera sobre todos os arquivos CSV no arquivo zipado, faz a leitura usando a função `read_data` e os metadados usando a função `read_metadata`, e depois junta os dados e os metadados em um único DataFrame.

```python
def read_zipfile(filepath: Path) -> pd.DataFrame:
    data = pd.DataFrame()
    with zipfile.ZipFile(filepath) as z:
        files = [zf for zf in z.infolist() if not zf.is_dir()]
        for zf in tqdm(files):
            d = read_data(z.open(zf.filename))
            meta = read_metadata(z.open(zf.filename))
            d = d.assign(**meta)
            data = pd.concat((data, d), ignore_index=True)
    return data
```

No final, basta usar essa última função definida (`read_zipfile`) para fazer a leitura dos arquivos ZIP baixados do site do INMET. (. ❛ ᴗ ❛.)

```python
df = reader.read_zipfile("inmet-bdmep_2023_20240102.zip")
# 100%|████████████████████████████████████████████████████████████████████████████████| 567/567 [01:46<00:00,  5.32it/s]
df
#         precipitacao  pressao_atmosferica  pressao_atmosferica_maxima  ...  longitude  altitude  data_fundacao
# 0                0.0                887.7                       887.7  ... -47.925833   1160.96     2000-05-07
# 1                0.0                888.1                       888.1  ... -47.925833   1160.96     2000-05-07
# 2                0.0                887.8                       888.1  ... -47.925833   1160.96     2000-05-07
# 3                0.0                887.8                       887.9  ... -47.925833   1160.96     2000-05-07
# 4                0.0                887.6                       887.9  ... -47.925833   1160.96     2000-05-07
# ...              ...                  ...                         ...  ...        ...       ...            ...
# 342078           0.0                902.6                       903.0  ... -51.215833    963.00     2019-02-15
# 342079           0.0                902.2                       902.7  ... -51.215833    963.00     2019-02-15
# 342080           0.2                902.3                       902.3  ... -51.215833    963.00     2019-02-15
# 342081           0.0                903.3                       903.3  ... -51.215833    963.00     2019-02-15
# 342082           0.0                903.8                       903.8  ... -51.215833    963.00     2019-02-15

# [342083 rows x 26 columns]
df.to_csv("inmet-bdmep_2023.csv", index=False)  # Salvando o DataFrame em um arquivo CSV
```

## 4. Gráfico de exemplo

Para finalizar, nada mais satisfatório do que fazer gráficos com os dados que coletamos e tratamos. ヾ(≧▽≦*)o

Nessa parte uso o R com o pacote `tidyverse` para fazer um gráfico combinando a temperatura horária e a média diária em São Paulo.

```r
library(tidyverse)

dados <- read_csv("inmet-bdmep_2023.csv")

print(names(dados))
#  [1] "precipitacao"               "pressao_atmosferica"
#  [3] "pressao_atmosferica_maxima" "pressao_atmosferica_minima"
#  [5] "radiacao"                   "temperatura_ar"
#  [7] "temperatura_orvalho"        "temperatura_maxima"
#  [9] "temperatura_minima"         "temperatura_orvalho_maxima"
# [11] "temperatura_orvalho_minima" "umidade_relativa_maxima"
# [13] "umidade_relativa_minima"    "umidade_relativa"
# [15] "vento_direcao"              "vento_rajada"
# [17] "vento_velocidade"           "data_hora"
# [19] "regiao"                     "uf"
# [21] "estacao"                    "codigo_wmo"
# [23] "latitude"                   "longitude"
# [25] "altitude"                   "data_fundacao"

print(unique(dados$regiao))
# [1] "CO" "N"  "NE" "SE" "S"

print(unique(dados$uf))
#  [1] "DF" "GO" "MS" "MT" "AC" "AM" "AP" "AL" "BA" "CE" "MA" "PB" "PE" "PI" "RN"
# [16] "SE" "PA" "RO" "RR" "TO" "ES" "MG" "RJ" "SP" "PR" "RS" "SC"

dados_sp <- dados |> filter(uf == "SP")


# Temperatura horária em São Paulo
dados_sp_h <- dados_sp |>
  group_by(data_hora) |>
  summarise(
    temperatura_ar = mean(temperatura_ar, na.rm = TRUE),
  )


# Temperatura média diária em São Paulo
dados_sp_d <- dados_sp |>
  group_by(data = floor_date(data_hora, "day")) |>
  summarise(
    temperatura_ar = mean(temperatura_ar, na.rm = TRUE),
  )


# Gráfico combinando temperatura horária e média diária em São Paulo
dados_sp_h |>
  ggplot(aes(x = data_hora, y = temperatura_ar)) +
  geom_line(
    alpha = 0.5,
    aes(
      color = "Temperatura horária"
    )
  ) +
  geom_line(
    data = dados_sp_d,
    aes(
      x = data,
      y = temperatura_ar,
      color = "Temperatura média diária"
    ),
    linewidth = 1
  ) +
  labs(
    x = "Data",
    y = "Temperatura (°C)",
    title = "Temperatura horária e média diária em São Paulo",
    color = "Variável"
  ) +
  theme_minimal() +
  theme(legend.position = "top")
ggsave("temperatura_sp.png", width = 16, height = 8, dpi = 300)
```

<figure class="size-large">
  <a href="https://imgbox.com/TiwgwbbH" target="_blank">
    <img src="https://images2.imgbox.com/7b/72/TiwgwbbH_o.jpg"/>
  </a>
  <figcaption>Temperatura horária e média diária em São Paulo em 2023</figcaption>
</figure>

## 5. Conclusão

Neste texto mostrei como coletar e tratar os dados climáticos do INMET-BDMEP. Os dados coletados são muito úteis para estudos e previsões nas mais variadas áreas. Com os dados tratados, é possível fazer análises e gráficos como o que mostrei no final.

Espero que tenha gostado do texto e que tenha sido útil para você.

Criei um pacote Python com as funções que mostrei neste texto. O pacote está disponível no meu repositório Git. Se quiser, pode baixar o pacote e usar as funções no seu próprio código.

Repositório Git: https://github.com/dankkom/inmet-bdmep-data

(～￣▽￣)～
