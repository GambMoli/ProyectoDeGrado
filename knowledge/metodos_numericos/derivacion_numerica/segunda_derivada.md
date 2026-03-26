# Segunda derivada numerica

## Metadata

- id: mn_derivacion_segunda_derivada
- course: metodos_numericos
- unit: derivacion_numerica
- topic: segunda_derivada
- subtopic: formulas_progresivas_regresivas_y_centrales
- content_type: concept_card
- difficulty: medio
- prerequisites: derivacion_numerica, serie_de_taylor
- tags: derivacion_numerica, segunda_derivada, diferencias_finitas, metodos_numericos
- source: corpus_seed_v2

## Learning goal

Entender como estimar la curvatura local de una funcion a partir de valores
discretos.

## Formal definition

La segunda derivada numerica se obtiene combinando valores vecinos de la funcion
con formulas progresivas, regresivas o centrales.

## Intuition

Mientras la primera derivada aproxima pendiente, la segunda describe como cambia
esa pendiente.

## Why it matters

Es util en problemas de concavidad, ecuaciones diferenciales y analisis de
datos discretos.

## Key formulas

- central: `f''(x_i) ~= (f(x_i+h) - 2f(x_i) + f(x_i-h)) / h^2`

## Step by step explanation

1. Identifica la posicion del punto.
2. Elige una formula compatible con los datos disponibles.
3. Sustituye valores tabulados.
4. Interpreta el signo y magnitud del resultado.

## Common mistakes

- Olvidar dividir por `h^2`.
- Reutilizar formulas de primera derivada.
- Ignorar sensibilidad al ruido experimental.

## Mini example

Con valores simetricos alrededor de `x_i`, la formula central de segunda
derivada suele dar una aproximacion estable.

## Related topics

- primera_derivada
- error_de_truncamiento
