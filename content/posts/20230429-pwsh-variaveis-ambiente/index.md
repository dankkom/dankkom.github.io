---
title: "Definindo variáveis de ambiente no Windows com PowerShell"
date: 2023-04-29T14:00:00-03:00
author: Komesu, D. K.
slug: pwsh-variaveis-ambiente-windows
aliases:
    - /posts/20230429-pwsh-variaveis-ambiente/index.html
tags: ["Microsoft Windows", "Powershell", "SysAdmin"]
---

Neste post mostro como definir uma variável de ambiente no Windows usando o PowerShell.

<!--more-->

Se você já trabalhou com desenvolvimento de software no Windows, provavelmente já precisou configurar variáveis de ambiente. Essas variáveis são importantes para que os programas e aplicativos possam acessar recursos do sistema e bibliotecas externas. No entanto, configurar essas variáveis manualmente pode ser uma tarefa tediosa e propensa a erros. Felizmente, o [PowerShell](https://en.wikipedia.org/wiki/PowerShell), a ferramenta de linha de comando da Microsoft, oferece uma maneira rápida e fácil de definir variáveis de ambiente no Windows. Neste post, vou mostrar passo a passo como fazer isso usando o PowerShell.

## Definição temporária

Para definir uma variável de ambiente temporária, válida apenas na sessão atual, digite no PowerShell:

```powershell
$Env:VARIAVEL = "valor"
```

## Definição "permanente"

Para definir uma variável de ambiente permanente, existem dois caminhos a seguir: definindo-a no arquivo de perfil do PowerShell ou definindo-a no sistema operacional.

### Arquivo de perfil do PowerShell

O primeiro caminho é definindo-a no [arquivo de perfil do PowerShell do usuário](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles), de modo semelhante como ocorre no Bash e ZSH no Linux. Para isso, edite o arquivo apontado na variável `$PROFILE`. Essa é uma variável automática que aponta para seu perfil de usuário para todos os hosts PowerShell. Por exemplo, usando o [Neovim](https://neovim.io):

```powershell
nvim $PROFILE
```

E então coloque a definição das variáveis de ambiente no arquivo:

```powershell
$Env:VARIAVEL1 = "valor1"
$Env:VARIAVEL2 = "valor2"
$Env:VARIAVEL3 = "valor3"
```

### Variáveis de ambiente no Windows

Para definir uma variável de ambiente de sistema, digite:

```powershell
[Environment]::SetEnvironmentVariable("VARIAVEL", "valor", "Machine")
```

Substitua `VARIAVEL` pelo nome da variável de ambiente e `valor` pelo valor que você quer atribuir a ela.

Para definir uma variável de ambiente de usuário, digite:

```powershell
[Environment]::SetEnvironmentVariable("VARIAVEL", "valor", "User")
```

Do mesmo modo anterior, substitua `VARIAVEL` pelo nome da variável de ambiente e `valor` pelo valor que você quer atribuir a ela.

---

Links e Referências:

- [Setting Windows PowerShell environment variables](https://stackoverflow.com/q/714877)
- [PowerShell Documentation](https://learn.microsoft.com/en-us/powershell/)
