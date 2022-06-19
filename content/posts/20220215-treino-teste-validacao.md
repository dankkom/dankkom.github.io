---
title: "Divisão de dados em Treino, Validação e Teste para Machine Learning"
date: 2022-02-15
author: Komesu, D. K.
slug: treino-teste-validacao
tags: []
---

A divisão de datasets em treino, teste e validação é um procedimento em *data science*, mais especificamente [machine learning supervisionado](https://dkko.me/aprendizado-supervisionado-vs-nao-supervisionado/), que divide o conjunto de dados (*dataset*) em três subconjuntos para permitir a medição da performance de algoritmos de previsão e classificação.

Em modelos de aprendizado supervisionado é de suma importância mensurar o erro e a precisão das previsões para que o modelo se ajuste de acordo. Mais importante ainda é que as previsões sejam não-viesadas, ou seja, que o modelo  performe bem em dados diferentes daqueles usados na etapa do treino.

A divisão dos dados em treino, validação e teste é importante também para detectar se o modelo sofre com problema de undeffiting ou overfitting.

<h2 id="para-que-serve-cada-dataset">Para quê serve cada dataset?</h2>

- **Treino**: esse dataset é usado para o treino, ou seja, o **fit** do modelo. Por exemplo, numa regressão os parâmetros são ajustados para minimizar o erro nesse dataset.
- **Validação**: esse dataset é usado para a avaliação não-viesada da performance do modelo durante o ajuste de hiperparâmetros.
- **Teste**: esse dataset é usado para a avaliação final do modelo. Não deve ser usado durante o treino e a validação.

Existem vários métodos de fazer a divisão do conjunto de dados em treino, validação e teste. O mais simples é pegar um percentual dos dados como estão e determinar qual conjunto é o quê.

Outras técnicas mais avançadas levam em conta o componente temporal (séries temporais), o componente espacial, componentes de agrupamento, entre outras características.

---

Link:

- [Real Python: Split Your Dataset With scikit-learn's train_test_split()](https://realpython.com/train-test-split-python-data/)
- [Towards Data Science: How to split data into three sets (train, validation, and test) And why?](https://towardsdatascience.com/how-to-split-data-into-three-sets-train-validation-and-test-and-why-e50d22d3e54c)
