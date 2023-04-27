---
title: "Excel Deblocker: Remova a Proteção de Planilhas"
date: 2023-03-31T10:00:00-03:00
author: Komesu, D. K.
slug: excel-deblocker
tags: ["Microsoft Excel", "Python"]
---

Hoje, trago um script Python que remove a proteção de planilhas Excel com um único comando. Se você já precisou lidar com planilhas protegidas no Excel, sabe o quão frustrante pode ser tentar editá-las ou até mesmo visualizá-las. Mas com esse script Python, você pode remover a proteção em questão de segundos.

<!--more-->

Antes de apresentar o código, é importante ressaltar que remover a proteção de uma planilha sem a devida autorização é uma violação de privacidade e pode ser ilegal. Certifique-se de que você está autorizado a remover a proteção antes de usar o script.

Sem mais delongas, aqui está o código Python para remover a proteção de planilhas Excel:

<script src="https://gist.github.com/dankkom/2ad22aac736b0bdb8ce65653591bd930.js"></script>

Para remover a proteção de uma planilha Excel, basta executar o seguinte comando no terminal:

```sh
python excel_deblocker.py <caminho_do_arquivo_excel>
```

Substitua `<caminho_do_arquivo_excel>` pelo caminho completo do arquivo Excel protegido que você deseja desbloquear. Certifique-se de incluir a extensão `.xlsx`.
