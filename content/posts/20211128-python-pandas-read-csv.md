---
title: "Pandas read_csv: como ler um arquivo CSV no Python"
date: 2021-11-28
author: Komesu, D. K.
slug: python-pandas-read-csv
aliases:
     - /python-pandas-read-csv
     - /posts/20211128-python-pandas-read-csv/index.html
tags: ["Python", "Programação", "CSV", "Dados", "Extração de Dados"]
katex: true
---

Uma das ações mais comuns em ciência de dados com Python é carregar os dados salvos em algum arquivo CSV para um dataframe no Pandas. Neste texto explico como usar a função `read_csv` e seus principais argumentos.

<!--more-->

Primeiro deve-se importar a biblioteca Pandas:

```python
import pandas as pd
```

### Básico

O uso mais básico da função `read_csv` é passando o caminho para o arquivo que se quer importar:

```python
df = pd.read_csv("test.csv")
df
```

```
     PassengerId  Pclass                                          Name  ...      Fare  Cabin  Embarked
0            892       3                              Kelly, Mr. James  ...    7.8292    NaN         Q
1            893       3              Wilkes, Mrs. James (Ellen Needs)  ...    7.0000    NaN         S
2            894       2                     Myles, Mr. Thomas Francis  ...    9.6875    NaN         Q
3            895       3                              Wirz, Mr. Albert  ...    8.6625    NaN         S
4            896       3  Hirvonen, Mrs. Alexander (Helga E Lindqvist)  ...   12.2875    NaN         S
..           ...     ...                                           ...  ...       ...    ...       ...
413         1305       3                            Spector, Mr. Woolf  ...    8.0500    NaN         S
414         1306       1                  Oliva y Ocana, Dona. Fermina  ...  108.9000   C105         C
415         1307       3                  Saether, Mr. Simon Sivertsen  ...    7.2500    NaN         S
416         1308       3                           Ware, Mr. Frederick  ...    8.0500    NaN         S
417         1309       3                      Peter, Master. Michael J  ...   22.3583    NaN         C
[418 rows x 11 columns]
```

Simples, não?

Porém, nem todos os CSVs são iguais, pois não existe um padrão para os arquivos Comma Separated Values. Coisas como delimitador de coluna, separador decimal, agrupador de dígitos, formato de data e codificação (*encoding*) podem diferir dependendo do país, sistema e preferência pessoal.

Por isso existem argumentos na função `read_csv` para dizer a Pandas quais caracteres usar para delimitar colunas, separar inteiros da parte decimal, representar os agrupamentos de milhar e decodificar data e hora. Os três argumentos básicos para ler arquivos CSV no Pandas são o `sep`, o `decimal` e o `encoding`. Com esses três pelo menos metade dos problemas com arquivos CSV são resolvidos logo ao carregar o arquivo.

### Argumentos para arquivos CSV

**sep**: usado para dizer à função qual caractere considerar como delimitador de colunas. Os mais comuns são a vírugula "," (padrão), o ponto e vírgula ";" e a tabulação "\t", mas pode-se passar qualquer *string* para esse argumento.

**encoding**: determina qual a codificação de caracteres do arquivo. O padrão é o UTF-8, mas no Brasil normalmente se usa o LATIN-1 (formalmente [ISO-8859-1](https://pt.wikipedia.org/wiki/ISO/IEC_8859-1)). Quando usamos o `read_csv` com esse argumento incorreto vemos aqueles nomes com caracteres estranhos (�).

### Argumentos para tratar números

**decimal**: diz à função qual caractere representa o [separador decimal de um número](https://pt.wikipedia.org/wiki/Separador_decimal). O ponto é o valor padrão (por exemplo  \\(\pi = 3.14\\)), mas no Brasil usamos a vírgula (\\(\pi = 3,14\\)).

**thousands**: define qual caractere a função interpretará como agrupador de milhar, por exemplo, ponto (1.000.000) e vírgula (1,000,000).

### Argumentos para tratar linhas

**skiprows** e **skipfooter**: servem para pular linhas no início e no final do arquivo respectivamente. Útil quando o arquivo tem textos de cabeçalho e rodapé.

**skip_blank_lines**: passamos um valor booleano (True ou False) se quisermos que o Pandas ignore linhas em branco no arquivo CSV.

**nrows**: diz ao Pandas quantas linhas ler do arquivo. Útil quando o arquivo é muito grande e queremos apenas dar uma olhada no formato dos dados.

**header**: pode ser um *int* ou uma lista de *int* que diz ao Pandas quais linhas considerar como contendo os nomes das colunas.

**names**: recebe uma lista de strings com os nomes das colunas. Útil quando o CSV não tem uma linha com os nomes das colunas ou quando queremos sobreescrever os nomes das colunas. Caso for sobreescrever os nomes das colunas, passar `header=0`.

---

Esses são os argumentos básicos para a função `read_csv` do Pandas. Existem vários outros argumentos que tratam de tipos das colunas, compressão do arquivo, entre outras. Para uma lista completa visite a documentação oficial: [https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
