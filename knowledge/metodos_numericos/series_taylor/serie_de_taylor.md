# Serie de Taylor

## Metadata

- id: mn_series_taylor_serie_de_taylor
- course: metodos_numericos
- unit: series_taylor
- topic: serie_de_taylor
- subtopic: aproximacion_local
- content_type: concept_card
- difficulty: medio
- prerequisites: derivadas, polinomios
- tags: taylor, aproximacion_local, truncamiento, metodos_numericos
- source: corpus_seed_v2

## Learning goal

Entender como aproximar una funcion por medio de un polinomio construido desde
sus derivadas en un punto.

## Formal definition

La expansion de Taylor de `f(x)` alrededor de `a` es una suma de terminos
basados en las derivadas de `f` evaluadas en `a`.

## Intuition

Cerca del punto de expansion, una funcion suave puede parecerse mucho a un
polinomio. Cuantos mas terminos se usan, mejor suele ser la aproximacion local.

## Why it matters

Permite construir formulas numericas, estimar errores y aproximar funciones que
no son faciles de evaluar directamente.

## Key formulas

- `f(x) ~= f(a) + f'(a)(x-a) + f''(a)(x-a)^2 / 2! + ...`

## Step by step explanation

1. Elige el punto de expansion `a`.
2. Calcula derivadas sucesivas de la funcion.
3. Sustituye las derivadas en la formula.
4. Trunca la serie en el orden que necesites.
5. Estima el error de truncamiento.

## Common mistakes

- Usar la serie lejos del punto de expansion.
- Confundir la serie completa con el polinomio truncado.
- No considerar el error del termino restante.

## Mini example

Cerca de `x = 0`, `e^x` puede aproximarse por `1 + x + x^2/2`.

## Related topics

- error_de_truncamiento
- derivacion_numerica
