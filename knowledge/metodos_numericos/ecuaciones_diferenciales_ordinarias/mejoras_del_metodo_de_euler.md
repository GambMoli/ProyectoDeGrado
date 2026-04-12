# Mejoras del metodo de Euler

## Metadata

- id: mn_edo_mejoras_del_metodo_de_euler
- course: metodos_numericos
- unit: ecuaciones_diferenciales_ordinarias
- topic: mejoras_del_metodo_de_euler
- subtopic: heun_y_punto_medio
- content_type: concept_card
- difficulty: medio
- tags: heun, punto_medio, euler_mejorado, edo, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_25

## Learning goal

Entender mejoras del metodo de euler y reconocer cuando conviene usarlo dentro del bloque de ecuaciones diferenciales ordinarias.

## Formal definition

Las mejoras del metodo de Euler, como Heun y el punto medio, usan pendientes adicionales dentro del paso para reducir el error local respecto del esquema basico.

## Intuition

En vez de usar solo la pendiente al inicio, Heun promedia una pendiente inicial y otra al final estimado del paso.

## Why it matters

Este bloque modela cambios dinamicos paso a paso y es central en simulacion cientifica e ingenieril.

## Mini example

En vez de usar solo la pendiente al inicio, Heun promedia una pendiente inicial y otra al final estimado del paso.

## Related topics

- metodo_de_euler
- metodos_de_runge_kutta
