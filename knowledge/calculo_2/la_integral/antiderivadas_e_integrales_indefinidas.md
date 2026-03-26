# Antiderivadas e integrales indefinidas

## Metadata

- id: calc2_la_integral_antiderivadas
- course: calculo_2
- unit: la_integral
- topic: antiderivadas_e_integrales_indefinidas
- subtopic: concepto_basico
- content_type: concept_card
- difficulty: basico
- prerequisites: derivadas_basicas
- tags: antiderivadas, integrales_indefinidas, calculo_2
- source: corpus_seed_v3

## Learning goal

Entender que una integral indefinida representa la familia de funciones cuya
derivada coincide con la funcion dada.

## Formal definition

Si `F'(x) = f(x)`, entonces `F(x)` es una antiderivada de `f(x)` y:

- `integral f(x) dx = F(x) + C`

## Intuition

Integrar indefinidamente es deshacer una derivada. El `+ C` aparece porque
muchas funciones distintas pueden tener la misma derivada.

## Why it matters

Es la base para integrar expresiones y para conectar luego con integrales
definidas y el teorema fundamental del calculo.

## Key formulas

- `integral x^n dx = x^(n+1)/(n+1) + C`, si `n != -1`
- `integral 1/x dx = ln|x| + C`

## Step by step explanation

1. Identifica el patron derivativo de la funcion.
2. Busca una funcion cuya derivada reproduzca ese patron.
3. Agrega la constante de integracion.

## Common mistakes

- Olvidar `+ C`.
- Confundir integral indefinida con un numero.
- Aplicar mal la regla de potencia cuando `n = -1`.

## Mini example

`integral 3x^2 dx = x^3 + C`, porque la derivada de `x^3` es `3x^2`.

## Related topics

- teorema_fundamental_del_calculo
- integracion_por_sustitucion
