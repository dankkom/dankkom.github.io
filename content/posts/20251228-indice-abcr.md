---
title: "Índice ABCR: O Termômetro das Rodovias e da Economia Brasileira com Python"
date: 2025-12-28T11:00:00-03:00
author: Komesu, D. K.
slug: "indice-abcr"
categories: ["Python", "Data Science", "Visualização de Dados"]
tags: ["Python", "Pandas", "Seaborn", "Análise de Dados", "Visualização de Dados", "ABCR", "Tráfego Rodoviário"]
description: "Neste post, exploramos o índice ABCR, que monitora o fluxo de veículos em praças pedagiadas no Brasil. Utilizando Python, baixamos os dados, realizamos a limpeza e transformação necessárias, e criamos visualizações para entender as tendências ao longo do tempo."
---

## Introdução: O asfalto fala sobre o PIB

Se você quer entender para onde a economia brasileira está indo antes que os dados oficiais do PIB sejam divulgados, olhe para as estradas. No Brasil, uma nação continental onde a malha ferroviária é limitada, <a href="https://pglbr.com.br/o-transporte-rodoviario-no-brasil-e-tendencias-no-setor/" rel="nofollow">o transporte rodoviário</a> não é apenas um modal logístico; é o sistema circulatório do país. Estima-se que mais de **<a href="https://www.terra.com.br/mobilidade/transporte-rodoviario-ainda-responde-por-mais-de-60-da-carga-no-pais,ec40b9d7d9b26e88dd1dc463748f5ce3aef6o8lq.html" rel="nofollow">60% de toda a carga transportada</a>** e a vasta maioria dos passageiros circulem sobre rodas.

O **<a href="https://melhoresrodovias.org.br/indice-abcr/" rel="nofollow">Índice ABCR</a>** (Associação Brasileira de Concessionárias de Rodovias) funciona, portanto, como um poderoso **<a href="https://static.poder360.com.br/2018/09/abcr_relatorio_novos_caminhos-1.pdf" rel="nofollow">indicador antecedente</a>**. Enquanto o PIB olha para o retrovisor (o que já aconteceu), o <a href="https://melhoresrodovias.org.br/indice-abcr/" rel="nofollow">fluxo de pedágios</a> nos dá o pulso da atividade econômica quase em tempo real. Se os caminhões param, a indústria parou semanas antes. Se os carros de passeio somem, a renda das famílias foi impactada.

Neste artigo, vamos transformar dados brutos em inteligência de mercado. Você aprenderá a:

1. **Automatizar a coleta de dados** de fontes governamentais/associativas com Python.
2. **Domar planilhas complexas** (MultiIndex) usando Pandas avançado.
3. **Visualizar ciclos econômicos** (Recessão de 2015, Pandemia e Recuperação) através de gráficos profissionais.

---

## Parte 1: Coleta e Preparação dos Dados (ETL)

Dados do mundo real raramente vêm prontos para análise. O arquivo da ABCR é rico, mas formatado para leitura humana (Excel), não para leitura de máquina. Vamos construir um pipeline de ETL (Extract, Transform, Load) robusto.

**Fonte dos dados:** <a href="https://melhoresrodovias.org.br/indice-abcr/" rel="nofollow">Associação Brasileira de Concessionárias de Rodovias</a>

### 1.1 Configuração do Ambiente

Para começar, precisamos de um ambiente Python equipado com as bibliotecas padrão da indústria para manipulação de dados (`pandas`) e requisições HTTP (`requests`).

```bash
pip install pandas requests seaborn openpyxl beautifulsoup4
```

Importamos as bibliotecas e definimos o estilo visual dos gráficos logo no início para garantir consistência estética.

```python
import pandas as pd
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from bs4 import BeautifulSoup

# Configuração estética do Seaborn para gráficos mais limpos
sns.set_style("whitegrid")
```

### 1.2 Extração (Download Automatizado)

Uma boa prática em Ciência de Dados é a **reprodutibilidade**. Ao invés de baixar o Excel manualmente e salvá-lo em uma pasta, escrevemos um script que busca a versão mais recente diretamente da fonte. Isso garante que, se a ABCR atualizar os dados, basta rodar o código novamente.

```python
page_url = "https://melhoresrodovias.org.br/indice-abcr/"
with requests.Session() as session:
    page = session.get(page_url)
    soup = BeautifulSoup(page.content, "html.parser")
    # Encontramos o link do arquivo Excel na página
    for link in soup.find_all("a", href=True):
        if link["href"].lower().endswith(".xlsx"):
            break
    else:
        raise ValueError("Link para o arquivo Excel não encontrado na página.")
    url = link['href']
    r = session.get(url)
    # Salvamos o binário do Excel localmente
    with open("abcr.xlsx", "wb") as f:
        f.write(r.content)
```

### 1.3 Leitura e Limpeza (O Desafio do MultiIndex)

Aqui encontramos o primeiro obstáculo técnico: o Excel da ABCR utiliza três linhas para formar o cabeçalho (Região > Tipo de Série > Tipo de Veículo). O `pandas` lida com isso através do `header=[0, 1, 2]`, criando um **MultiIndex** nas colunas.

Além disso, planilhas formatadas para impressão costumam ter colunas vazias para espaçamento visual. Identificamos e removemos essas colunas para limpar o dataset.

```python
# Lendo o Excel considerando as 3 primeiras linhas como cabeçalho
df = pd.read_excel("abcr.xlsx", sheet_name="(C) Original", header=[0, 1, 2])

# Removendo colunas desnecessárias ou vazias que costumam vir no Excel
# Nota: Os índices 4, 8 e 12 foram identificados como colunas de
# separação visual na planilha original
df = df.drop(df.columns[[4, 8, 12]], axis=1)

# Visualizando as primeiras linhas brutas
print(df)
```

```
	Unnamed: 0_level_0	Brasil	São Paulo	Paraná	Rio de Janeiro
Unnamed: 0_level_1	Série original - número índice (1999=100)	Série original - número índice (1999=100)	Série original - número índice (1999=100)	Série original - número índice (1999=100)
Unnamed: 0_level_2	LEVES	PESADOS	TOTAL	LEVES	PESADOS	TOTAL	LEVES	PESADOS	TOTAL	LEVES	PESADOS	TOTAL
0	1999-01-01	117.667781	94.286208	112.442880	115.621665	94.890700	111.018130	130.072273	86.140365	114.250698	110.267077	97.993420	108.365801
1	1999-02-01	98.318947	87.925361	95.996372	95.448095	88.485682	93.902016	101.926359	83.961737	95.456605	94.939069	87.793056	93.832101
2	1999-03-01	95.978647	107.940122	98.651586	96.015216	105.960890	98.223760	91.598440	121.605998	102.405319	97.140236	104.606781	98.296856
3	1999-04-01	97.189397	98.208155	97.417051	98.430869	96.956850	98.103547	96.803426	104.235705	99.480076	95.995827	96.133878	96.017212
4	1999-05-01	96.210717	101.902630	97.482645	96.439384	100.699425	97.385372	93.308385	107.684536	98.485792	98.608305	99.795485	98.792208
...	...	...	...	...	...	...	...	...	...	...	...	...	...
318	2025-07-01	177.311849	192.256577	180.314271	186.122331	215.642656	191.224171	NaN	NaN	NaN	152.988028	132.366085	149.488096
319	2025-08-01	170.162716	185.721481	173.101433	179.384779	208.330825	185.034465	NaN	NaN	NaN	146.991010	128.481189	143.668028
320	2025-09-01	167.518556	187.960590	171.665193	177.253170	211.821681	184.307209	NaN	NaN	NaN	144.688899	131.376640	142.344628
321	2025-10-01	174.046107	194.365095	178.231547	184.076411	218.695524	190.148474	NaN	NaN	NaN	149.144289	137.821869	147.357760
322	2025-11-01	172.052619	177.412981	172.641473	179.587214	197.913388	182.622317	NaN	NaN	NaN	146.540789	128.506901	143.385660
323 rows × 13 columns
```

*Saída (Resumida):* Observe como a estrutura hierárquica é complexa. Temos "Brasil" no nível 0, "Série Original" no nível 1 e "LEVES/PESADOS" no nível 2.

Para facilitar o trabalho, vamos renomear as colunas e achatá-las, garantindo que a coluna de datas seja tratada corretamente.

### 1.4 Transformação: De "Wide" para "Long" (Tidy Data)

Para criar visualizações com bibliotecas modernas como o `seaborn` (ou Tableau/PowerBI), o formato "Wide" (uma coluna para cada variável) é ruim. Precisamos do formato "Long" (Tidy Data), onde:

* Cada coluna é uma variável (Data, Local, Tipo, Valor).
* Cada linha é uma observação única.

Usamos a função `.stack()` para "empilhar" os níveis das colunas transformar essa matriz larga em uma lista longa e vertical.

```python
data_col = ('Data', '', '')
if data_col not in df.columns:
    data_col = next((c for c in df.columns if c[0] == 'Data'), None)

df = df.set_index(data_col).stack(list(range(df.columns.nlevels))).reset_index()
df.columns = ['Data', 'Local', 'Variável', 'Tipo', 'Valor']
print(df)
```

```
	Data	Local	Variável	Tipo	Valor
0	1999-01-01	Brasil	Série original - número índice (1999=100)	LEVES	117.667781
1	1999-01-01	Brasil	Série original - número índice (1999=100)	PESADOS	94.286208
2	1999-01-01	Brasil	Série original - número índice (1999=100)	TOTAL	112.442880
3	1999-01-01	Paraná	Série original - número índice (1999=100)	LEVES	130.072273
4	1999-01-01	Paraná	Série original - número índice (1999=100)	PESADOS	86.140365
...	...	...	...	...	...
3730	2025-11-01	Rio de Janeiro	Série original - número índice (1999=100)	PESADOS	128.506901
3731	2025-11-01	Rio de Janeiro	Série original - número índice (1999=100)	TOTAL	143.385660
3732	2025-11-01	São Paulo	Série original - número índice (1999=100)	LEVES	179.587214
3733	2025-11-01	São Paulo	Série original - número índice (1999=100)	PESADOS	197.913388
3734	2025-11-01	São Paulo	Série original - número índice (1999=100)	TOTAL	182.622317
3735 rows × 5 columns
```

Agora temos um dataset limpo, padronizado e pronto para alimentar qualquer modelo de Machine Learning ou dashboard.

---

## Parte 2: Análise Exploratória e Suavização

### 2.1 O Ruído da Sazonalidade

Dados de tráfego são extremamente voláteis. Feriados como Carnaval ou Natal, e até o número de dias úteis no mês, causam picos e vales abruptos. Ao plotarmos os dados brutos, vemos muito "ruído" e pouca "tendência".

```python
# Configuração estética dos gráficos
plt.rcParams.update(
    {
        "font.size": 22,
        "font.family": "Times New Roman",
        "axes.facecolor": "#FFFFFF",
        "figure.facecolor": "#FFFFFF",
        "font.weight": "normal",
    },
)
```

```python
f, ax = plt.subplots(figsize=(16, 10))
sns.lineplot(x="Data", y="Valor", hue="Local", data=df[df["Tipo"] == "TOTAL"])
plt.savefig("abcr-0.png", dpi=120, bbox_inches="tight")
```

*Figura 1: A série bruta mostra a dificuldade de leitura devido à volatilidade mensal.*

<a href="https://imgbox.com/Xh0LRO1k" target="_blank" rel="noopener noreferrer nofollow"><img src="https://images2.imgbox.com/f6/dc/Xh0LRO1k_o.png" alt="image host"/></a>

### 2.2 Revelando a Tendência (Média Móvel)

Para limpar esse ruído e enxergar a direção real da economia, aplicamos uma **Média Móvel de 12 meses**. Essa técnica estatística suaviza a curva, anulando os efeitos sazonais (comparando o ciclo anual completo) e destacando a tendência estrutural.

```python
# Pivotamos novamente para calcular a média móvel (rolling mean)
df2 = df.pivot_table(index=["Data"], columns=["Local", "Tipo"], values="Valor")
df2 = df2.rolling(12, center=False).mean() # Janela de 12 meses

# Voltamos para o formato Long para plotagem
df2 = df2.reset_index().melt(id_vars=[("Data", '')], value_name="Valor")
df2 = df2[~df2["Valor"].isna()] # Removemos os NaNs gerados pela janela móvel
df2.columns = ['Data', 'Local', 'Tipo', 'Valor']
print(df2)
```

```
	Data	Local	Tipo	Valor
11	1999-12-01	Brasil	LEVES	100.000000
12	2000-01-01	Brasil	LEVES	99.806610
13	2000-02-01	Brasil	LEVES	99.474390
14	2000-03-01	Brasil	LEVES	99.946861
15	2000-04-01	Brasil	LEVES	100.135661
...	...	...	...	...
3871	2025-07-01	São Paulo	TOTAL	181.186747
3872	2025-08-01	São Paulo	TOTAL	181.498007
3873	2025-09-01	São Paulo	TOTAL	181.856594
3874	2025-10-01	São Paulo	TOTAL	182.433105
3875	2025-11-01	São Paulo	TOTAL	182.721460
3603 rows × 4 columns
```

---

## Parte 3: Insights Visuais e História Econômica

Com os dados tratados, os gráficos deixam de ser riscos aleatórios e passam a contar a história recente do Brasil.

### 3.1 Análise Regional: A Disparidade do Desenvolvimento

O gráfico a seguir ilustra a média móvel por região. Ele é um retrato fiel das desigualdades regionais e da resiliência econômica de cada estado.

```python
f, ax = plt.subplots(figsize=(16, 16))
sns.lineplot(
    x="Data",
    y="Valor",
    hue="Local",
    data=df2[df2["Tipo"] == "TOTAL"],
    linewidth=3,
)
f.suptitle(
    "Fluxo de veículos em\npraças pedagiadas",
    fontsize=80,
    fontweight="bold",
    horizontalalignment="left",
    x=0.025,
    y=0.975,
)
ax.set_title(
    "Média móvel de 12 meses do índice ABCR por região",
    fontsize=30,
    style="italic",
    horizontalalignment="right",
    x=1,
    y=1,
)
ax.set_ylabel("Índice (1999=100)")
ax.set_position([0.075, 0.125, 0.9, 0.65])
plt.figtext(x=0.025, y=0.025, s="Fonte: ABCR")
plt.savefig("abcr-1.png", dpi=120)
```

*Figura 2: Análise Regional da atividade econômica via tráfego.*

<a href="https://imgbox.com/zkS7jtai" target="_blank" rel="noopener noreferrer nofollow"><img src="https://images2.imgbox.com/f6/2a/zkS7jtai_o.png" alt="image host"/></a>

**O que os dados nos dizem:**

1. **A "Década Perdida" (2014-2016):** Observe a inclinação negativa acentuada em todas as curvas a partir de 2014. Isso reflete a grave recessão econômica brasileira. Nenhuma região escapou ilesa.
2. **O "Crash" da COVID-19 (2020):** A queda vertical é o impacto imediato dos lockdowns. Diferente da recessão de 2015, que foi uma erosão lenta, 2020 foi um choque súbito de oferta e demanda.
3. **A Recuperação Assimétrica:**
   * **São Paulo (Vermelho):** É a locomotiva. Recuperou-se em "V" e já supera largamente os níveis pré-crise. A diversificação econômica (indústria + serviços + agro) blinda o estado.
   * **Rio de Janeiro (Verde):** A linha verde conta uma história de estagnação. O estado luta para retomar os níveis de tráfego de uma década atrás, refletindo crises fiscais estaduais e menor dinamismo industrial.
   * **Paraná (Laranja):** A volatilidade ascendente reflete a força do Agronegócio. As safras recordes impulsionam o fluxo de caminhões, garantindo uma tendência de alta robusta.

### 3.2 Termômetro de Consumo vs. Produção (Leves vs. Pesados)

Ao separar o tráfego por tipo de veículo (consolidado Brasil), temos uma proxy perfeita para **Renda das Famílias** (Leves) vs. **Produção Industrial/Agro** (Pesados).

```python
f, ax = plt.subplots(figsize=(16, 16))
sns.lineplot(
    x="Data",
    y="Valor",
    hue="Tipo",
    data=df2[df2["Local"] == "Brasil"],
    linewidth=3,
)
f.suptitle(
    "Fluxo de veículos em\npraças pedagiadas",
    fontsize=80,
    fontweight="bold",
    horizontalalignment="left",
    x=0.025,
    y=0.975,
)
ax.set_title(
    "Média móvel de 12 meses do índice ABCR por tipo de veículo",
    fontsize=30,
    style="italic",
    horizontalalignment="right",
    x=1,
    y=1,
)
ax.set_ylabel("Índice (1999=100)")
ax.set_position([0.075, 0.125, 0.9, 0.65])
plt.figtext(x=0.025, y=0.025, s="Fonte: ABCR")
plt.savefig("abcr-2.png", dpi=120)
```

*Figura 3: O descolamento entre produção e consumo.*

<a href="https://imgbox.com/SvcQv6GP" target="_blank" rel="noopener noreferrer nofollow"><img src="https://images2.imgbox.com/e8/80/SvcQv6GP_o.png" alt="image host"/></a>

**Análise Econômica:**

* **Veículos Pesados (Linha Laranja - Produção):** É o setor mais resiliente. Note que, mesmo na pandemia, a queda foi menor e a recuperação foi fulminante. O Brasil precisava continuar transportando soja, milho e bens essenciais. É o motor que puxa o índice para cima.
* **Veículos Leves (Linha Azul - Consumo):** É altamente sensível à renda e ao desemprego. Sofreu o maior impacto durante o isolamento social e sua recuperação é mais lenta. O fato de a linha azul estar abaixo da laranja nos últimos anos indica que a *produção* (PIB) está crescendo mais rápido que a capacidade de *consumo* (bem-estar) das famílias, ou que houve uma mudança estrutural no comportamento de transporte (home office, preço dos combustíveis).

---

## Conclusão

Através de poucas linhas de código Python, transformamos uma planilha burocrática em um painel econômico vibrante. A análise do Índice ABCR nos mostra que a recuperação econômica brasileira recente é liderada pelo setor produtivo (caminhões/agro) e fortemente concentrada em polos específicos como São Paulo e o Sul do país.

Para o cientista de dados ou economista, fica a lição: **os dados mais valiosos muitas vezes estão escondidos em formatos não amigáveis**. A habilidade de limpar e estruturar esses dados (ETL) é tão importante quanto a capacidade de gerar gráficos bonitos.

## Referências

1. ASSOCIAÇÃO BRASILEIRA DE CONCESSIONÁRIAS DE RODOVIAS. Índice ABCR – apresentação, metodologia e séries históricas. São Paulo, 2025. Disponível em: <a href="https://melhoresrodovias.org.br/indice-abcr/" rel="nofollow">https://melhoresrodovias.org.br/indice-abcr/</a>. Acesso em: 28 dez. 2025.
2. ASSOCIAÇÃO BRASILEIRA DE CONCESSIONÁRIAS DE RODOVIAS. ABCR em movimento 2024: relatório anual. São Paulo, 2024. Disponível em: <a href="https://melhoresrodovias.org.br/wp-content/uploads/2025/07/ABCR-em-movimento-2024.pdf" rel="nofollow">https://melhoresrodovias.org.br/wp-content/uploads/2025/07/ABCR-em-movimento-2024.pdf</a>. Acesso em: 28 dez. 2025.
3. CONFEDERAÇÃO NACIONAL DO TRANSPORTE. Pesquisa CNT de Rodovias 2023. Brasília, 2023. Disponível em: <a href="https://www.cnt.org.br/agencia-cnt/pesquisa-cnt-de-rodovias-2023-refora-a-importancia-de-maior-investimento-na-malha-rodoviria" rel="nofollow">https://www.cnt.org.br/agencia-cnt/pesquisa-cnt-de-rodovias-2023-refora-a-importancia-de-maior-investimento-na-malha-rodoviria</a>. Acesso em: 28 dez. 2025.
4. CONFEDERAÇÃO NACIONAL DO TRANSPORTE. Transporte rodoviário ainda responde por mais de 60% da carga no país. Brasília, 2025. Disponível em: <a href="https://www.terra.com.br/mobilidade/transporte-rodoviario-ainda-responde-por-mais-de-60-da-carga-no-pais" rel="nofollow">https://www.terra.com.br/mobilidade/transporte-rodoviario-ainda-responde-por-mais-de-60-da-carga-no-pais</a>. Acesso em: 28 dez. 2025.
5. PGL BRASIL. O transporte rodoviário no Brasil e tendências no setor. 2025. Disponível em: <a href="https://pglbr.com.br/o-transporte-rodoviario-no-brasil-e-tendencias-no-setor/" rel="nofollow">https://pglbr.com.br/o-transporte-rodoviario-no-brasil-e-tendencias-no-setor/</a>. Acesso em: 28 dez. 2025.
6. R. S. TRANSPORTES. 60% da carga no Brasil é transportada pelo modal rodoviário. s.l., s.d. Disponível em: <a href="https://www.rstransportes.com/blog/60-da-carga-no-brasil-e-transportada-pelo-modal-rodoviario/" rel="nofollow">https://www.rstransportes.com/blog/60-da-carga-no-brasil-e-transportada-pelo-modal-rodoviario/</a>. Acesso em: 28 dez. 2025.
7. ASSOCIAÇÃO BRASILEIRA DE CONCESSIONÁRIAS DE RODOVIAS. Novos caminhos para concessões de rodovias no Brasil: Índice ABCR, o termômetro da economia. Brasília: Poder360, 2018. Disponível em: <a href="https://static.poder360.com.br/2018/09/abcr_relatorio_novos_caminhos-1.pdf" rel="nofollow">https://static.poder360.com.br/2018/09/abcr_relatorio_novos_caminhos-1.pdf</a>. Acesso em: 28 dez. 2025.
8. ECONODADOS. Séries históricas do Índice ABCR (fluxo de veículos em praças pedagiadas – Brasil, Leves, Pesados, Total, 1999=100). 2025. Disponível em: <a href="https://web.macrodados.com/tabela.dll/in?pg=1&cod=818" rel="nofollow">https://web.macrodados.com/tabela.dll/in?pg=1&cod=818</a>. Acesso em: 28 dez. 2025.
9. IMTRAFF. Modelos de projeção de variação de tráfego rodoviário a partir do Índice ABCR. São Paulo, 2021. Disponível em: <a href="https://www.imtraff.com.br/wp-content/uploads/2021/10/Artigo-Previsao-TAXA-DE-CRESCIMENTO-DE-TRAFEGO.pdf" rel="nofollow">https://www.imtraff.com.br/wp-content/uploads/2021/10/Artigo-Previsao-TAXA-DE-CRESCIMENTO-DE-TRAFEGO.pdf</a>. Acesso em: 28 dez. 2025.
10. MATO GROSSO DO SUL. Secretaria de Estado de Governo e Gestão Estratégica. MODELAGEM TÉCNICA – Produto 1: estudos de tráfego. Campo Grande, 2025. Disponível em: <a href="https://www.epe.segov.ms.gov.br/wp-content/uploads/2025/01/Produto-1-Estudos-de-trafego-1.pdf" rel="nofollow">https://www.epe.segov.ms.gov.br/wp-content/uploads/2025/01/Produto-1-Estudos-de-trafego-1.pdf</a>. Acesso em: 28 dez. 2025.
