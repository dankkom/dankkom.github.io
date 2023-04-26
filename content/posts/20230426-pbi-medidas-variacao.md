---
title: "Microsoft Power BI: Medidas de Variação em Séries Temporais"
date: 2023-04-26T16:00:00-03:00
author: Komesu, D. K.
slug: power-bi-medidas-variacao-series-temporais
tags: ["Microsoft Power BI", "BI"]
katex: true
---

Nesse post apresento duas medidas para relatórios em Power BI que calculam a variação percentual de séries temporais: uma para variação mensal (Month over Month - MoM) e outra para a variação de um período contra o mesmo período do ano anterior (Year over Year - YoY)

__É necessário ter uma tabela *Calendário* para as medidas funcionarem.__

## Variação percentual do mês atual contra mês imediatamente anterior (MoM)

```DAX
% MoM =
VAR ValorMesAtual = SUM('FATO'[valor])
VAR ValorMesAnterior = CALCULATE(SUM('FATO'[valor]), DATEADD('Calendário'[data], -1, MONTH))
RETURN
    IF(
        AND(ValorMesAtual <> 0, ValorMesAnterior <> 0),
        DIVIDE(ValorMesAtual, ValorMesAnterior) - 1,
        BLANK()
    )
```

Na fórmula da medida _MoM_, declaro duas _variáveis_:

- `ValorMesAtual`: é o valor da série no período atual para usar como numerador da divisão para calcular a variação percentual _MoM_.
- `ValorMesAnterior`: é o valor da série no período anterior, seja dia, mês ou ano. Para obter esse valor é preciso usar a função `CALCULATE` que opera sobre o _row context_, permitindo contornar os filtros aplicados no relatório. Para que o `CALCULATE` retorne o valor do período anterior foi usado a função `DATEADD`, usadas para somas de datas.

O retorno da medida é a divisão do `ValorMesAtual` sobre `ValorMesAnterior` subtraído de 1, ou seja:

$$MoM = \frac{ValorMesAtual}{ValorMesAnterior} - 1$$

Porém, caso `ValorMesAtual` e `ValorMesAnterior` sejam iguais a zero, a medida retorna _blank_.

## Variação percentual do período atual contra mesmo período do ano anterior (YoY)

```DAX
% YoY =
VAR ValorMesAtual = SUM('FATO'[valor])
VAR ValorMesAnoAnterior = CALCULATE(
    SUM('FATO'[valor]),
    SAMEPERIODLASTYEAR('Calendário'[data])
)
RETURN
    IF(
        AND(ValorMesAtual <> 0, ValorMesAnoAnterior <> 0),
        DIVIDE(ValorMesAtual, ValorMesAnoAnterior) - 1,
        BLANK()
    )
```

A fórmula da medida _YoY_ segue a mesma lógica da medida _MoM_, apenas diferenciando na função usada para o `CALCULATE` retornar o valor no mesmo período do ano anterior.

Nesse caso usou-se o `SAMEPERIODLASTYEAR` no campo de filtro do `CALCULATE` para a variável `ValorMesAnoAnterior`. O retorno da medida então é:

$$YoY = \frac{ValorMesAtual}{ValorMesAnoAnterior} - 1$$
