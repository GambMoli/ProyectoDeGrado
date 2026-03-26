# Interpolacion de Lagrange

## Metadata

- id: mn_interpolacion_lagrange
- course: metodos_numericos
- unit: interpolacion
- topic: lagrange
- subtopic: polinomio_interpolante
- content_type: concept_card
- difficulty: medio
- prerequisites: polinomios, funciones
- tags: interpolacion, lagrange, polinomio, metodos_numericos
- source: corpus_seed_v2

## Learning goal

Entender como construir un polinomio que pase exactamente por un conjunto de
datos dados.

## Formal definition

La interpolacion de Lagrange expresa el polinomio interpolante como suma de
bases que valen `1` en un nodo y `0` en los demas.

## Intuition

Cada base de Lagrange actua como un interruptor que activa solo el valor de un
nodo y anula el resto.

## Why it matters

Permite aproximar funciones y reconstruir curvas a partir de datos discretos.

## Key formulas

- `P(x) = sum y_i L_i(x)`

## Step by step explanation

1. Toma los nodos `(x_i, y_i)`.
2. Construye cada base `L_i(x)`.
3. Multiplica cada base por su valor `y_i`.
4. Suma todos los terminos.

## Common mistakes

- Repetir nodos `x_i`.
- Confundir interpolacion con ajuste por minimos cuadrados.
- Usar demasiados puntos sin controlar oscilaciones.

## Mini example

Con dos puntos, la interpolacion de Lagrange produce simplemente la recta que
pasa por ambos.

## Related topics

- interpolacion_de_newton
- error_de_interpolacion
