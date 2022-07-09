---
title: "Como copiar chaves SSH do Windows para o WSL"
date: 2022-01-08
author: Komesu, D. K.
slug: copiar-chaves-ssh-wsl
aliases:
    - /copiar-chaves-ssh-wsl
tags: []
---

A introdução do Windows Subsystem for Linux (WSL) foi uma grande novidade da Microsoft para quem trabalha com código. Com essa camada de compatibilidade é possível executar várias coisas de Linux sem sair do Windows. No entanto, para trabalhar com repositórios *git* remoto é preciso configurar as chaves SSH dentro da distribuição Linux no WSL. Ao invés de gerar um par de chaves próprio para o WSL, é mais prático compartilhar as chaves já configuradas no Windows.

<!--more-->

- [Windows Subsystem for Linux (WSL)](https://en.wikipedia.org/wiki/Windows_Subsystem_for_Linux)
- [chaves SSH](https://en.wikipedia.org/wiki/Secure_Shell)

#### 1. Copiar as chaves SSH no Windows

Presumindo que [as chaves SSH já foram geradas no Windows](https://interworks.com/blog/2021/09/15/setting-up-ssh-agent-in-windows-for-passwordless-git-authentication/), execute o seguinte comando no Linux para copiar essas chaves para o WSL.

```sh
cp -r /mnt/c/Users/<username>/.ssh ~/.ssh
```

#### 2. Corrigir permissões dos arquivos

Antes de dar push para algum repositório remoto é preciso corrigir as permissões dos arquivos copiados no WSL. Execute a seguinte linha para configurar o acesso a leitura e escrita para o proprietário apenas.

```sh
chmod 600 ~/.ssh/id_rsa
```

Fonte: [Windows Command Line](https://devblogs.microsoft.com/commandline/sharing-ssh-keys-between-windows-and-wsl-2/)
