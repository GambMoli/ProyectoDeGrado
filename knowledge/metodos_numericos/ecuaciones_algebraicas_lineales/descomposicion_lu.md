# Descomposicion LU

## Metadata

- id: mn_lineales_descomposicion_lu
- course: metodos_numericos
- unit: ecuaciones_algebraicas_lineales
- topic: descomposicion_lu
- subtopic: factorizacion_matricial
- content_type: concept_card
- difficulty: medio
- prerequisites: algebra_lineal_basica, eliminacion_de_gauss
- tags: descomposicion_lu, matrices, factorizacion, sistemas_lineales, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_10

## Learning goal

Comprender como factorizar una matriz en componentes triangulares para resolver
sistemas lineales con mayor eficiencia.

## Formal definition

La descomposicion LU escribe la matriz de coeficientes como el producto de una
matriz triangular inferior `L` y una matriz triangular superior `U`, de modo que
`[A] = [L][U]`.

## Intuition

En vez de repetir toda la eliminacion para cada nuevo vector del lado derecho,
se hace una sola factorizacion y luego se resuelven dos sistemas triangulares
mucho mas baratos.

## Why it matters

Es especialmente util cuando la misma matriz `A` se usa con varios vectores
`b`. Tambien facilita calcular la inversa y analizar la condicion del sistema.

## Key formulas

- `[A] = [L][U]`
- `[L]{d} = {b}`
- `[U]{x} = {d}`

## Step by step explanation

1. Factoriza la matriz `A` en `L` y `U`.
2. Resuelve primero el sistema inferior `L d = b`.
3. Usa el resultado intermedio `d`.
4. Resuelve despues el sistema superior `U x = d`.
5. Reutiliza la misma factorizacion si cambia `b`.

## Common mistakes

- Pensar que siempre evita por completo el pivoteo.
- No distinguir entre la fase de factorizacion y la fase de sustitucion.
- Aplicarlo sin revisar si la matriz requiere reordenamiento para estabilidad.

## Mini example

Si varios problemas comparten la misma matriz de coeficientes pero cambian los
terminos independientes, la factorizacion `LU` permite resolver todos con menos
trabajo que repetir Gauss desde cero.

## Related topics

- eliminacion_de_gauss
- gauss_seidel
