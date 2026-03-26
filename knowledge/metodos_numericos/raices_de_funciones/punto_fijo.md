# Punto fijo

## Metadata

- id: mn_raices_punto_fijo
- course: metodos_numericos
- unit: raices_de_funciones
- topic: punto_fijo
- subtopic: iteracion_gx
- content_type: concept_card
- difficulty: medio
- prerequisites: funciones, convergencia
- tags: punto_fijo, iteracion, raices, metodos_numericos
- source: corpus_seed_v2

## Learning goal

Entender como transformar una ecuacion `f(x)=0` en una iteracion del tipo
`x = g(x)` y estudiar si esa iteracion converge.

## Formal definition

Un punto fijo de `g` es un valor `x` tal que `g(x) = x`. El metodo itera:

- `x_(n+1) = g(x_n)`

## Intuition

La idea es construir una funcion que al aplicarse repetidamente acerque la
secuencia hacia un valor estable.

## Why it matters

Es una base conceptual para muchos metodos iterativos y ayuda a entender
criterios de convergencia.

## Key formulas

- `x_(n+1) = g(x_n)`

## Step by step explanation

1. Reescribe `f(x)=0` como `x = g(x)`.
2. Elige un valor inicial.
3. Itera `x_(n+1) = g(x_n)`.
4. Verifica si la secuencia se estabiliza.

## Common mistakes

- Elegir una transformacion `g(x)` que no converge.
- No verificar condiciones locales de convergencia.
- Confundir el metodo con interpolacion.

## Mini example

Si `x = cos(x)`, se puede iterar `x_(n+1) = cos(x_n)` para buscar un punto fijo.

## Related topics

- newton_raphson
- criterio_de_contraccion
