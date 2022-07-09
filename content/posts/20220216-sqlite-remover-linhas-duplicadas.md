---
title: "SQLite: como remover linhas duplicadas"
date: 2022-02-16
author: Komesu, D. K.
slug: sqlite-remover-linhas-duplicadas
aliases:
    - /sqlite-remover-linhas-duplicadas
tags: []
---

Quando o DBA (ou seja, nós mesmos) não coloca uma constraint (restrição) de valores únicos numa tabela, pode ser que sejam inseridas linhas com valores duplicados. Não dá para colocar um constraint nessa tabela depois que temos linhas duplicadas. É preciso remover essas linhas.

<!--more-->

Para remover linhas duplicadas no SQLite use um comando como o seguinte:

```sql
DELETE FROM database
WHERE rowid NOT IN (
  SELECT MIN(rowid)
  FROM database
  GROUP BY column1, column2
);
```

O SQLite tem uma coluna especial chamada `ROWID` que identifica unicamente cada linha numa tabela.

O que o código faz é:

- Agrupa-se a tabela pelas colunas `column1` e `column2` aplicando a função `MIN()` sobre a coluna `ROWID`;
- Então o comando `DELETE` apaga as linhas com `ROWIDs` que não estão contidas nessa consulta, ou seja, removemos tudo exceto os `ROWIDs` mínimos para cada valor único agrupado pelas colunas `column1` e `column2`.

---

Links:

- [SQLite - CREATE TABLE](https://www.sqlite.org/lang_createtable.html#rowid)
- [StackOverflow - how can I delete duplicates in SQLite?](https://stackoverflow.com/a/25885564)
