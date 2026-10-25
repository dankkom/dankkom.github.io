---
title: "Devlog Quantilica #02 — Outubro/2026: quando o dado parece certo e está errado"
date: 2026-10-23T09:00:00-03:00
author: Komesu, D. K.
slug: devlog-quantilica-02-dado-certo-que-esta-errado
categories: [Quantilica, Devlog]
tags: [Quantilica, Devlog, Python, Dados Abertos, DATASUS, B3, Polars, Qualidade de Dados]
description: "Outubro/2026 na Quantilica: três fontes novas (B3, CVM e TSE), a fundação de download retomável e, principalmente, os erros silenciosos que corrigimos em DATASUS, B3, INMET e PDET — dados que carregavam sem erro e estavam errados."
---

> **Novo por aqui?** Leia antes [O que é a Quantilica](/posts/o-que-e-quantilica).

## O mês em uma frase

Em outubro o ecossistema passou de 12 para **15 fontes** e publicou mais de **60 versões** em 18 pacotes. Mas o que mais me ensinou não foi nenhuma funcionalidade nova. Foi uma série de bugs com a mesma assinatura: **o código rodava, o arquivo Parquet saía, os testes passavam — e os números estavam errados.**

Um erro que derruba o programa é barato: você vê, corrige e segue. O erro que devolve um `DataFrame` de aparência normal com um valor de saúde de 1,2 trilhão de reais é o que contamina uma análise inteira antes de alguém notar. Este devlog junta os casos do mês e o que eles mudaram na forma de escrever coletores.

Combinado do [#01](/posts/devlog-quantilica-01-visao-geral): o deep-dive do SIDRA de ponta a ponta fica para o #03. O SIDRA teve pouca novidade em outubro, e o tema de correção de dados era a história real do mês.

---

## O que mudou

### Três fontes novas

| Pacote | Versão | O que coleta |
|---|---|---|
| `b3-fetcher` | 0.1.0 | Cotações Históricas (COTAHIST) da B3: arquivos anuais desde 1986 |
| `cvm-fetcher` | 0.1.1 | Dados abertos da CVM: cadastros, companhias, fundos, estruturados e mercado |
| `tse-fetcher` | 0.2.0 | Dados eleitorais do TSE: candidatos, bens, votação e prestação de contas |

Com elas, a documentação pública ganhou dois domínios novos: **Mercado de Capitais** e **Política**. Todas se instalam pelo mesmo caminho das demais (`quantilica install b3`, `quantilica install cvm`, `quantilica install tse`) e seguem o contrato de sempre: download atômico, manifesto SHA-256 e, opcionalmente, conversão para Parquet.

O COTAHIST merece uma nota: é um arquivo de texto de **largura fixa**, com registros de 245 bytes e campos que dependem do layout publicado pela B3. É o tipo de formato em que o erro silencioso mora — voltamos a ele abaixo.

### Fundação: baixar sem refazer, sem derrubar o servidor

As versões do `quantilica-core` foram de 0.7.1 para **0.12.1**, e a CLI de 0.7.0 para **0.12.0**. O fio condutor foi tornar o download **verificável e retomável**:

* **`check` antes de `sync`.** Os coletores baseados na CLI unificada (e o `sidra-fetcher`) ganharam o comando `check`, que compara o remoto com o local *sem baixar nada* e emite um plano (`--json` ou `--out`). O `sync --from-plan` baixa só o que o plano marcou como necessário. Dá para auditar antes de gastar banda — e dos servidores alheios.
* **Retomada com `Range`.** O servidor de balança comercial do MDIC, por exemplo, derruba a conexão a cada ~3,8 MB. Antes, cada queda consumia uma tentativa e o arquivo recomeçava do zero. Agora, se o servidor honra `Range` e o download *avançou*, a tentativa não é gasta: o arquivo parcial é retomado de onde parou, com um teto de retomadas para não girar para sempre.
* **Frescor por política.** O _core_ ganhou sondas de frescor (HTTP via `HEAD`, FTP via `SIZE`/`MDTM`) e políticas explícitas de pular ou baixar. O sidecar de manifesto passou a valer como prova de que o arquivo local está íntegro.
* **Peças que antes eram copiadas em cada coletor** subiram para o núcleo: `RateLimiter` público, parser de listagem FTP legada e `decompress_archive` com proteção contra *Zip Slip* (um ZIP malicioso não escreve fora do diretório de destino).
* **`quantilica health`** faz sondas leves nas fontes canônicas e mostra estado e latência em tabela ou JSON.
* Na camada analítica, o `quantilica-analytics` 0.4.0 escreve Parquet de forma atômica (arquivo temporário e `os.replace`), com a proveniência do arquivo bruto gravada nos metadados.

### A fonte oficial mudou sem avisar

Parte do trabalho do mês foi só acompanhar provedores que mudaram:

* **TSE** removeu do CDN os arquivos de receitas e despesas particionados por UF — centenas de downloads passaram a dar 404. O coletor agora usa o arquivo nacional consolidado (`prestacao_contas`) e mantém os nomes antigos como alias.
* **SIDRA** passou a responder HTTP 400 acima de 50 mil valores por requisição. O limite do coletor caiu de 100 mil para 50 mil e o erro virou uma exceção própria, com mensagem útil em vez de traceback.
* **RAIS** republicou 2023, 2024 e 2025 em outro formato: vírgula como separador, ponto decimal, aspas e 62 colunas em vez de 60.
* **RTN** teve o catálogo reorganizado em três grupos. O `sync` padrão baixa as 87 planilhas de série histórica, em vez de mais de 2 mil arquivos — o resto continua disponível pedindo o grupo.

Versões atuais dos coletores no fim do mês: `datasus-fetcher` 0.14.1, `pdet-fetcher` 0.7.0, `inmet-fetcher` 0.5.1, `rtn-fetcher` 0.5.1, `rfb-cnpj-fetcher` 0.4.0, `bcb-sgs-fetcher` 0.11.0, `sidra-fetcher` 0.10.8, `tesouro-direto-fetcher` 3.2.4, `comex-fetcher` 2.3.2, `anp-fetcher` 1.4.3, `anac-fetcher` 0.4.3 e `inep-fetcher` 0.4.2.

---

## O que aprendi: o erro silencioso é o pior erro

Cinco casos, todos corrigidos neste mês. Cada um virou uma regra.

### 1. O DATASUS e o campo que começava no lugar errado

Os arquivos `.dbf` do DATASUS trazem, no cabeçalho de cada campo, o deslocamento dentro do registro. Nos arquivos reais esse deslocamento vem **zerado**. A biblioteca de leitura rápida (`fastdbf`) confiava nele e lia todos os campos a partir do início do registro.

O resultado: no SIH, a data de internação saía como `' 1200002'` e o valor total (`VAL_TOT`) chegava a **1,2 trilhão**; no SIM, `SEXO` vinha vazio. Pior: no SIA-PA o leitor "funcionava" só porque o lixo fazia a biblioteca rápida falhar e cair no leitor lento (`dbfread`), que lia certo. O sistema acertava *por acaso*.

A correção tem três partes:

* o cabeçalho passa a ser recalculado somando o tamanho dos campos, numa cópia (o arquivo original não é tocado);
* cada pedaço lido compara as primeiras 50 linhas com o `dbfread`; se divergir, relê com o leitor lento e **avisa**;
* testes com recortes de arquivos reais de SIM, SINASC, SIH e SINAN — que falham no leitor antigo.

Quem gerou Parquets de DATASUS antes da v0.14.0 precisa **regenerá-los**. Está no changelog em destaque, porque é o tipo de correção que não se pode deixar para o usuário descobrir.

De quebra, uma melhora de memória no mesmo trabalho: ler o `.dbc` de 166 MB do SIA-PA (4,7 milhões de linhas) chegava a **18,8 GB** de RAM; lendo em pedaços de 32 MiB, caiu para **4,7 GB**, com o `DataFrame` idêntico (mesmo hash de linhas).

### 2. B3: R$ 37,80 não é 37,800000000000004

O COTAHIST guarda preços como inteiros com vírgula implícita: `3780` num campo `(11)V99` significa R$ 37,80. A primeira versão do leitor dividia por 100 em ponto flutuante:

```python
>>> 3780 * 0.01
37.800000000000004
>>> from decimal import Decimal
>>> Decimal(3780) / Decimal(100)
Decimal('37.80')
```

Parece detalhe até você somar milhões de linhas, comparar com outra fonte ou fazer um `join` por preço. A regra agora é: **campo monetário com escala fixa vira `Decimal` com a precisão e a escala do próprio layout** — `(11)V99` em 13 posições vira duas casas; `(07)V06`, seis. O mesmo vale para `VAL_*` do SIH e `PA_VAL*` do SIA no DATASUS, e para `capital_social` no cadastro de CNPJ.

Para conferir, o leitor foi comparado com uma carga anterior de referência. Nos 40 arquivos anuais de 1986 a 2025, não houve erro nem nulo; nos 9.834 pregões em comum, 9.832 tinham contagem, soma do último preço e soma do volume idênticas. Os 2 pregões restantes divergem e ficaram registrados no changelog, em vez de escondidos.

### 3. INMET: o teste passava, o arquivo real não

O leitor do INMET tinha testes verdes. Só que com fixtures **sintéticas**. Com os arquivos reais:

* o encoding era Latin-1, mas lido de dentro de um ZIP o parâmetro era ignorado, e 6 das 17 medidas perdiam o nome;
* o tipo era inferido nas primeiras 100 linhas, e um `,2` (vírgula sem o zero) derrubava a leitura;
* a pasta guardava várias versões do mesmo ano, e o leitor **concatenava todas**, repetindo horas;
* o ZIP de 2026 trazia dois recortes da mesma estação (até 31/08 e até 30/09), também concatenados.

Agora: tudo lido como texto e convertido depois; colunas mapeadas pelo **nome do cabeçalho**, não pela posição; só a versão mais recente é lida; e um par (estação, hora) repetido levanta erro. `data_hora` passou a ter fuso UTC, como o próprio cabeçalho diz — uma mudança incompatível, anunciada como tal.

### 4. PDET: o ponto que virou milhar

Na RAIS republicada, o separador decimal mudou de vírgula para ponto. O conversor, configurado para o formato brasileiro (`1.234,56`), removia os pontos como se fossem separadores de milhar:

```python
>>> float("2956.01".replace(".", "").replace(",", "."))
295601.0
```

Um salário de R$ 2.956,01 virava R$ 295.601. Sem erro, sem aviso. Ao mesmo tempo, as três colunas de faixas (`Faixa Rem Média`, `Faixa Hora Contrat`, `Faixa Rem Dez`) mudaram de ordem, e o mapeamento **por posição** teria dado a cada coluna o nome de outra.

Duas correções: o separador decimal passou a ser detectado pelo arquivo, e as colunas passaram a ser nomeadas pelo cabeçalho, com mapas que cobrem os 24 layouts publicados no FTP da PDET (561 arquivos conferidos) e reproduzem os nomes antigos nos layouts antigos. Cabeçalho desconhecido ou nome repetido levanta `ParseError`.

A versão 0.7.0 trouxe uma variação do mesmo problema nos campos indicadores (sim/não): qualquer código diferente de zero virava `True`, inclusive o `9`, que significa "não identificado". Ilustrativamente:

```python
# antes: tudo que não é "0" vira verdadeiro
valor = codigo != "0"            # "9" -> True (errado)

# depois: mapa explícito; o resto falha em voz alta
MAPA = {"0": False, "1": True, "9": None}
valor = MAPA[codigo]             # "7" -> KeyError (ParseError no coletor)
```

### 5. Códigos não são números

Parecia inofensivo converter `SEXO` ou `RACA_COR` em inteiro. Mas `"01"` vira `1`, e `"M"`/`"F"` (que o SINAN usa) viravam **nulo** num cast tolerante. Pior: `QTDFILVIVO = "99"` significa "ignorado", não 99 filhos — e há valores como `"XX"` e `"9."` na origem.

Códigos categóricos agora ficam como **texto**. O mesmo no cadastro de CNPJ: partes do CNPJ, CNAE e município mantêm os zeros à esquerda.

### As cinco regras que saíram disso

1. **Conversão estrita.** Valor que não converte levanta erro com a coluna e exemplos. Nulo só aparece para *sentinelas declaradas* (`-9999`, vazio, `N/D`), nunca como saída padrão de um cast que falhou.
2. **Fixtures reais.** Teste com dado sintético só prova que o código lê o que o autor imaginou. Cada leitor agora tem recortes de arquivos reais — com o cabeçalho original — no repositório.
3. **Tipo exato para dinheiro.** `Decimal` com escala do layout; ponto flutuante só para o que é de fato medida.
4. **Nome, não posição.** Mapear colunas pelo cabeçalho transforma "o provedor mudou a ordem" de dado errado em erro claro.
5. **Validar antes de persistir.** O `bcb-sgs-fetcher` 0.11.0 corrigiu um caso em que a página de "sessão expirada" era salva como se fosse o metadado da série e só estourava no parse. Agora cada resposta é validada antes de ir para o disco.

Nenhuma dessas regras é sofisticada. O difícil é perceber que elas faltam: na maioria dos casos, **nada quebrou** — ou quebrou só em alguns arquivos. O que ajudou foi comparar com uma segunda fonte (o `dbfread`, uma carga de referência), olhar o valor máximo de uma coluna e abrir um arquivo real em vez de confiar no teste.

---

## Próximo mês

O #03 faz o deep-dive prometido: o **pipeline SIDRA de ponta a ponta**, do coletor aos pipelines declarativos e à carga em banco, incluindo o que aprendi medindo o reuso de conexão (cerca de 140 ms contra 1,2 s por requisição pequena quando o cliente é usado dentro de `with`). Se algum outro provedor mudar de formato até lá, ele entra como nota.

---

## Nesta série

* [O que é a Quantilica](/posts/o-que-e-quantilica) (pilar evergreen)
* [Devlog #01 — Visão geral e setembro/2026](/posts/devlog-quantilica-01-visao-geral)
* **#02 — Outubro/2026: quando o dado parece certo e está errado** (este post)
* #03 — SIDRA de ponta a ponta: coletor, pipelines e banco (planejado)

---

*Baseado em fontes públicas: documentação em docs.quantilica.com, changelogs e releases no GitHub e pacotes no PyPI/índice Quantilica. Versões referem-se ao estado em 23/10/2026.*
