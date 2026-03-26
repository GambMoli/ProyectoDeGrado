# Primera derivada numerica

## Metadata

- id: mn_derivacion_primera_derivada
- course: metodos_numericos
- unit: derivacion_numerica
- topic: primera_derivada
- subtopic: formulas_progresivas_regresivas_y_centrales
- content_type: concept_card
- difficulty: medio
- prerequisites: derivadas, serie_de_taylor
- tags: derivacion_numerica, primera_derivada, diferencias_finitas, metodos_numericos
- source: corpus_seed_v2

## Learning goal

Entender como aproximar la primera derivada a partir de valores tabulados de una
funcion.

## Formal definition

Las formulas de diferencias finitas estiman la derivada usando puntos vecinos.
Se usan variantes progresivas, regresivas y centrales, incluyendo formulas de 3
y 4 puntos segun la posicion del dato.

## Intuition

Si no tienes la derivada exacta pero si varios valores de la funcion, puedes
estimar la pendiente comparando como cambia la funcion entre nodos cercanos.

## Why it matters

Es util en datos experimentales, simulaciones y problemas donde solo se conoce
la funcion en una malla discreta.

## Key formulas

- progresiva: `f'(x_i) ~= (f(x_i+h)-f(x_i))/h`
- regresiva: `f'(x_i) ~= (f(x_i)-f(x_i-h))/h`
- central: `f'(x_i) ~= (f(x_i+h)-f(x_i-h))/(2h)`

## Step by step explanation

1. Identifica si el punto esta al inicio, al final o en el interior.
2. Elige la formula adecuada: progresiva, regresiva o central.
3. Usa formulas de 3 o 4 puntos si necesitas mejor precision.
4. Calcula la aproximacion y estima el orden del error.

## Common mistakes

- Usar formula central en un borde.
- Mezclar formulas con espaciado `h` no uniforme.
- No distinguir el orden del error de cada formula.

## Mini example

Si conoces `f(x_i)` y `f(x_i+h)`, una diferencia progresiva da una primera
estimacion de `f'(x_i)`.

## Related topics

- segunda_derivada
- serie_de_taylor
