---
title: "O que é a Quantilica"
date: 2026-09-25T09:00:00-03:00
author: Komesu, D. K.
slug: o-que-e-quantilica
categories: [Quantilica]
tags: [Quantilica, Dados Abertos, Python, IBGE, BCB, DATASUS, SIDRA, Tesouro Direto, Open Source]
description: "A Quantilica é um ecossistema aberto de ferramentas Python para dados públicos brasileiros — IBGE, Tesouro, DATASUS, INMET, CAGED, Comex e mais. Entenda a dor que ela resolve, os princípios e por onde começar."
---

## Pare de raspar governo. Comece a analisar.

Quem já tentou trabalhar com dados oficiais brasileiros conhece o roteiro:

- A API do IBGE devolve `502` no meio de uma série histórica.
- O FTP do DATASUS parece ter parado em 1998 e cai a cada três dias úteis.
- O CSV de 50 milhões de linhas do CAGED estoura a memória do Pandas.
- O Siscomex serve arquivos de gigabytes com SSL quebrado e schemas que mudam sem aviso.
- O Tesouro publica taxas em planilhas com cabeçalhos hierárquicos e `;` como separador.
- Cada análise começa com duas semanas de raspagem antes do primeiro insight.

Você está fazendo um trabalho que outra pessoa já fez ontem. E vai refazer amanhã.

A **Quantilica** resolve isso de uma vez, para todo mundo: um ecossistema aberto de coletores Python para os dados públicos brasileiros — IBGE, Tesouro Nacional, DATASUS, INMET, CAGED, RAIS, Comex, Banco Central, ANP, ANAC, INEP, RFB — com **uma ferramenta especializada por fonte**, todas seguindo os mesmos princípios.

A missão que guia o projeto é direta: *democratizar o acesso a dados públicos brasileiros por meio de ferramentas abertas, confiáveis e bem documentadas*. Os valores: **transparência** (código aberto, metodologia documentada), **precisão** (pipelines auditáveis, manifestos de proveniência, sem "magic numbers") e **acessibilidade** (APIs simples, curva de entrada baixa).

---

## Os cinco princípios

Todo pacote do ecossistema segue os mesmos cinco princípios de design:

1. **Modularidade** — uma ferramenta por fonte. Se o IBGE muda um endpoint, só um pacote precisa de release.
2. **Resiliência** — retry com backoff, pacing respeitoso, tolerância às instabilidades lendárias dos provedores oficiais.
3. **Performance** — Polars em vez de Pandas para arquivos grandes, downloads paralelos, streaming.
4. **Reprodutibilidade** — cada download vem com manifesto SHA-256: URL de origem, timestamp, checksum. Dá para auditar tudo depois.
5. **Sem mágica** — sem números escondidos, sem comportamento implícito. O que a ferramenta faz está documentado e é verificável.

---

## Uma ferramenta por dor

| Ferramenta | A dor que ela elimina |
|---|---|
| `sidra-fetcher` | API do IBGE instável, rate limiting, períodos em strings ambíguas |
| `sidra-sql` + `sidra-pipelines` | Carga de tabelas SIDRA em PostgreSQL com histórico de revisões |
| `tesouro-direto-fetcher` | CKAN do Tesouro, leitores por dataset, gráficos prontos |
| `rtn-fetcher` | Planilhas hierárquicas do RTN viradas em DataFrame tipado |
| `pdet-fetcher` | CAGED/RAIS com 50M+ linhas processadas sem estourar memória |
| `comex-fetcher` | Siscomex com SSL ruim, arquivos gigantes, downtime governamental |
| `datasus-fetcher` | FTP legado do DATASUS, crawler multithread, centenas de GB de microdados |
| `inmet-fetcher` | BDMEP do INMET com encoding limpo e séries por estação |
| `bcb-sgs-fetcher` + `bcb-sgs-sql` | SGS do BCB sem API de metadados, séries truncadas |
| `anp-fetcher` | Preços de combustíveis, produção, vendas e royalties |
| `anac-fetcher` | Aviação civil: voos, aeronaves, aeródromos |
| `inep-fetcher` | Bases educacionais (ENEM, Censo Escolar) em Parquet tipado |
| `rfb-cnpj-fetcher` | Base inteira de CNPJs (245 GB) com download paralelo |

Por baixo, quatro pacotes de fundação sustentam tudo: `quantilica-core` (HTTP resiliente, storage atômico, manifestos), `quantilica-analytics` (Parquet tipado com proveniência), `quantilica-cli` (o comando único `quantilica <fonte> <cmd>`) e `quantilica-catalog` (modelo canônico para cruzar fontes).

Por cima, o **portal web** da Quantilica — a aplicação unificada onde dado bruto vira tabela curada, gráfico e artigo, cobrindo as áreas fiscal, saúde, IBGE, Banco Central e Tesouro Direto. É a camada que o usuário final enxerga; os coletores são o motor embaixo dela.

---

## Comece em 5 minutos

Pré-requisitos: Python 3.12+ e [uv](https://github.com/astral-sh/uv).

```bash
# Instala a CLI unificada
uv tool install quantilica-cli

# Instala o coletor desejado sob demanda
quantilica install comex
```

Ou como biblioteca no seu projeto:

```bash
uv add sidra-fetcher --index https://index.quantilica.com/simple/
```

```python
# O IPCA-15 em 3 linhas
from sidra_fetcher.fetcher import SidraClient

with SidraClient() as client:
    agregado = client.get_agregado(1705)  # metadados + períodos + localidades
```

Documentação completa em [docs.quantilica.com](https://docs.quantilica.com), código em [github.com/Quantilica](https://github.com/Quantilica).

---

## Acompanhe a construção

Este blog mantém um **diário mensal de desenvolvimento** da Quantilica — o retrato operacional, as decisões e o roadmap, com versões e evidências. Comece pelo [Devlog #01 — visão geral e estado de setembro/2026](/posts/devlog-quantilica-01-visao-geral), que traz o mapa técnico completo do ecossistema.

---

## Nesta série

* **O que é a Quantilica** (este post — o pilar evergreen)
* [Devlog #01 — Visão geral do ecossistema e estado de setembro/2026](/posts/devlog-quantilica-01-visao-geral)
