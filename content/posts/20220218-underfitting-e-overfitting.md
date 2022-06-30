---
title: "Underfitting e Overfitting"
date: 2022-02-18
author: Komesu, D. K.
slug: underfitting-e-overfitting
tags: []
---

Underfitting e overfitting são problemas em machine learning supervisionado que podem aparecer nos modelos e está relacionado com o trade-off de viés e variância.

<!--more-->

- [trade-off de viés e variância](/posts/trade-off-vies-variancia/)

O **overfitting** é quando o modelo se ajusta demais aos dados de treinamento. Desse modo, o modelo "memoriza" os dados de treinamento e assim consegue minimizar o erro, fazendo parecer que tem uma performance melhor do que realmente tem. Ao tentarmos fazer previsões com dados diferentes o modelo erra muito mais. Quando isso ocorre, diz-se que o modelo não generaliza bem.

O **overfitting** ocorre quando o modelo tem **muitas variáveis**, ou seja, é **muito complexo** e não consegue fazer previsões e classificações com novos dados.

## Como identificar underfitting e overfitting?

Para identificar se o modelo está sofrendo com o problema de underfitting e overfitting é preciso olhar para suas métricas de desempenho. Para medir o desempenho do modelo é necessário fazer a [divisão dos dados em treino, validação e teste](/posts/treino-teste-validacao/) e validar as previsões com, por exemplo, a técnica de [validação cruzada](https://en.wikipedia.org/wiki/Cross-validation_(statistics)).

Alguns métodos recomendados para resolver o problema de overfitting são:

- [Early stopping](https://en.wikipedia.org/wiki/Early_stopping)
- Treinar com mais dados
- Feature selection
- Regularização
- Usar métodos ensemble

O **underfitting** é quando o modelo não consegue fazer boas previsões nem com os dados de treinamento. Nesse caso tentar incluir mais variáveis no modelo pode ajudar e, se for o caso, diminuir o nível de regularização. Também é válido treinar o modelo com uma base de dados maior, pois ruídos em conjuntos de dados pequenos podem estar prejudicando a aprendizagem do algoritmo.

<figure class="aligncenter size-full">
    <img src="https://images2.imgbox.com/a9/17/X9bOZXUM_o.png" alt=""/>
    <figcaption>Figura 1 - Exemplo de overfitting. Fonte: Wikipédia.</figcaption>
</figure>

Observe que na Figura 1 a linha verde separa perfeitamente os pontos vermelhos dos pontos azuis. Esse é um exemplo de overfitting, pois o algoritmo provavelmente não vai conseguir fazer essa separação perfeita com novos dados.

<figure class="alignwide size-full is-style-default">
    <img src="https://images2.imgbox.com/20/67/cDcK6ajL_o.png" alt=""/>
    <figcaption>Figura 2 - Exemplos de modelos com underfitting, overfitting e balanceado.</figcaption>
</figure>

Na Figura 2 temos três situações, o modelo com underfitting, o modelo balanceado (ideal) e o modelo com overfitting.

---

Links:

- [StackOverflow - O que é Overfitting e Underfitting em Machine Learning](https://pt.stackoverflow.com/questions/377643/o-que-%C3%A9-overfitting-e-underfitting-em-machine-learning)
- [AWS - Machine Learning - Ajuste do modelo: Subajuste versus sobreajuste](https://docs.aws.amazon.com/pt_br/machine-learning/latest/dg/model-fit-underfitting-vs-overfitting.html)
- [Wikipédia - Overfitting](https://en.wikipedia.org/wiki/Overfitting)
- [GeeksforGeeks - ML | Underfitting and Overfitting](https://www.geeksforgeeks.org/underfitting-and-overfitting-in-machine-learning/)
- [3 Dimensões - Overfitting e Underfitting](https://www.3dimensoes.com.br/post/overfitting-e-underfitting)
- [Didática Tech - Underfitting e Overfitting](https://didatica.tech/underfitting-e-overfitting/)
- [IBM Cloud Learn Hub - Underfitting](https://www.ibm.com/cloud/learn/underfitting)
- [IBM Cloud Learn Hub - Overfitting](https://www.ibm.com/cloud/learn/overfitting)
