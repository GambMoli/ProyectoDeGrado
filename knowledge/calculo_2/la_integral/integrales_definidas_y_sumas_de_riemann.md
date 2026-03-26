# Integrales definidas y sumas de Riemann

## Metadata

- id: calc2_la_integral_integrales_definidas_riemann
- course: calculo_2
- unit: la_integral
- topic: integrales_definidas_y_sumas_de_riemann
- subtopic: acumulacion_y_area_neta
- content_type: concept_card
- difficulty: basico
- prerequisites: funciones, sumatorias
- tags: integrales_definidas, riemann, area_neta, calculo_2
- source: corpus_seed_v3

## Learning goal

Entender la integral definida como limite de sumas que acumulan valores de una
funcion en subintervalos pequenos.

## Formal definition

La integral definida de `f(x)` en `[a, b]` se interpreta como el limite de sumas
de Riemann cuando el ancho de los subintervalos tiende a cero.

## Intuition

Se parte el intervalo en muchas franjas pequenas, se calcula un rectangulo en
cada franja y se suma el aporte total. Mientras mas fina la particion, mejor la
aproximacion.

## Why it matters

Permite interpretar la integral como acumulacion, area neta y fundamento de
varias aplicaciones fisicas y geometricas.

## Key formulas

- `integral_a^b f(x) dx = lim sum f(x_i^*) Delta x`

## Step by step explanation

1. Divide el intervalo `[a, b]` en partes pequenas.
2. Elige un punto de muestreo en cada subintervalo.
3. Multiplica el valor de la funcion por el ancho.
4. Suma todos los productos.
5. Lleva la particion al limite.

## Common mistakes

- Confundir area geometrica con area neta.
- Pensar que la integral definida siempre es positiva.
- No distinguir una aproximacion de Riemann de la integral exacta.

## Mini example

Para `f(x) = x` en `[0,1]`, una suma de Riemann aproxima el area bajo la recta
y converge a `1/2`.

## Related topics

- teorema_fundamental_del_calculo
- integracion_numerica
