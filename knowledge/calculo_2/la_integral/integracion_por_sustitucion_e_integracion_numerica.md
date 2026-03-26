# Integracion por sustitucion e integracion por metodos numericos

## Metadata

- id: calc2_la_integral_sustitucion_y_metodos_numericos
- course: calculo_2
- unit: la_integral
- topic: integracion_por_sustitucion_e_integracion_numerica
- subtopic: cambio_de_variable_y_aproximacion
- content_type: concept_card
- difficulty: medio
- prerequisites: antiderivadas, teorema_fundamental_del_calculo
- tags: sustitucion, integracion_numerica, cambio_de_variable, calculo_2
- source: corpus_seed_v3

## Learning goal

Distinguir entre integrar por cambio de variable exacto y aproximar una integral
cuando no se dispone de una antiderivada facil.

## Formal definition

La sustitucion reescribe una integral mediante un cambio de variable. La
integracion numerica aproxima el valor de una integral definida con reglas como
trapecios o Simpson.

## Intuition

La sustitucion simplifica la forma algebraica. La integracion numerica reemplaza
la curva por figuras geometricas o polinomios sencillos para estimar el area.

## Why it matters

No todas las integrales se resuelven de forma cerrada. Por eso es importante
saber cuando transformar exactamente y cuando aproximar.

## Key formulas

- `u = g(x)`
- `integral_a^b f(x) dx ~= aproximacion_numerica`

## Step by step explanation

1. Revisa si la integral tiene una composicion apta para sustitucion.
2. Si la sustitucion no simplifica o la antiderivada no es accesible, considera
   un metodo numerico.
3. Elige la estrategia segun el objetivo: exactitud simbolica o aproximacion.

## Common mistakes

- Forzar sustituciones que no simplifican.
- Usar metodos numericos sin controlar error o tamano de paso.
- No ajustar los limites al cambiar de variable en integrales definidas.

## Mini example

`integral 2x cos(x^2) dx` se resuelve naturalmente con `u = x^2`, mientras que
otras integrales definidas pueden aproximarse con trapecios o Simpson.

## Related topics

- metodo_de_sustitucion
- simpson_1_3
