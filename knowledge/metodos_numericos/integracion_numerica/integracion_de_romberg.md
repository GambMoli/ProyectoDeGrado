# Integracion de Romberg

## Metadata

- id: mn_integracion_romberg
- course: metodos_numericos
- unit: integracion_numerica
- topic: integracion_de_romberg
- subtopic: extrapolacion_de_richardson
- content_type: concept_card
- difficulty: medio
- prerequisites: trapecios, error_de_truncamiento
- tags: romberg, richardson, integracion_numerica, extrapolacion, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_22

## Learning goal

Entender como combinar aproximaciones del trapecio para obtener integrales mucho
mas exactas.

## Formal definition

La integracion de Romberg aplica extrapolacion de Richardson sobre una secuencia
de reglas del trapecio con pasos cada vez menores para cancelar terminos
dominantes del error.

## Intuition

Si se conocen dos aproximaciones con errores parecidos pero distintos pasos, se
pueden mezclar de forma inteligente para producir una estimacion mejor.

## Why it matters

Suele alcanzar alta precision con pocas evaluaciones de la funcion cuando esta es
suave y puede evaluarse libremente.

## Key formulas

- `I_(j,k) = (4^(k-1) I_(j+1,k-1) - I_(j,k-1)) / (4^(k-1) - 1)`
- `I_(j,1)` proviene de la regla del trapecio compuesta

## Step by step explanation

1. Calcula una integral con trapecio usando un paso inicial.
2. Repite con un paso mas pequeno.
3. Combina ambas con extrapolacion de Richardson.
4. Construye una tabla triangular de estimaciones mejores.
5. Detente cuando el cambio entre niveles sea aceptable.

## Common mistakes

- Aplicarlo a funciones poco suaves o con singularidades sin revisar supuestos.
- Confundir la tabla de Romberg con una simple repeticion del trapecio.
- No usar un criterio de paro para decidir cuando detener la refinacion.

## Mini example

Si ya tienes dos estimaciones del trapecio con `h` y `h/2`, Romberg las combina
para anular parte del error principal y acercarse mucho mas al valor real.

## Related topics

- trapecios
- cuadratura_de_gauss
