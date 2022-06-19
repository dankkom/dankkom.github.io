---
title: "Restaurar arquivos configuração de pacotes no Linux Debian com APT"
date: 2022-01-03
author: Komesu, D. K.
slug: restaurar-arquivos-configuracao-pacotes-linux-debian-apt
tags: []
---

Esse texto é para quem apagou algum arquivo de configuração (🤦‍♀️) que foi criado por algum pacote instalado no Linux e agora precisa restaurá-lo. Não, simplesmente usar o APT para reinstalar o pacote com `sudo apt install --reinstall <nome-do-pacote>` não restaura os arquivos de configuração 😢 — eu já tentei isso.

<!--more-->

O ponto principal está no comando `apt purge`. Depois de horas procurando a solução específica para esse problema finalmente encontrei a sequência de comandos que funciona. No caso eu estava tentando instalar o [transmission-daemon no Raspberry Pi](https://pimylifeup.com/raspberry-pi-transmission/).

#### 1. Remova o pacote e suas dependências

Primeiro, para uma instalação limpa, remova o pacote e suas dependências com o seguinte comando:

```sh
sudo apt remove <package-name>
sudo apt autoremove
```

#### 2. Purge

Esse é ponto importante para o APT reinstalar os arquivos de configuração. A diferença entre o `apt remove` e o `apt purge` é que o último [apaga os arquivos de configuração deixados pelo pacote](https://askubuntu.com/a/231568).

```sh
sudo apt purge <package-name>
```

#### 3. Reinstale o pacote

Por último, instale novamente o pacote. Agora, depois do `apt purge` os arquivos de configuração serão reinstalados.

```sh
sudo apt install <package-name>
```

---

Referências:

- [How to reset Network Manager to default?](https://askubuntu.com/a/637739)
- [Resposta no Unix StackExchange: Restore /etc/ configuration files from the default](https://unix.stackexchange.com/a/27777)
- [Ubuntu manpage: apt-get](https://manpages.ubuntu.com/manpages/bionic/man8/apt-get.8.html)
