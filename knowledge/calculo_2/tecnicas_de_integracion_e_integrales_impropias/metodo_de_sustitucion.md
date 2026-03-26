# Metodo de sustitucion

## Metadata

- id: calc2_tecnicas_metodo_de_sustitucion
- course: calculo_2
- unit: tecnicas_de_integracion_e_integrales_impropias
- topic: metodo_de_sustitucion
- subtopic: trigonometria_y_racionalizacion
- content_type: concept_card
- difficulty: medio
- prerequisites: regla_de_la_cadena, integrales_basicas
- tags: sustitucion, trigonometria, racionalizacion, calculo_2
- source: corpus_seed_v3

## Learning goal

Entender como un cambio de variable simplifica integrales y como extender esta
idea a potencias trigonometricas, sustitucion trigonometrica y racionalizacion.

## Formal definition

La sustitucion consiste en introducir una variable auxiliar `u = g(x)` para
reescribir la integral en una forma mas simple.

## Intuition

Se busca reconocer una estructura compuesta donde parte del integrando actua
como derivada de otra parte.

## Why it matters

Es una de las tecnicas mas versatiles de integracion y aparece en gran cantidad
de ejercicios.

## Key formulas

- `u = g(x)`
- `du = g'(x) dx`

## Step by step explanation

1. Identifica una expresion interna candidata.
2. Deriva esa expresion para ver si aparece en el integrando.
3. Reescribe toda la integral en terminos de `u`.
4. Integra en la nueva variable.
5. Regresa a la variable original si es necesario.

## Common mistakes

- Cambiar solo una parte de la integral y dejar el resto en `x`.
- No transformar correctamente `dx`.
- Elegir sustituciones que complican mas la expresion.

## Mini example

Las potencias de funciones trigonometricas y las sustituciones trigonometricas
aparecen cuando hay radicales como `sqrt(a^2 - x^2)` o productos especiales.

## Related topics

- integracion_por_partes
- fracciones_parciales
