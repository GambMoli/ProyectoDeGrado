# Metodos de pasos multiples

## Metadata

- id: mn_edo_metodos_de_pasos_multiples
- course: metodos_numericos
- unit: ecuaciones_diferenciales_ordinarias
- topic: metodos_de_pasos_multiples
- subtopic: uso_de_historial_previo
- content_type: concept_card
- difficulty: medio
- tags: pasos_multiples, edo, adams, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_26

## Learning goal

Entender metodos de pasos multiples y reconocer cuando conviene usarlo dentro del bloque de ecuaciones diferenciales ordinarias.

## Formal definition

Los metodos de pasos multiples reutilizan informacion de varios pasos anteriores para avanzar la solucion con menor costo por iteracion una vez inicializados.

## Intuition

En lugar de calcular muchas pendientes nuevas como en RK4, un metodo multipaso aprovecha pendientes ya almacenadas del historial reciente.

## Why it matters

Este bloque modela cambios dinamicos paso a paso y es central en simulacion cientifica e ingenieril.

## Mini example

En lugar de calcular muchas pendientes nuevas como en RK4, un metodo multipaso aprovecha pendientes ya almacenadas del historial reciente.

## Related topics

- metodos_de_runge_kutta
- rigidez
