---
title: "Cron Jobs no Linux: como automatizar a execução de scripts"
date: 2021-12-23
author: Komesu, D. K.
slug: cron-jobs-linux-automatizar-scripts
aliases:
    - /cron-jobs-linux-automatizar-scripts
tags: ["Linux", "SysAdmin"]
---

Eu sou a favor da automação no trabalho. Quanto menos trabalho repetitivo ocupa o tempo do funcionário, melhor, tanto para o funcionário quanto para a empresa. Uma das ferramentas que ajudam a diminuir as tarefas repetitivas é o *cron* do Linux.

<!--more-->

### O que é

O *cron* é um agendador de tarefas (*job scheduler*) nos sistemas Unix-like ([Wikipedia](https://en.wikipedia.org/wiki/Cron)). É um serviço que executa comandos (*jobs*) na hora determinada de acordo com uma tabela (*crontab*). As tarefas podem ser agendadas para ser executadas apenas uma vez ou podem ser tarefas recorrentes — executadas periodicamente num intervalo de tempo.

### Sintaxe

O *crontab* é um arquivo texto descrevendo os comandos a serem executados pelo *cron* e quando esses comandos serão executados.

Para editar o *crontab* basta rodar o comando `crontab -e`

A sintaxe do cronta se o formato a seguir:

```
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of the month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday to Saturday;
# │ │ │ │ │                                   7 is also Sunday on some systems)
# │ │ │ │ │
# │ │ │ │ │
# * * * * * <command to execute>
```

#### Exemplos

Para executar um comando todos os dias às 9 horas da manhã:

```sh
0 9 * * * <comando>
```

Para executar um comando a cada hora no dia 10 de cada mês:

```sh
0 * 10 * * <comando>
```

Para executar um comando a cada 5 minutos:

```sh
*/5 * * * * <comando>
```

Para executar um comando todo sábado e domingo às 15 horas e 10 minutos nos meses de janeiro, fevereiro e março:

```sh
10 15 * 1,2,3 0,6 <comando>
```

O site [Crontab.guru](https://crontab.guru/) é de grande ajuda na elaboração dessas expressões do *crontab*.

### Variáveis de ambiente (*environment variables*)

Quando criamos *cron jobs* é preciso atentar-se às variáveis de ambiente que a tarefa precisa para rodar. Por padrão os *cron jobs* não têm acesso às variáveis de ambiente do terminal e isso pode ser a fonte de erros nas tarefas agendadas.

Para adicionar as variáveis de ambiente nas *cron jobs* é preciso colocá-las no arquivo *crontab*. Por exemplo, coloque essa linha antes das descrições de tarefas no *crontab*:

```
PATH=/usr/local/bin:/bin
```

Assim, os scripts terão acesso aos executáveis localizados em `/usr/local/bin` e `/bin`

### Script executável

Para que o *cron* execute um script é preciso que o script seja executável. Para isso, basta rodar o comando `chmod +x script.sh` no terminal.

### Logs dos *Cron Jobs*

Para ver os registros das tarefas executadas pelo cron podemos usar o seguinte comando:

```sh
grep CRON /var/log/syslog
```

Esse comando `grep` vai pegar todas as linhas no arquivo `/var/log/syslog` que contém o termo `CRON`.
