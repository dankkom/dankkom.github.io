---
title: "Extraindo dados de arquivos Excel"
date: 2021-04-20
author: Komesu, D. K.
slug: extraindo-dados-de-arquivos-excel
tags: []
---

É comum disponibilizar dados tabulares em arquivos CSV ou XLSX. No entanto, nem sempre esses dados vêm no melhor formato estruturado para leitura e processamento por softwares.

O IBGE, por exemplo, disponibiliza vários dados em arquivos de planilhas (.xls, .xlsx, .ods) que, em muitos casos, não é amigável à leitura por scripts. Nesses casos é preciso escrever scripts para extrair esses dados para um formato usável em análise de dados.

Neste texto eu descrevo passo a passo como extrair dados das Projeções de População do IBGE de 2018.

<!--more-->

## Instalação dos pacotes necessários

Para instalar os pacotes necessários, se ainda não os tiver, basta executar o sequinte comando:

```sh
pip install pandas xlrd
```

- pandas: manipulação de dataframes
- xlrd: ler/salvar arquivos xls

Com tudo instalado, basta importar o pandas com:

```python
import pandas as pd
```

## Download dos arquivos

Primeiro é preciso baixar os arquivos Excel no servidor FTP do IBGE. Isso pode ser feito via navegador ou pelo Python mesmo.

Os arquivos podem ser encontrados nos endereços:

- Web: [https://www.ibge.gov.br/estatisticas/sociais/populacao/9109-projecao-da-populacao.html?=&amp;amp;t=downloads](https://www.ibge.gov.br/estatisticas/sociais/populacao/9109-projecao-da-populacao.html?=&amp;t=downloads)
- FTP: ftp.ibge.gov.br/Projecao_da_Populacao/Projecao_da_Populacao_2018

O arquivo que vou usar é `projecoes_2018_indicadores.xls`

## Inspeção visual no Microsoft Excel / LibreOffice Calc

A primeira coisa que faço é abrir os arquivos no Excel / Calc para fazer uma inspeção visual em como os dados estão organizados na planilha.

Primeiro vejo como os dados estão organizados e se é possível extraí-los apenas com o Pandas. Olho coisas como:

- onde começa e termina o cabeçalho da(s) tabela(s) (argumento `headers`);
- se há linhas antes ou depois da tabela para ignorar (`skiprows` e `skipfooter`);
- se há mais de uma planilha no arquivo;

No caso do arquivo `projecoes_2018_indicadores.xls` temos várias planilhas (uma para cada região), felizmente todas com a mesma estrutura: três linhas antes da tabela, duas linhas de cabeçalho e doze linhas de rodapé.

Primeiro é vou descrever o código para extrair dados de uma planilha e então aplicar um loop para fazer o mesmo com todas as planilhas do arquivo.

Assim, a chamada para a função `read_excel` do pandas fica assim:

```python
df = pd.read_excel(
    "data/projecoes_2018_indicadores.xls",
    skiprows=3,
    skipfooter=12,
    header=(0, 1),
)
df.head()
```

![](https://images2.imgbox.com/48/57/DpoiLNaF_o.png)

Veja que é preciso tratar os nomes das colunas. Principalmente, é preciso corrigir os nomes das olunas do segundo nível (as colunas "Unnamed" 😣).

### MultiIndex

A tabela do IBGE tem um cabeçalho com nomes das colunas com dois níveis hierárquicos formatado com células mescladas. No Pandas esse tipo de coluna é representado pelo objeto `MultiIndex`.

Vou então construir um novo `MultiIndex` com uma lista de tuplas com os nomes das colunas e atribuir ao `DataFrame`.

O bloco de código a seguir itera sobre as colunas do `DataFrame`:

- substitui o caractere de nova linha ("\n") por um espaço (" ");
- se o nome da coluna no segundo nível começar com "Unnamed:", o nome dele é o mesmo do primeiro nível
- coloca a tupla ("coluna_nivel_1", "coluna_nivel_2") numa lista (`new_columns`)

```python
new_columns = []
for column in df.columns:
    column = [col.replace("\n", " ") for col in column]
    for i, col in enumerate(column):
        if col.startswith("Unnamed:"):
            column[i] = column[i-1]
    new_columns.append(tuple(column))
```

Agora que temos a lista das colunas com nomes corrigidos podemos construir o novo `MultiIndex` e atribuir ao `DataFrame`.

```python
df.columns = pd.MultiIndex.from_tuples(new_columns)
df.head()
```

![](https://images2.imgbox.com/0f/2c/B2Zt62PA_o.png)

O código para ler os dados de uma planilha está feito. Vou colocá-lo em uma função para usar no loop para ler todas as planilhas do arquivo.

```python
def ler_planilha(filepath, sheet_name):
    df = pd.read_excel(
        filepath,
        sheet_name=sheet_name,
        skiprows=3,
        skipfooter=12,
        header=(0, 1),
    )
    new_columns = []
    for col0, col1 in df.columns:
        col0 = col0.replace("\n", " ")
        col1 = col1.replace("\n", " ")
        if col1.startswith("Unnamed:"):
            new_columns.append((col0, col0))
        else:
            new_columns.append((col0, col1))
    df.columns = pd.MultiIndex.from_tuples(new_columns)
    df.loc[:, ("REGIAO", "REGIAO")] = sheet_name
    return df
```

Agora é preciso ler os dados de todas as planilhas do arquivo.

Para isso pode-se colocar o código num loop iterando sobre todas as planilhas. Para obter os nomes das planilhas a classe `ExcelFile` do pandas é bem útil.

```python
with pd.ExcelFile("data/projecoes_2018_indicadores.xls") as xls:
    sheet_names = xls.sheet_names
print(sheet_names)
```

```sh
['Brasil', 'Norte', 'RO', 'AC', 'AM', 'RR', 'PA', 'AP', 'TO', 'Nordeste', 'MA', 'PI', 'CE', 'RN', 'PB', 'PE', 'AL', 'SE', 'BA', 'Sudeste', 'MG', 'ES', 'RJ', 'SP', 'Sul', 'PR', 'SC', 'RS', 'Centro-Oeste', 'MS', 'MT', 'GO', 'DF']
```

Cada planilha contém dados de uma região do Brasil. Para identificar a região nos dados cria-se uma coluna com valores igual ao nome da planilha.

```python
data = pd.DataFrame()
for sheet_name in sheet_names:
    df = ler_planilha("data/projecoes_2018_indicadores.xls", sheet_name)
    data = pd.concat((data, df), ignore_index=True)
```

Enfim salvamos o arquivo num formato mais conveniente (como *parquet*).

```python
data.to_parquet("projecoes_2018_indicadores.parquet")
```

Apesar da grande quantidade de dados públicos na Internet, nem sempre eles estão prontos para serem processados por modelos estatísticos e algoritmos de *machine learning*. É preciso fazer um pré-processamento para deixá-los utilizáveis. A técnica descrita neste texto é apenas um exemplo de como resolver um problema que um engenheiro / cientista de dados no seu dia a dia.
