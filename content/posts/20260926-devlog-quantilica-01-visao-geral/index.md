---
title: "Devlog Quantilica #01 — Visão geral do ecossistema e estado de setembro/2026"
date: 2026-09-26T09:00:00-03:00
author: Komesu, D. K.
slug: devlog-quantilica-01-visao-geral
categories: [Quantilica, Devlog]
tags: [Quantilica, Devlog, Python, Dados Abertos, IBGE, BCB, DATASUS, SIDRA, Tesouro Direto]
description: "Primeiro post do diário mensal do ecossistema Quantilica: o mapa atual dos 12 coletores, o portal, os pipelines, a saúde das fontes em setembro/2026 e o roadmap."
---

## Por que um diário?

A Quantilica cresceu. O que começou como scripts isolados para baixar dados públicos brasileiros virou um ecossistema: 12 coletores de dados, um portal web, catálogos ETL declarativos e documentação pública — com coleta rodando todos os dias.

Com esse tamanho, o trabalho ficou invisível. Cada semana tem um ajuste de resiliência num coletor, um release novo, uma fonte que mudou de comportamento — e nada disso aparece em lugar nenhum.

Este devlog mensal resolve isso. A ideia é simples, no espírito de *build in public*:

1. **Registrar o mapa** — onde o ecossistema está hoje.
2. **Registrar o movimento** — o que mudou no mês, com versões e evidências.
3. **Registrar o aprendizado** — decisões, erros e trade-offs.
4. **Apontar o próximo mês** — o que vem a seguir.

Este #01 é o post "visão + técnico": metade mapa geral, metade retrato operacional de setembro/2026. A partir do #02, cada edição mergulha num tema (o candidato atual é o pipeline SIDRA de ponta a ponta).

> **Novo por aqui?** Leia antes [O que é a Quantilica](/posts/o-que-e-quantilica) — a dor que o projeto resolve, os cinco princípios e o quickstart de 5 minutos. Abaixo vai o mapa técnico completo, com versões verificadas hoje.

---

## 1. O mapa técnico (resumo)

O retrato conceitual está no [artigo pilar](/posts/o-que-e-quantilica). Aqui, o essencial técnico: um **ecossistema de pacotes Python para coletar, normalizar e analisar dados públicos brasileiros**, com uma CLI unificada e releases independentes por pacote.

Componentes (releases atuais em setembro/2026):

### Infraestrutura

| Pacote | Versão | Papel |
|---|---|---|
| `quantilica-core` | 0.7.0 | Fundação: HTTP com keep-alive, logging estruturado, storage atômico, manifestos SHA-256 de proveniência |
| `quantilica-analytics` | 0.2.1 | Camada analítica: Polars, PyArrow, Parquet, validação de schema |
| `quantilica-cli` | 0.3.2 | CLI unificada `quantilica <fonte> <cmd>`, descobre fetchers via entry points, sem dependências duras |
| `quantilica-catalog` | 0.2.1 | Catálogo unificado + modelo canônico de observações |

### Coletores (12 fontes)

| Pacote | Versão | Fonte | Domínio |
|---|---|---|---|
| `sidra-fetcher` | 0.10.3 | IBGE SIDRA/Agregados | IPCA, estatísticas econômicas, demografia |
| `comex-fetcher` | 2.3.1 | MDIC/Comex Stat | Importação/exportação |
| `datasus-fetcher` | 0.11.0 | DATASUS FTP | Microdados de saúde (DBC/DBF) |
| `inmet-fetcher` | 0.4.1 | INMET BDMEP | Meteorologia por estação |
| `pdet-fetcher` | 0.5.2 | MTE/PDET | Trabalho (CAGED, RAIS) |
| `rtn-fetcher` | 0.4.0 | STN | Fiscal (RTN, Excel multi-aba) |
| `tesouro-direto-fetcher` | 3.2.1 | STN | Taxas, preços e estoques de títulos |
| `bcb-sgs-fetcher` | 0.9.0 | BCB SGS | Séries temporais do Banco Central |
| `anp-fetcher` | 1.4.0 | ANP | Petróleo, gás e biocombustíveis |
| `anac-fetcher` | 0.4.0 | ANAC | Aviação civil |
| `inep-fetcher` | 0.4.1 | INEP | Educação (ENEM, Censo Escolar) |
| `rfb-cnpj-fetcher` | 0.3.1 | RFB | Cadastro público de CNPJs |

### ETL e carga em banco

| Pacote | Versão | Papel |
|---|---|---|
| `sidra-sql` | 2.0.0 | Carga SIDRA em PostgreSQL (modelo vintage/as-of) |
| `bcb-sgs-sql` | 0.2.1 | Motor de carga SGS em PostgreSQL |
| `sidra-pipelines` | — | Catálogo declarativo de pipelines SIDRA prontos para rodar |
| `bcb-sgs-pipelines` | — | Catálogo de pipelines de séries macro do BCB |

### Aplicação e publicação

* **Portal web** — aplicação unificada onde dado bruto vira tabela curada, gráfico e artigo, cobrindo as áreas fiscal, saúde, IBGE, Banco Central e Tesouro Direto.
* **Documentação pública** — portal em MkDocs (`docs.quantilica.com`) com guias por domínio (aviação, BCB, clima, comex, educação, empresas, petróleo, saúde, tesouro, trabalho, IBGE), além de conceitos, cookbook e normas de contribuição.
* **Distribuição** — só os pacotes de fundação vão ao PyPI; os coletores distribuem via GitHub Releases + índice próprio. O fluxo para o usuário é um comando único (`quantilica install <fonte>`), nunca instalação manual por repositório.

O desenho resume a filosofia: a fundação não depende de nada interno; todo coletor é um adaptador puro de fonte (requisições, retries, registros tipados). Representação analítica (DataFrames, Parquet, contratos) mora nas camadas ETL — nunca no coletor.

---

## 2. Como se trabalha

Todo coletor segue o mesmo contrato público: testes automatizados, lint limpo, changelog por release e versionamento semântico — releases de correção para robustez, minor para endpoints e tabelas novas, major para quebra de contrato. Cada pacote tem ciclo de release independente: quando uma fonte oficial muda de comportamento, só aquele coletor precisa de release, e o resto do ecossistema continua funcionando.

Todo download gera manifestos de proveniência (checksums, URLs de origem, timestamps), de modo que qualquer dataset pode ser auditado depois. É esse contrato — e não nenhum servidor específico — que permite escalar de 1 para 12 fontes sem virar bagunça.

---

## 3. Retrato de setembro/2026

### Coleta contínua

As fontes são sincronizadas todos os dias — algumas diariamente (Tesouro Direto, BCB, RTN, ANP), outras em janelas semanais ou mensais conforme o calendário de publicação de cada órgão (Comex, PDET, RFB, SIDRA, ANAC). Cada execução registra manifestos de proveniência, de modo que dá para saber exatamente quando cada dataset foi baixado e de onde veio.

### Saúde das fontes

A documentação pública classifica a maioria das fontes como estável, com três intermitentes — DATASUS, Comex e PDET — por instabilidade do lado do provedor, não do código. É o padrão do setor: FTP legado que cai, API que limita requisições, SSL quebrado. O trabalho do coletor é justamente absorver essa instabilidade para que o usuário não precise.

### O que andou no mês

Quatro frentes contam a história de setembro:

* **Microdados de saúde no navegador** — a direção é tirar a fricção do acesso ao DATASUS, inclusive com conversão de formatos legados direto no browser, mais guias de conteúdo.
* **Resiliência do SIDRA** — o IBGE passou a responder com bloqueios a coletas em ritmo alto; a resposta é pacing e backoff. Clássico: a fonte muda o comportamento, o coletor se adapta sem virar um DDoS.
* **Tabelas curadas** — URLs estáveis e amigáveis por tabela, gráficos prontos e edição editorial. É a ponte entre dado bruto e storytelling.
* **Eficiência do desenvolvimento** — testes paralelos, checagens automatizadas antes de cada PR e consolidação das ferramentas internas. Com 12+ pacotes, o gargalo é o tempo de ciclo, não a coleta em si.

Nos releases públicos, o destaque do mês foi o `quantilica-core` v0.7.0, com cliente HTTP com keep-alive — menos conexões, coletas mais rápidas e mais gentis com os servidores oficiais.

---

## 4. Roadmap: para onde isso vai

O roadmap público organiza o futuro em três frentes:

* **Confiança** — health-checks, status page pública, CI padronizado com cobertura.
* **Acesso a dados** — Parquet analítico, contratos de dados, versionamento temporal, sincronização incremental.
* **Produto** — cookbook, storytelling com dados, financiamento aberto.

O retrato de hoje: confiança em andamento pesado (é onde está o esforço de eficiência), acesso a dados pavimentado pelos motores de carga SQL, produto nascendo nas tabelas curadas e nos guias de microdados.

---

## 5. O que mudou · O que aprendi · Próximo mês

**O que mudou (mês):** `quantilica-core` v0.7.0 no PyPI, testes paralelos no ciclo de desenvolvimento, checagens automatizadas pré-PR formalizadas, coleta diária estável nas fontes principais.

**O que aprendi:** o gargalo do ecossistema não é coletar — é sustentar. Com 12 fontes, o trabalho real é pacing, retry, manifesto de proveniência e CI que detecta deriva antes do usuário. Por isso confiança vem antes de acesso: dado sem proveniência e sem status público não escala.

**Próximo mês:** o Devlog #02 vai fazer o deep-dive do pipeline SIDRA de ponta a ponta — do coletor aos pipelines declarativos, da carga em banco às tabelas no portal. Se a saga da resiliência contra bloqueios render novos aprendizados, eles entram lá.

---

## Nesta série

* **#01 — Visão geral do ecossistema e estado de setembro/2026** (este post)
* #02 — SIDRA de ponta a ponta: coletor, pipelines, banco e portal (planejado)
* #03 — Séries do Banco Central: da coleta às tabelas macro (planejado)

---

*Baseado em fontes públicas: documentação em docs.quantilica.com, releases no GitHub e pacotes no PyPI/índice Quantilica. Números de versão referem-se aos releases públicos de setembro/2026.*
