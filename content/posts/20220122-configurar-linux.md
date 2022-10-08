---
title: "Checklist para configurar um servidor Linux seguro"
date: 2022-01-22
author: Komesu, D. K.
slug: configurar-linux
aliases:
    - /configurar-linux
tags: []
---

Este post é checklist a seguir ao configurar um servidor Linux recém instalado. Numa instalação nova do Linux em um servidor é preciso configurar algumas coisas para se certificar que o sistema está seguro e atualizado.

<!--more-->

Para acessar um servidor Linux, o padrão é usar o SSH com o comando:

```sh
ssh root@<endereco-do-servidor>
```

### 1. Criar usuário

Em sistemas Linux recém instalados o usuário inicial, geralmente, é o root. É recomendado criar um usuário próprio. Para isso execute o comando:

```sh
useradd <nome-do-usuario>
```

Após executar o comando insira uma senha para o novo usuário.

#### Concedendo privilégios administrativos

Após criar seu próprio usuário é preciso adicioná-lo ao grupo *sudo* para podermos executar algumas tarefas administrativas no sistema usando o comando *sudo*. Execute o seguinte comando para adicionar o usuário criado ao grupo *sudo*:

```sh
usermod -aG sudo <nome-do-usuario>
```

Após criar o seu próprio usuário já podemos desconectar do servidor pelo usuário root e conectar pelo nosso usuário e senha usando SSH.

### 2. Chave SSH

Para reforçar a segurança do servidor e maior conveniência ao conectar pelo SSH podemos usar chaves SSH. Com isso não será preciso digitar nenhuma senha para nos conectarmos.

No Windows 10, para criar uma chave SSH, bastar rodar o seguinte comando:

```sh
ssh-keygen -t ed25519
```

Nesse comando, o `-t ed25519` especifica o algoritmo de criptografia da chave que queremos criar, nesse caso [Ed25519](https://www.cryptopp.com/wiki/Ed25519). O programa vai perguntar onde deseja salvar as chaves pública e privada. Pode deixar no local padrão apertando `Enter`. Também vai perguntar por uma senha. Geralmente, deixe em branco em máquinas na qual somente você tenha acesso.

Pronto! O par de chaves SSH está criado. Agora temos que copiar a chave pública no servidor Linux para que ele aceite a conexão usando a correspondente chave privada.

Para copiar a chave pública no servidor basta usar o comando `scp`.

No Windows, através do Powershell, o comando é:

```sh
scp $env:USERPROFILE/.ssh/id_ed25519.pub <nomedousuario>@<enderecodoservidor>:~/.ssh/authorized_keys
```

No Linux o comando é:

```sh
scp ~/.ssh/id_ed25519.pub <nomedousuario>@<enderecodoservidor>:~/.ssh/authorized_keys
```

### 3. Desabilitar acesso root e acesso por senha

Após criar um usuário próprio e configurar uma chave SSH é mais do que recomendado desabilitar o acesso pelo usuário root e desabilitar o acesso por senha. Para fazer isso edite o arquivo `/etc/ssh/sshd_config` com algum editor de texto (vim, nano, emacs).

```sh
sudo nano /etc/ssh/sshd_config
```

Para desabilitar acesso root troque  `PermitLoginRoot yes` por `PermitLoginRoot no`

Para desabilitar acesso por senha substitua ``PasswordAuthentication` yes` por ` PasswordAuthentication no`

Após salvar o arquivo de configuração editado é preciso reiniciar o *daemon*:

```sh
sudo systemctl restart sshd
```

### 4. Firewall

O Uncomplicated Firewall (UFW) é uma interface simplificada do iptables para configurar um firewall para permitir e bloquear tráfego de rede em sistemas Linux. Para instalar use o APT:

```sh
sudo apt install ufw
```

Para listar as portas abertas no Linux use o comando:

```sh
sudo ss -tupln
```

Para permitir ou bloquear tráfego pelo número da porta use o comando:

```sh
sudo ufw allow <numero-da-porta>  # permite
sudo ufw deny <numero-da-porta>   # bloqueia
```

É possível especificar o nome do serviço, ao invés do número da porta, para permitir ou bloquear o tráfego. Para listar os serviços disponíveis:

```sh
sudo ufw app list
```

Então, para permitir ou bloquear acesso pelo nome do serviço:

```sh
sudo ufw allow <nome-do-aplicativo>  # permite acesso
sudo ufw deny <nome-do-aplicativo>   # bloqueia acesso
```

Após definir as regras de permissão e bloqueio de tráfego é preciso habilitar o UFW:

```sh
sudo ufw enable
```

Depois disso, sempre que você fizer alguma mudança nas regras do IFW será preciso recarregar com o comando:

```sh
sudo ufw reload
```

---

Referências:

<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/ZhMw53Ud2tY" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

- [DigitalOcean - "Initial Server Setup with Ubuntu 20.04"](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-20-04)
- UFW ([1](https://help.ubuntu.com/community/UFW), [2](https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-with-ufw-on-ubuntu-20-04), [3](https://www.devmedia.com.br/ufw-firewall-do-ubuntu/18317))
