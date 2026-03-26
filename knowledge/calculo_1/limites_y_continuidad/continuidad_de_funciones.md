# Continuidad de funciones

## Metadata

- id: calc1_limites_continuidad_de_funciones
- course: calculo_1
- unit: limites_y_continuidad
- topic: continuidad_de_funciones
- subtopic: criterio_de_continuidad
- content_type: concept_card
- difficulty: basico
- prerequisites: limites_de_una_funcion
- tags: continuidad, funciones, calculo_1
- source: corpus_seed_v4

## Learning goal

Entender cuando una funcion no presenta saltos, huecos o rupturas en un punto o
en un intervalo.

## Formal definition

Una funcion es continua en `a` si:

1. `f(a)` existe.
2. `lim x->a f(x)` existe.
3. `lim x->a f(x) = f(a)`.

## Intuition

Una funcion continua puede dibujarse localmente sin levantar el lapiz en el
entorno del punto considerado.

## Why it matters

La continuidad permite aplicar teoremas y garantiza buen comportamiento para
muchos procedimientos del calculo.

## Key formulas

- continuidad en `a`: existencia del valor y coincidencia con el limite

## Step by step explanation

1. Verifica si la funcion esta definida en el punto.
2. Calcula o estima el limite en el punto.
3. Compara el limite con el valor de la funcion.
4. Decide si hay continuidad o algun tipo de discontinuidad.

## Common mistakes

- Pensar que basta con que exista el valor de la funcion.
- Confundir discontinuidad removible con salto.
- No revisar ambos lados del punto.

## Mini example

Si `f(2)=4` y `lim x->2 f(x)=4`, entonces la funcion es continua en `2`.

## Related topics

- limites_de_una_funcion
- maximos_minimos_razones_de_cambio_y_optimizacion
