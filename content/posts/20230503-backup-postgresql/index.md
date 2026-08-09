---
title: "Script Python para fazer backups (dumps) de bases de dados em PostgreSQL"
date: 2023-05-03T22:45:00-03:00
author: Komesu, D. K.
slug: script-backup-postgresql
tags: [
    "Base de Dados",
    "Backup",
    "SysAdmin",
    "Python",
    "Dados",
    "Data Hoarder"
]
---

Neste post apresento um script Python que uso para fazer backups de bases de dados PostgreSQL.

<!--more-->

Para usar o script é necessário ter instalado, além do Python, o 7zip para comprimir os backups.

Sem mais delongas, segue o script para fazer um dump SQL (backup) de uma base de dados PostgreSQL.

<script src="https://gist.github.com/dankkom/876fc77f4e3939cc743920d637d7a7d7.js"></script>

O script pede três argumentos obrigatórios: `-U` (ou `--user`) para o usuário da base de dados, `-d` (ou `--database`) para o nome da base de dados que será feito o backup e `-dest-dir` para o diretório de destino onde será salvo o arquivo de backup.

O argumento opcional `--remove-uncompressed-sql` apaga o arquivo .SQL não comprimido. Geralmente é de bom senso apagar esse arquivo, pois pode ocupar espaço considerável no computador.

O arquivo de backup será um arquivo .SQL comprimido pelo 7zip, no nível de compressão máximo ("-mx=9").

É isso! Até mais! 👋
