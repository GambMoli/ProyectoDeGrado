# Integracion por partes

## Metadata

- id: calc2_tecnicas_integracion_por_partes
- course: calculo_2
- unit: tecnicas_de_integracion_e_integrales_impropias
- topic: integracion_por_partes
- subtopic: regla_del_producto_al_reves
- content_type: concept_card
- difficulty: medio
- prerequisites: regla_del_producto, integrales_basicas
- tags: integracion_por_partes, tecnicas, calculo_2
- source: corpus_seed_v3

## Learning goal

Entender cuando conviene transformar una integral de producto en otra integral
mas simple usando la regla del producto invertida.

## Formal definition

- `integral u dv = uv - integral v du`

## Intuition

Se escoge una parte para derivar y otra para integrar con la meta de simplificar
la nueva integral resultante.

## Why it matters

Es muy util para productos de polinomios con exponenciales, logaritmos o
funciones trigonometricas.

## Key formulas

- `integral u dv = uv - integral v du`

## Step by step explanation

1. Elige `u` como lo que se simplifica al derivar.
2. Elige `dv` como lo que se puede integrar con facilidad.
3. Calcula `du` y `v`.
4. Sustituye en la formula.
5. Resuelve la nueva integral.

## Common mistakes

- Elegir mal `u` y `dv`.
- Perder el signo negativo.
- No revisar si la nueva integral realmente es mas simple.

## Mini example

`integral x e^x dx = x e^x - integral e^x dx`

## Related topics

- metodo_de_sustitucion
- fracciones_parciales
