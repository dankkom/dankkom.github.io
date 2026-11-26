---
title: "Devlog Quantilica #03 — Novembro/2026: SIDRA de ponta a ponta"
date: 2026-11-25T09:00:00-03:00
author: Komesu, D. K.
slug: devlog-quantilica-03-sidra-ponta-a-ponta
categories: [Quantilica, Devlog]
tags: [Quantilica, Devlog, Python, Dados Abertos, IBGE, SIDRA, PostgreSQL, Qualidade de Dados]
description: "Novembro/2026 na Quantilica: o SIDRA vira ibge-sidra-fetcher e passa a guardar cada resposta crua com a data da fonte, o caminho completo até o banco, dez coletores na versão 0.1.0 e um núcleo de download que respeita o limite de cada servidor."
---

> **Novo por aqui?** Leia antes [O que é a Quantilica](/posts/o-que-e-quantilica).

## O mês em uma frase

Novembro foi o mês de mexer em **onde e como o dado fica guardado**. O SIDRA, prometido para este número no [#02](/posts/devlog-quantilica-02-dado-certo-que-esta-errado), mudou de nome, de layout de arquivo e de forma de atualização. A camada de download ganhou regras por servidor, e dez coletores ganharam a versão 0.1.0. No total, foram **238 versões em 29 pacotes** publicados no mês.

Combinado do #02: este número faz o deep-dive do SIDRA, do coletor ao banco. Ele está na seção [SIDRA de ponta a ponta](#sidra-de-ponta-a-ponta).

---

## O que mudou

### SIDRA: `sidra-fetcher` vira `ibge-sidra-fetcher`

Desde **13 de novembro** (versão 0.12.0), o pacote se chama `ibge-sidra-fetcher`, com módulo `ibge_sidra_fetcher`. O nome agora segue o padrão do órgão, como `bcb-sgs` e `bcb-microdados`. Não há módulo de compatibilidade: quem fazia `import sidra_fetcher` precisa trocar o import. A migração mais simples é `quantilica install ibge-sidra`, que instala a distribuição nova e remove a antiga.

O produto SIDRA não mudou. Mudaram o nome do pacote e, a partir da 0.13.0, o caminho padrão de saída: de `/data/sidra` para `/data/ibge-sidra`.

### Um arquivo por consulta, com a data da fonte

A mudança mais importante do mês é de layout, e ela é incompatível (versão 0.13.0, 19 de novembro). Até a 0.12.0, o `sync` juntava as respostas num NDJSON por nível. Agora cada consulta ao endpoint `/values` vira um arquivo com a resposta crua do servidor, byte a byte, e o nome carrega a data de modificação do período no SIDRA:

```text
<raiz>/t-<id>/t-<id>_p-<periodo>_..._n<nivel>-<locs>_v-<vars>@AAAAMMDD.json
<raiz>/t-<id>/metadados@AAAAMMDD.json
<raiz>/indice_pesquisas@AAAAMMDD.json
```

Quando o IBGE revisa um período, o arquivo novo aparece ao lado do antigo, que não é apagado. Se a API não informa a data, o sufixo vira `@00010101`.

### Índice de pesquisas (0.14.0, 24 de novembro)

O `sync` também grava o índice de pesquisas do SIDRA, mas só quando o conteúdo muda (comparação por sha256). Se o índice falhar, o download continua e sai um aviso.

### Núcleo: download que respeita cada servidor (`quantilica-core` 0.22 a 0.27.1)

Quatro mudanças que os coletores passam a poder usar (quase todas são opt-in):

* **Política por host** (0.23.0, 15 de novembro): balde de tokens para controlar o ritmo, pausa por host quando o servidor responde `429` e disjuntor, que recusa novas requisições para um host em falha até um teste após o cooldown. Tudo é opt-in: sem configurar, o comportamento é o de antes.
* **Paginação OData por chave**, sem `$skip` (0.23.0). Se a fonte ignora o filtro, o erro aparece em vez de a coleta truncar em silêncio.
* **Detector de regeneração** (0.23.0): compara o conteúdo sem as colunas de carimbo e marca o arquivo como `skipped` quando só o carimbo mudou.
* **Limpeza de temporários** (0.22.0): `remove_stale_atomic_temps` apaga resíduos de downloads interrompidos, e `extracted_archive` sempre remove a pasta de extração. Na 0.27.1 (19 de novembro), arquivos de lixo de ZIP, como `Thumbs.db`, `.DS_Store` e `__MACOSX/`, deixaram de ser gravados no destino.

### Coletores

* **Dez fontes com versão inicial em 1º de novembro** (0.1.0): `antt-fetcher`, `bcb-microdados-fetcher`, `capes-fetcher`, `infosiga-fetcher`, `ipeadata-fetcher`, `loterias-fetcher`, `ons-fetcher`, `pgfn-fetcher`, `sigtap-fetcher` e `transparencia-sp-fetcher`.
* **DATASUS 0.21.0** (25 de novembro): o Parquet de um período é escrito numa única passada. Quando a pasta tem duas versões do mesmo bruto, só a mais nova é decodificada. Um DBC corrompido vira erro registrado, e o resto do período é gravado.
* **Demais atualizações do mês:** `anac-fetcher` 0.10.1, `anp-fetcher` 2.11.2, `inep-fetcher` 0.8.3, `rtn-fetcher` 0.7.4, `inmet-fetcher` 0.7.1, `b3-fetcher` 0.5.3 e `antt-fetcher` 0.4.2.

### Camada SQL

* **`quantilica-sql` 0.3.0** (14 de novembro): o comando `quantilica sql validate`, no motor duckdb, confere se as referências `fonte.alias` do SQL constam no arquivo de aliases e devolve erro quando não constam. `CREATE SCHEMA` só roda quando o schema não existe, porque o `IF NOT EXISTS` exige o privilégio `CREATE` no banco mesmo com o schema já criado. Isso importa quando o papel da aplicação não tem esse privilégio.
* **`quantilica-sql` 0.3.1** (25 de novembro): a conversão entrega ao conversor só a versão vigente de cada arquivo bruto.

Versões atuais em 25/11, nos pacotes centrais: `quantilica-core` 0.27.1, `quantilica-cli` 0.29.0, `quantilica-analytics` 0.15.3, `quantilica-sql` 0.3.1 e `ibge-sidra-fetcher` 0.14.0.

---

## SIDRA de ponta a ponta

O caminho de um número do IBGE até uma tabela analítica tem seis passos. Cada passo é um comando da CLI ou uma função da biblioteca.

**1. Descobrir.** `quantilica ibge-sidra periods 1620` lista os períodos com a data de modificação de cada um. Com `quantilica ibge-sidra info 1737`, você vê os metadados de uma tabela.

**2. Planejar sem baixar.** `quantilica ibge-sidra check 1620 -o ./data` compara o remoto com o local e mostra o plano. `sync --dry-run` lista os nomes de arquivo que seriam gerados. Só depois disso vem o download.

**3. Baixar respeitando o limite da API.** Desde outubro, a API recusa pedidos com mais de 50 mil valores (HTTP 400). O coletor divide o pedido por período e, quando o erro acontece mesmo assim, mostra uma mensagem útil em vez de um traceback. Desde a 0.13.0, cada pedaço cobre sempre um período só, mesmo que a tabela coubesse em uma consulta.

**4. Ler a tabela inteira.** A mesclagem saiu do download e foi para a leitura:

```python
from ibge_sidra_fetcher.reader import iter_dados_tabela

for linha in iter_dados_tabela("./data", 1620):
    ...  # cada linha vem do pedaço mais recente de cada consulta
```

Por padrão (`ultima_versao=True`), o leitor usa só a versão mais recente de cada consulta. As antigas continuam no disco.

**5. Carregar no PostgreSQL.** `quantilica sql load sidra` carrega um arquivo por chamada. Cada arquivo carregado fica registrado em `ibge_sidra.arquivo_carregado`, e a mesma carga não roda duas vezes.

**6. Materializar com um pipeline declarativo.** Um pipeline é uma pasta com o arquivo de busca (`fetch.toml`), o de transformação (`transform.toml`) e um ou mais `.sql`. O catálogo oficial tem 20 pipelines do IBGE em oito temas. O `quantilica sql run ibge/precos/snipc` materializa sete tabelas no schema `analytics`: `inpc`, `ipca`, `ipca15` e mais quatro.

O cliente também tem um detalhe de desempenho que vale conhecer. Medido em 13 de outubro contra a API, uma requisição pequena leva cerca de **140 ms dentro de um bloco `with`** e cerca de **1,2 s fora dele**. A conexão só é reaproveitada dentro do contexto. Por isso, as docstrings do cliente avisam, e os exemplos da documentação abrem o cliente com `with`.

---

## O que aprendi

Quatro decisões do mês, com os custos que cada uma trouxe.

### 1. Guarde a resposta crua; mesclar é uma decisão de leitura

O NDJSON mesclado era prático: um arquivo por nível geográfico, pronto para ler. O problema é que a versão anterior de um período não ficava como arquivo próprio, então uma revisão do IBGE não deixava rastro separado. Agora cada resposta é um arquivo com a data da fonte no nome. A revisão vira um arquivo novo, e a escolha de qual versão usar fica na leitura, com `ultima_versao=True` como padrão. O DATASUS seguiu o mesmo princípio na 0.21.0.

O custo é real. Há mais arquivos na pasta, e as versões 0.12.0 e 0.13.0 foram anunciadas como quebra de compatibilidade, porque é melhor avisar do que deixar a mudança passar despercebida.

### 2. Frescor pela data da fonte, não pelo disco

A API do SIDRA não oferece ETag nem um `HEAD` confiável para validar o conteúdo. Por isso, o plugin usa a política `REMOTE_ONLY` desde a 0.11.0: a frescura é decidida pelo conteúdo que a própria API informa, a data de modificação do período. Como essa data está no nome do arquivo, o `check` compara nomes. Ele não depende de `mtime`, que pode mudar ao copiar a pasta.

O trade-off é depender de a API informar a data certa. Quando ela não informa, o sufixo `@00010101` marca isso de forma explícita, em vez de inventar uma data.

### 3. Nem toda mudança de arquivo é mudança de dado

Algumas fontes regeneram o mesmo arquivo com um carimbo novo. Sem tratamento, cada regeneração parece uma versão nova, e o download e o reprocessamento acontecem à toa. O detector da 0.23.0 calcula o hash do conteúdo sem as colunas de carimbo, sem BOM, sem diferença de quebra de linha e também dentro de gzip. Se só o carimbo mudou, o arquivo é `skipped`.

O custo é que alguém precisa declarar quais colunas são carimbo. Uma lista errada pode esconder uma mudança real. Por isso a regra é explícita e fica no código, onde pode ser revisada.

### 4. Um servidor pode responder 200 e mandar uma página de manutenção

Esse caso já apareceu no #02, no `bcb-sgs-fetcher`, que salvou uma página de "sessão expirada" como se fosse o metadado da série. A política por host da 0.23.0 trata esse caso. O balde de tokens controla o ritmo. A pausa por host protege contra rajadas de `429`. O disjuntor reconhece página HTML curta de manutenção e para de insistir até um teste bem-sucedido após o cooldown.

O custo é o risco de configurar mal. Um disjuntor que abre na hora errada interrompe a coleta inteira de uma fonte. Por isso, tudo é opt-in e o padrão continua sendo o comportamento de antes.

---

## Próximo mês

Ficam para dezembro as pendências desta leva. A documentação ainda lista o `check` do `bcb-sgs-fetcher` como ausente, e a migração de `sidra-sql` e `bcb-sgs-sql` para o `quantilica-sql` segue gradual. Se algum provedor mudar de formato até lá, ele entra como nota, como em outubro.

---

## Nesta série

* [O que é a Quantilica](/posts/o-que-e-quantilica) (pilar evergreen)
* [Devlog #01 — Visão geral e setembro/2026](/posts/devlog-quantilica-01-visao-geral)
* [Devlog #02 — Outubro/2026: quando o dado parece certo e está errado](/posts/devlog-quantilica-02-dado-certo-que-esta-errado)
* **#03 — Novembro/2026: SIDRA de ponta a ponta** (este post)

---

*Baseado em fontes públicas: documentação em docs.quantilica.com, changelogs e releases no GitHub e pacotes no PyPI/índice Quantilica. Versões referem-se ao estado em 25/11/2026.*
