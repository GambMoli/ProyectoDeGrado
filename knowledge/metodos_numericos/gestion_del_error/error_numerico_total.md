# Error numerico total

## Metadata

- id: mn_error_error_numerico_total
- course: metodos_numericos
- unit: gestion_del_error
- topic: error_numerico_total
- subtopic: balance_entre_truncamiento_y_redondeo
- content_type: concept_card
- difficulty: medio
- tags: error_numerico_total, truncamiento, redondeo, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_4

## Learning goal

Entender error numerico total y reconocer cuando conviene usarlo dentro del bloque de gestion del error.

## Formal definition

El error numerico total combina el error de truncamiento y el error de redondeo, y muestra que reducir el paso no siempre mejora indefinidamente la precision.

## Intuition

En una derivada numerica, hacer h demasiado grande aumenta truncamiento, pero hacerla demasiado pequena puede disparar el redondeo y empeorar el resultado.

## Why it matters

Este bloque ayuda a estimar la confiabilidad de los resultados numericos y a decidir si una aproximacion ya es aceptable.

## Mini example

En una derivada numerica, hacer h demasiado grande aumenta truncamiento, pero hacerla demasiado pequena puede disparar el redondeo y empeorar el resultado.

## Related topics

- gestion_del_error
- propagacion_del_error
