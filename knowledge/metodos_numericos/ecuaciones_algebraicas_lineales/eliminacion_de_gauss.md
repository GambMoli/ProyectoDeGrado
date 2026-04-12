# Eliminacion de Gauss

## Metadata

- id: mn_lineales_eliminacion_de_gauss
- course: metodos_numericos
- unit: ecuaciones_algebraicas_lineales
- topic: eliminacion_de_gauss
- subtopic: sistema_triangular_y_pivoteo
- content_type: concept_card
- difficulty: medio
- prerequisites: algebra_lineal_basica, sistemas_lineales
- tags: eliminacion_de_gauss, sistemas_lineales, pivoteo, matrices, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_9

## Learning goal

Entender como transformar un sistema lineal en uno triangular superior para
resolverlo de manera sistematica por sustitucion hacia atras.

## Formal definition

La eliminacion de Gauss aplica operaciones elementales por filas para anular los
coeficientes que quedan debajo de la diagonal principal de la matriz de
coeficientes. Una vez obtenida la forma triangular superior, las incognitas se
recuperan por sustitucion hacia atras.

## Intuition

Cada fila nueva elimina una variable de las ecuaciones inferiores. El sistema no
cambia de solucion, pero queda escrito en una forma mucho mas facil de resolver.

## Why it matters

Es uno de los algoritmos base del calculo cientifico. Tambien sirve como punto
de partida para pivoteo, factorizaciones y metodos mas avanzados para algebra
lineal numerica.

## Key formulas

- `[A]{x} = {b}`
- `m_ik = a_ik / a_kk`
- `fila_i <- fila_i - m_ik * fila_k`

## Step by step explanation

1. Escribe el sistema como matriz aumentada.
2. Usa la fila pivote para anular los elementos inferiores de una columna.
3. Repite el proceso columna por columna hasta formar una matriz triangular.
4. Resuelve la ultima ecuacion.
5. Sustituye hacia arriba hasta recuperar todas las variables.

## Common mistakes

- No intercambiar filas cuando el pivote es cero o muy pequeno.
- Redondear demasiado pronto durante la eliminacion.
- Olvidar que sin pivoteo parcial el metodo puede ser numericamente inestable.

## Mini example

Para un sistema `3x - 0.1y - 0.2z = 7.85`, `0.1x + 7y - 0.3z = -19.3`,
`0.3x - 0.2y + 10z = 71.4`, la eliminacion produce una forma triangular y
luego se despejan primero `z`, despues `y` y finalmente `x`.

## Related topics

- descomposicion_lu
- gauss_seidel
