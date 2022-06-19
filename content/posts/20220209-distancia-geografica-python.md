---
title: "Como calcular distâncias geográficas entre duas coordenadas em Python"
date: 2022-02-09
author: Komesu, D. K.
slug: distancia-geografica-python
tags: []
---

Em análises geoespaciais, uma das tarefas mais frequentes é medir a distância entre duas coordenadas geográficas. Em Python é possível obter essa distância facilmente usando o pacote `geopy` e seu módulo `distance`.

O pacote `geopy` é um cliente Python para trabalhar vários serviços web de geocodificação populares e inclui o módulo `distance` que tem funções para calcular distâncias geográficas.

Para instalar o pacote use o comando:

```sh
pip install geopy
```

Então, para calcular a distância geográfica entre dois pontos é preciso ter as coordenadas desses pontos. O código a seguir, por exemplo, para calcular a distância em quilômetros entre [São Paulo (23.550278, -46.633889)](https://geohack.toolforge.org/geohack.php?pagename=S%C3%A3o_Paulo¶ms=23_33_01_S_46_38_02_W_type:city_region:BR) e [Rio de Janeiro (22.902778, -43.207778)](https://geohack.toolforge.org/geohack.php?pagename=Rio_de_Janeiro¶ms=22_54_10_S_43_12_28_W_type:city_region:BR):

```python
from geopy import distance
distance.distance((23.550278, -46.633889), (22.902778, -43.207778)).km
# 357.9108359775276
```

A distância entre São Paulo e Rio de Janeiro é de 358 quilômetros, segundo o `geopy`.

Para obter a distância em metros é só acessar o atributo `m` ao invés do `km`.

---

Links:

- [GeoPy - módulo distance](https://geopy.readthedocs.io/en/stable/#module-geopy.distance)
