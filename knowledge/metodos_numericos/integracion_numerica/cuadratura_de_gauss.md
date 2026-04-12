# Cuadratura de Gauss

## Metadata

- id: mn_integracion_cuadratura_de_gauss
- course: metodos_numericos
- unit: integracion_numerica
- topic: cuadratura_de_gauss
- subtopic: nodos_y_pesos_optimos
- content_type: concept_card
- difficulty: medio
- prerequisites: integrales_definidas, trapecios
- tags: cuadratura_de_gauss, integracion_numerica, nodos, pesos, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_22

## Learning goal

Comprender por que elegir nodos y pesos optimos puede superar a las formulas de
Newton-Cotes con el mismo numero de evaluaciones.

## Formal definition

La cuadratura de Gauss aproxima una integral como una suma ponderada de valores
de la funcion evaluados en nodos interiores especialmente elegidos para maximizar
la exactitud algebraica.

## Intuition

No todos los puntos del intervalo aportan igual. Si eliges bien donde evaluar y
cuanto pesa cada evaluacion, obtienes mas precision con menos trabajo.

## Why it matters

Es una de las tecnicas mas eficientes para integrar funciones suaves cuando se
puede evaluar la funcion directamente y se busca alta exactitud.

## Key formulas

- `integral_(-1)^1 f(x) dx ~= sum(w_i f(x_i))`
- `x = ((b - a) xi + (b + a)) / 2`
- `integral_a^b f(x) dx ~= ((b - a)/2) sum(w_i f(x_i))`

## Step by step explanation

1. Lleva el intervalo ` [a, b] ` a `[-1, 1]` si hace falta.
2. Selecciona los nodos `x_i` y pesos `w_i` de la regla elegida.
3. Evalua la funcion en esos nodos.
4. Multiplica por los pesos y suma.
5. Reescala el resultado si la integral original no estaba en `[-1, 1]`.

## Common mistakes

- Usar nodos de Gauss en el intervalo original sin transformarlos.
- Confundir pesos con espaciados uniformes.
- Aplicarlo sin cuidado en funciones con singularidades o comportamiento no suave.

## Mini example

Una regla de Gauss-Legendre de pocos puntos puede integrar exactamente muchos
polinomios de grado mayor que una regla de Newton-Cotes con igual numero de
evaluaciones.

## Related topics

- integracion_de_romberg
- simpson_1_3
