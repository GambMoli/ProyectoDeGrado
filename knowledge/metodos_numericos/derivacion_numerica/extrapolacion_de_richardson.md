# Extrapolacion de Richardson

## Metadata

- id: mn_deriv_extrapolacion_de_richardson
- course: metodos_numericos
- unit: derivacion_numerica
- topic: extrapolacion_de_richardson
- subtopic: cancelacion_de_error_dominante
- content_type: concept_card
- difficulty: medio
- tags: richardson, derivacion_numerica, extrapolacion, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_23

## Learning goal

Entender extrapolacion de richardson y reconocer cuando conviene usarlo dentro del bloque de derivacion numerica.

## Formal definition

La extrapolacion de Richardson combina aproximaciones obtenidas con distintos tamanos de paso para cancelar el termino dominante del error y mejorar la precision.

## Intuition

Si calculas una derivada con h y con h/2, Richardson puede mezclarlas para producir una estimacion mas fina que cualquiera de las dos por separado.

## Why it matters

Este bloque permite estimar tasas de cambio con datos tabulados y controlar mejor los errores de aproximacion.

## Mini example

Si calculas una derivada con h y con h/2, Richardson puede mezclarlas para producir una estimacion mas fina que cualquiera de las dos por separado.

## Related topics

- integracion_de_romberg
- formulas_de_diferenciacion_de_alta_exactitud
