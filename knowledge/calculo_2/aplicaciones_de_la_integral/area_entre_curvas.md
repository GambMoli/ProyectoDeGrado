# Area entre curvas

## Metadata

- id: calc2_aplicaciones_area_entre_curvas
- course: calculo_2
- unit: aplicaciones_de_la_integral
- topic: area_entre_curvas
- subtopic: diferencia_superior_menos_inferior
- content_type: concept_card
- difficulty: medio
- prerequisites: integrales_definidas, graficas
- tags: area_entre_curvas, aplicaciones, calculo_2
- source: corpus_seed_v3

## Learning goal

Entender como calcular el area encerrada entre dos curvas comparando cual queda
arriba y cual queda abajo.

## Formal definition

Si `f(x)` esta por encima de `g(x)` en `[a,b]`, entonces:

- `A = integral_a^b (f(x) - g(x)) dx`

## Intuition

El area entre curvas se obtiene sumando pequeñas tiras verticales cuya altura es
la diferencia entre la curva superior y la inferior.

## Why it matters

Es una de las aplicaciones geometricas mas directas de la integral definida.

## Key formulas

- `A = integral_a^b (superior - inferior) dx`

## Step by step explanation

1. Encuentra puntos de interseccion.
2. Determina cual curva es superior.
3. Plantea la diferencia adecuada.
4. Integra en el intervalo correcto.

## Common mistakes

- No dividir el intervalo cuando las curvas intercambian posicion.
- Restar en el orden incorrecto.
- Confundir area con integral neta.

## Mini example

Si `f(x)` esta arriba de `g(x)` en un intervalo, la altura de cada franja es
`f(x) - g(x)`.

## Related topics

- volumen_solidos_de_revolucion
- integrales_definidas_y_sumas_de_riemann
