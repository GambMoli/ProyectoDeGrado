# Interpolacion de Newton

## Metadata

- id: mn_interpolacion_newton
- course: metodos_numericos
- unit: interpolacion
- topic: newton
- subtopic: diferencias_divididas
- content_type: concept_card
- difficulty: medio
- prerequisites: polinomios, interpolacion
- tags: interpolacion, newton, diferencias_divididas, metodos_numericos
- source: corpus_seed_v2

## Learning goal

Entender como construir el polinomio interpolante de manera incremental usando
diferencias divididas.

## Formal definition

La forma de Newton del polinomio interpolante usa coeficientes obtenidos por
diferencias divididas y factores acumulados del tipo `(x - x_i)`.

## Intuition

Es una forma eficiente de agregar nodos nuevos sin recomputar todo el polinomio
desde cero.

## Why it matters

Es util computacionalmente y permite actualizar la interpolacion de forma
progresiva.

## Key formulas

- `P_n(x) = a_0 + a_1(x-x_0) + a_2(x-x_0)(x-x_1) + ...`

## Step by step explanation

1. Ordena los nodos.
2. Calcula la tabla de diferencias divididas.
3. Extrae los coeficientes principales.
4. Construye el polinomio en forma de Newton.

## Common mistakes

- Llenar mal la tabla de diferencias divididas.
- Cambiar el orden de nodos sin actualizar la tabla.
- Confundir diferencias divididas con diferencias finitas.

## Mini example

Con tres puntos, la forma de Newton produce un polinomio cuadratico que puede
ampliarse facilmente si se agrega un cuarto nodo.

## Related topics

- lagrange
- diferencias_divididas
