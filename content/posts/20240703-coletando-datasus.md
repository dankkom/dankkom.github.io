---
title: "Coletando os arquivos de microdados do DATASUS"
date: 2024-07-03T22:00:00-03:00
author: Komesu, D. K.
slug: coletando-datasus
tags: [Python, Brazil, DATASUS, Population, Data]
description: "Neste texto apresento o datasus-fetcher, um CLI para baixar microdados do DATASUS e deixá-los de forma organizada no seu sistema de arquivos."
cover:
  image: https://images2.imgbox.com/42/9f/yxfHgXu1_o.jpg
  alt: "Imagem de gatos doutores usando computadores"
  caption: "Imagem de gatos doutores usando computadores. Fonte: Google Gemini."
ShowToc: true
TocOpen: true
---

O Departamento de Informática do SUS (DATASUS) disponibiliza os microdados do sistema de saúde pública do Brasil em um servidor FTP.

Porém, quem ainda utiliza FTP? 🧓

Os navegadores já deram [cabo do suporte ao protocolo][1] [há algum tempo][2], principalmente por preocupações com segurança e pouquíssimo uso.

No entanto, ainda há empresas e instituições públicas que disponibilizam arquivos unicamente por esse protocolo da idade das pedras da tecnologia da informação. Uma dessas instituições é o DATASUS.

Se você acha que baixar arquivos de um servidor FTP se tornou confuso com o abandono do suporte a esse protocolo pelos navegadores, não sabe como é a organização dos arquivos de microdados do DATASUS.

Existem várias bases de dados no DATASUS. Os arquivos dessas bases são particionadas por data de referência e algumas também são particionadas por unidade da federação. Assim, muitas vezes é necessário fazer o download de dezenas, ou até milhares, de arquivos para se obter os dados necessários para um trabalho.

O pior é que cada base segue uma convenção de nomeação de arquivo diferente. Bem… Existem certos padrões nas convenções de nomeação de arquivo, mas nem todas as bases seguem um mesmo padrão, infelizmente 😞.

Baixar as bases do DATASUS pode ser é uma tarefa tediosa.

Por isso criei o datasus-fetcher, um pacote Python, e uma ferramenta de linha de comando, para baixar os arquivos de microdados do DATASUS sem muito esforço e deixá-los de forma organizada no seu sistema de arquivos.

## O datasus-fetcher

O datasus-fetcher usa uma _file naming convention_ para facilitar a busca dos dados necessários tanto por humanos quanto por outros sistemas automatizados (como scripts em Python e R). A _file naming convention_ do datasus-fetcher é bem simples, consistindo de três partes:

1. abreviação da base de dados (dataset)
2. partição, se houver
3. data da última modificação no servidor FTP do DATASUS

Essas três partes são separadas por sublinhado (_), também conhecido como underscore ou underline. Assim, o arquivo `sih-rd_2020-sp_20210102.dbc` é um arquivo da base de dados SIH-RD, particionado por estado (SP) e data de referência 2020, e foi modificado pela última vez em 2 de janeiro de 2021.

## Instalando o datasus-fetcher

O [datasus-fetcher está no Python Package Index (PyPI)](https://pypi.org/project/datasus-fetcher/) e pode ser instalado facilmente com o comando pip:

```sh
pip install datasus-fetcher
```

Ou também pode ser instalado pelo pipx, se você quiser ter o datasus-fetcher como um comando global no terminal:

```sh
pipx install datasus-fetcher
```

Ou ainda, se você quiser instalar o datasus-fetcher a partir do código-fonte, você pode clonar o repositório no GitHub e instalar o pacote com o comando pip:

```sh
git clone https://github.com/viridisdata/datasus-fetcher.git
cd datasus-fetcher
pip install .
```

## Listando as bases de dados

Para listar as bases de dados disponíveis no servidor FTP do DATASUS, use o comando `list-datasets`, que tem a seguinte sintaxe:

```sh
usage: datasus-fetcher list-datasets [-h] [datasets ...]

positional arguments:
  datasets    Datasets to list

options:
  -h, --help  show this help message and exit
```

A saída desse comando é uma lista de abreviações das bases de dados disponíveis no servidor FTP do DATASUS, o número de arquivos disponíveis, o tamanho total dos arquivos e o período de referência dos arquivos.

```
-----------Dataset----------|---Nº files---|--Total size--|------Period range------
base-populacional-ibge-pop  |     33 files |     150.4 MB | from 1980    to 2012
base-populacional-ibge-popt |     29 files |       2.3 MB | from 1992    to 2021
base-territorial-conversao  |     28 files |       2.1 MB | from 1992    to 2021
base-territorial-mapas      |     83 files |     124.4 MB | from 1991    to 2013
cih-cr                      |    868 files |     157.5 MB | from 2008-01 to 2011-04
ciha                        |   4052 files |    3146.2 MB | from 2011-01 to 2024-04
cnes-dc                     |   6102 files |     112.6 MB | from 2005-08 to 2024-05
cnes-ee                     |   3201 files |       4.3 MB | from 2007-03 to 2021-07
...                         |          ... |          ... | ...
sinasc-dnex                 |      9 files |       0.5 MB | from 2014    to 2022
siscolo-cc                  |   2858 files |    2380.9 MB | from 2006-01 to 2015-10
siscolo-hc                  |   2858 files |      38.9 MB | from 2006-01 to 2015-10
sismama-cm                  |   1675 files |       4.8 MB | from 2009-01 to 2015-07
sismama-hm                  |   1674 files |       5.7 MB | from 2009-01 to 2015-07
sisprenatal-pn              |    944 files |     221.6 MB | from 2012-01 to 2014-12
Total size: 294.1 GB
Total files: 164810 files
```

## Baixando os arquivos

O datasus-fetcher pode baixar três tipos de arquivos: dados, documentação e auxiliares.

### Arquivos de dados

Os arquivos de dados são os arquivos de microdados propriamente ditos, no formato DBC. Para baixar os arquivos de dados, use o comando `data`, que tem a seguinte sintaxe:

```sh
usage: datasus-fetcher data [-h]
                            [--start START] [--end END]
                            [--regions REGIONS [REGIONS ...]]
                            --data-dir DATA_DIR
                            [-t THREADS]
                            [datasets ...]

options:
  -h, --help            show this help message and exit
  --data-dir DATA_DIR   Directory to download to
  -t THREADS, --threads THREADS
                        Number of concurrent fetchers

dataset:
  datasets              Datasets to download (eg.: sih-rd, cnes-dc, ...)
  --start START         Start period to download (eg.: 2001 OR 2001-01)
  --end END             End period to download (eg.: 2020 OR 2020-12)
  --regions REGIONS [REGIONS ...]
                        Regions to download (eg.: br, ac, am, ce, ...)
```

Para baixar dados de uma base específica, use o seguinte comando:

```sh
datasus-fetcher data sim-do --data-dir ./data
```

Esse comando baixa todos os arquivos da base SIM-DO disponíveis no servidor FTP do DATASUS.

Para baixar dados de uma base E um período específico, use o seguinte comando:

```sh
datasus-fetcher data sinan-deng --start 2010 --end 2023 --data-dir ./data
```

Esse comando baixa todos os arquivos da base SINAN-DENG disponíveis no servidor FTP do DATASUS entre 2010 e 2023.

Para baixar dados de uma base E um período específico E de uma região específica, use o seguinte comando:

```sh
datasus-fetcher data sia-pa --start 2010 --end 2023 --regions sp rj --data-dir ./data
```

Esse comando baixa todos os arquivos da base SIA-PA disponíveis no servidor FTP do DATASUS entre 2010 e 2023 e que são referentes aos estados de São Paulo e Rio de Janeiro.

A opção `--data-dir` é obrigatória e indica o diretório onde os arquivos serão salvos.

A opção `--threads` é opcional e indica o número de threads que serão usadas para baixar os arquivos. O padrão é 2.

### Arquivos de documentação e auxiliares

O comando `docs` baixa a documentação dos arquivos de microdados. A sintaxe é a seguinte:

```sh
usage: datasus-fetcher docs [-h] [--data-dir DATA_DIR] [datasets ...]

positional arguments:
  datasets             Datasets documentation to download

options:
  -h, --help           show this help message and exit
  --data-dir DATA_DIR  Directory to download to
```

O comando `aux` baixa as tabelas auxiliares. As tabelas auxiliares são tabelas que contêm informações adicionais sobre os dados de microdados, como tabelas de conversão de códigos, tabelas de referência, etc. A sintaxe é a seguinte:

```sh
usage: datasus-fetcher aux [-h] [--data-dir DATA_DIR] [datasets ...]

positional arguments:
  datasets             Datasets auxiliary tables to download

options:
  -h, --help           show this help message and exit
  --data-dir DATA_DIR  Directory to download to
```

## Movendo arquivos antigos

Como dito anteriormente, o datasus-fetcher baixa cada nova versão de um arquivo com um nome diferente. Isso é o design da ferramenta, pois permite acumular um histórico de versões dos arquivos de dados. Por isso, quando realizamos o download de novos arquivos podemos ter várias versões antigas salvas no diretório de dados. Isso pode ser desejável para alguns. Mas para analistas e cientistas de dados, que só querem fazer suas análises e modelos com os dados mais recentes, isso é só um incômodo. Para esses usuários existe o comando `archive`, que arquiva os dados defasados, movendo-os para outro diretório no sistema de arquivos.

O comando `archive` tem a seguinte sintaxe:

```sh
usage: datasus-fetcher archive [-h] --data-dir DATA_DIR --archive-data-dir ARCHIVE_DATA_DIR

options:
  -h, --help            show this help message and exit
  --data-dir DATA_DIR
  --archive-data-dir ARCHIVE_DATA_DIR
```

## Lendo os dados

Não é escopo deste texto a leitura dos arquivos DBC do DATASUS, mas vou dar uma dica: usem o pacote {read.dbc} do R. O pacote é muito bom e lê os arquivos DBC do DATASUS sem problemas.

O pacote {read.dbc} pode ser instalado a partir do CRAN:

```r
install.packages("read.dbc")
```

E os arquivos DBC podem ser lidos com o comando `read.dbc`:

```r
library(read.dbc)
dados <- read.dbc("datasus/sinan-deng/2022/sinan-deng_2022-br_20230821.dbc")
tibble::as_tibble(head(dados))
```

A saída do comando acima é um tibble com as primeiras seis linhas do arquivo DBC lido:

```
# A tibble: 6 × 121
  TP_NOT ID_AGRAVO DT_NOTIFIC SEM_NOT NU_ANO SG_UF_NOT ID_MUNICIP ID_REGIONA ID_UNIDADE DT_SIN_PRI
  <fct>  <fct>     <date>     <fct>   <fct>  <fct>     <fct>      <fct>      <fct>      <date>
1 2      A90       2022-01-12 202202  2022   12        120020     1941       6801099    2022-01-06
2 2      A90       2022-08-11 202232  2022   12        120020     1941       5336171    2022-08-03
3 2      A90       2022-03-25 202212  2022   12        120020     1941       2002116    2022-03-21
4 2      A90       2022-03-07 202210  2022   12        120020     1941       6801099    2022-03-04
5 2      A90       2022-01-18 202203  2022   12        120020     1941       6801099    2022-01-18
6 2      A90       2022-02-21 202208  2022   12        120020     1941       6801099    2022-02-19
# ℹ 111 more variables: SEM_PRI <fct>, ANO_NASC <fct>, NU_IDADE_N <int>, CS_SEXO <fct>,
#   CS_GESTANT <fct>, CS_RACA <fct>, CS_ESCOL_N <fct>, SG_UF <fct>, ID_MN_RESI <fct>,
#   ID_RG_RESI <fct>, ID_PAIS <fct>, DT_INVEST <date>, ID_OCUPA_N <fct>, FEBRE <fct>,
#   MIALGIA <fct>, CEFALEIA <fct>, EXANTEMA <fct>, VOMITO <fct>, NAUSEA <fct>, DOR_COSTAS <fct>,
#   CONJUNTVIT <fct>, ARTRITE <fct>, ARTRALGIA <fct>, PETEQUIA_N <fct>, LEUCOPENIA <fct>,
#   LACO <fct>, DOR_RETRO <fct>, DIABETES <fct>, HEMATOLOG <fct>, HEPATOPAT <fct>, RENAL <fct>,
#   HIPERTENSA <fct>, ACIDO_PEPT <fct>, AUTO_IMUNE <fct>, DT_CHIK_S1 <date>, DT_CHIK_S2 <date>, …
# ℹ Use `colnames()` to see all variable names
```

## Conclusão

O datasus-fetcher é uma ferramenta simples e eficiente para baixar os arquivos de microdados do DATASUS. Com ele, é possível baixar os arquivos de dados, documentação e auxiliares de forma rápida e organizada. O datasus-fetcher é uma ferramenta de linha de comando, mas também pode ser usada como um pacote Python para automatizar o download dos arquivos de microdados do DATASUS.

[1]: https://developer.chrome.com/blog/deps-rems-95
[2]: https://blog.mozilla.org/security/2021/07/20/stopping-ftp-support-in-firefox-90/
