# Simpson 1/3

## Metadata

- id: mn_integracion_simpson_un_tercio
- course: metodos_numericos
- unit: integracion_numerica
- topic: simpson_1_3
- subtopic: aproximacion_parabolica
- content_type: concept_card
- difficulty: medio
- prerequisites: integrales, interpolacion_cuadratica
- tags: simpson_1_3, integracion_numerica, cuadratica, metodos_numericos
- source: corpus_seed_v2

## Learning goal

Entender como aproximar una integral definida usando una parabola que interpola
tres puntos.

## Formal definition

La regla de Simpson 1/3 aproxima la integral en un intervalo usando un polinomio
de grado dos construido con los extremos y el punto medio.

## Intuition

En vez de aproximar la curva con una recta, se usa una parabola, lo que suele
mejorar la precision cuando la funcion es suave.

## Why it matters

Es una de las reglas compuestas mas usadas por su buen balance entre costo y
precision.

## Key formulas

- `integral_a^b f(x) dx ~= (h/3) [f(x0) + 4f(x1) + f(x2)]`

## Step by step explanation

1. Divide el intervalo en un numero par de subintervalos.
2. Calcula el paso `h`.
3. Evalua la funcion en nodos extremos e intermedios.
4. Aplica los pesos `1, 4, 2, 4, ..., 1` en la version compuesta.

## Common mistakes

- Usar un numero impar de subintervalos.
- Aplicar mal los pesos.
- Pensar que siempre supera a otros metodos aun con datos ruidosos.

## Mini example

Si solo tienes tres nodos igualmente espaciados, Simpson 1/3 usa el punto medio
con peso `4`.

## Related topics

- trapecios
- error_de_integracion
