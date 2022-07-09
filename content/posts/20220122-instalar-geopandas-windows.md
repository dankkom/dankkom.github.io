---
title: "PIP: Como instalar o GeoPandas no Windows (sem Conda)"
date: 2022-01-22
author: Komesu, D. K.
slug: instalar-geopandas-windows
aliases:
    - /instalar-geopandas-windows
tags: []
---

Como instalar o pacote GeoPandas no Windows sem usar o conda? Quando tentamos instalá-lo usando o PIP recebemos um erro. Muitas respostas no StackOverflow dizem para usar o Conda nesse caso. Porém, e quando não queremos usar o Conda, pois não queremos instalar outra versão gerenciador de pacotes no Windows?

<!--more-->

A resposta para isso é usar os "Unofficial Windows Binaries for Python Extension Packages" compilados por Christoph Gohlke da Universidade da Califórnia.

- [pacote GeoPandas](https://geopandas.org/)
- ["Unofficial Windows Binaries for Python Extension Packages" compilados por Christoph Gohlke da Universidade da Califórnia](https://www.lfd.uci.edu/~gohlke/pythonlibs/)

Para instalar o Geopandas no Windows vá à página com os binários e baixe os binários dos pacotes necessários, listados abaixo, observando as versões compatíveis.

- GDAL
- Fiona
- pyproj
- Rtree
- Shapely
- GeoPandas

Dê um `pip install <caminho/para/o/arquivo>` nos arquivos, na sequência listada.

Se tudo der certo, o GeoPandas estará instalado no Windows e disponível para importar no Python. 🙂

---

Links:

- [Unofficial Windows Binaries for Python Extension Packages](https://www.lfd.uci.edu/~gohlke/pythonlibs/)
- Perg[unta no StackOverflow: "pip install geopandas on windows"](https://stackoverflow.com/questions/56958421/pip-install-geopandas-on-windows)
