# Gestion del error

## Metadata

- id: mn_error_gestion_del_error
- course: metodos_numericos
- unit: gestion_del_error
- topic: gestion_del_error
- subtopic: error_absoluto_relativo_y_redondeo
- content_type: concept_card
- difficulty: basico
- prerequisites: algebra_basica
- tags: error_absoluto, error_relativo, truncamiento, redondeo, metodos_numericos
- source: corpus_seed_v2

## Learning goal

Entender como medir y controlar el error al aproximar numeros o resultados en
metodos numericos.

## Formal definition

El error absoluto es la diferencia en valor absoluto entre el valor real y el
valor aproximado. El error relativo compara esa diferencia con el tamano del
valor real.

## Intuition

En metodos numericos casi nunca se obtiene el valor exacto. La calidad del
metodo depende de que tan pequeno sea el error y de como ese error se propaga.

## Why it matters

Sin control del error no se puede decidir si una aproximacion es util ni cuando
detener un algoritmo iterativo.

## Key formulas

- `error_absoluto = |valor_real - valor_aproximado|`
- `error_relativo = |valor_real - valor_aproximado| / |valor_real|`

## Step by step explanation

1. Identifica el valor de referencia si esta disponible.
2. Calcula la diferencia entre el valor exacto y el aproximado.
3. Evalua si conviene usar error absoluto o relativo.
4. Usa una tolerancia para decidir si el metodo ya es suficientemente bueno.

## Common mistakes

- Confundir precision con exactitud.
- Usar solo error absoluto cuando la escala del problema cambia mucho.
- Ignorar el error de redondeo acumulado.

## Mini example

Si el valor real es `2.0` y la aproximacion es `1.96`, el error absoluto es
`0.04` y el error relativo es `0.02`.

## Related topics

- criterio_de_parada
- convergencia_numerica
