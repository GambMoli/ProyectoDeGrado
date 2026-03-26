# Regla del trapecio

## Metadata

- id: mn_integracion_trapecios
- course: metodos_numericos
- unit: integracion_numerica
- topic: trapecios
- subtopic: aproximacion_lineal
- content_type: concept_card
- difficulty: basico
- prerequisites: integrales_definidas
- tags: trapecios, integracion_numerica, lineal, metodos_numericos
- source: corpus_seed_v2

## Learning goal

Entender como aproximar el area bajo una curva usando segmentos rectos.

## Formal definition

La regla del trapecio reemplaza la curva por una recta entre nodos consecutivos
y suma las areas de los trapecios formados.

## Intuition

Es la version mas simple de integracion numerica cuando la funcion se conoce en
pocos puntos o se requiere una aproximacion rapida.

## Why it matters

Es facil de implementar, robusta y sirve como base para formulas compuestas.

## Key formulas

- `integral_a^b f(x) dx ~= (h/2) [f(x0) + 2f(x1) + ... + 2f(xn-1) + f(xn)]`

## Step by step explanation

1. Divide el intervalo en subintervalos.
2. Evalua la funcion en cada nodo.
3. Multiplica extremos por `1` e interiores por `2`.
4. Multiplica la suma final por `h/2`.

## Common mistakes

- Olvidar duplicar los puntos interiores en la formula compuesta.
- Usar un `h` incorrecto.
- Esperar alta precision en curvas muy curvadas con pocos nodos.

## Mini example

Con dos puntos extremos, la regla del trapecio equivale a calcular el area del
trapecio bajo la recta secante.

## Related topics

- simpson_1_3
- error_de_integracion
