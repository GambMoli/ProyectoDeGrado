# Regula falsi

## Metadata

- id: mn_raices_regula_falsi
- course: metodos_numericos
- unit: raices_de_funciones
- topic: regula_falsi
- subtopic: interpolacion_lineal
- content_type: concept_card
- difficulty: medio
- prerequisites: biseccion, recta_secante
- tags: regula_falsi, falsa_posicion, raices, metodos_numericos
- source: corpus_seed_v2

## Learning goal

Entender como aproximar una raiz usando la interseccion de la recta secante con
el eje `x`, manteniendo un intervalo con cambio de signo.

## Formal definition

El metodo usa los extremos `a` y `b` para construir una recta secante y tomar
como aproximacion la abscisa donde esa recta corta el eje `x`.

## Intuition

En vez de cortar el intervalo por la mitad, se usa la forma local de la funcion
para proponer un punto mas informado.

## Why it matters

Suele ser mas rapido que biseccion cuando la funcion es casi lineal cerca de la
raiz, sin perder la idea de intervalo seguro.

## Key formulas

- `c = b - f(b)(b-a)/(f(b)-f(a))`

## Step by step explanation

1. Elige un intervalo con cambio de signo.
2. Calcula la interseccion de la secante con el eje `x`.
3. Evalua la funcion en el nuevo punto.
4. Conserva el subintervalo con cambio de signo.
5. Repite hasta la tolerancia deseada.

## Common mistakes

- No mantener el intervalo valido.
- Esperar convergencia rapida en funciones muy asimetricas.
- No distinguirlo del metodo de la secante libre.

## Mini example

Si `f(a)` y `f(b)` tienen signos opuestos, la falsa posicion usa la recta que
pasa por `(a, f(a))` y `(b, f(b))` para construir la nueva aproximacion.

## Related topics

- biseccion
- metodo_de_la_secante
