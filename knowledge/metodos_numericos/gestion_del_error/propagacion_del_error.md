# Propagacion del error

## Metadata

- id: mn_error_propagacion_del_error
- course: metodos_numericos
- unit: gestion_del_error
- topic: propagacion_del_error
- subtopic: sensibilidad_y_acumulacion
- content_type: concept_card
- difficulty: medio
- tags: propagacion_del_error, sensibilidad, errores, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_4

## Learning goal

Entender propagacion del error y reconocer cuando conviene usarlo dentro del bloque de gestion del error.

## Formal definition

La propagacion del error estudia como los errores presentes en datos, parametros o pasos intermedios se transmiten y amplifican en el resultado final de un calculo numerico.

## Intuition

Si una salida depende de varias mediciones aproximadas, una pequena variacion en cada entrada puede acumularse y cambiar la respuesta final mas de lo esperado.

## Why it matters

Este bloque ayuda a estimar la confiabilidad de los resultados numericos y a decidir si una aproximacion ya es aceptable.

## Key formulas

- `delta y ~= (dy/dx) delta x`

## Mini example

Si una salida depende de varias mediciones aproximadas, una pequena variacion en cada entrada puede acumularse y cambiar la respuesta final mas de lo esperado.

## Related topics

- gestion_del_error
- error_numerico_total
