# Integrales impropias

## Metadata

- id: calc2_tecnicas_integrales_impropias
- course: calculo_2
- unit: tecnicas_de_integracion_e_integrales_impropias
- topic: integrales_impropias
- subtopic: limites_en_integracion
- content_type: concept_card
- difficulty: medio
- prerequisites: integrales_definidas, limites
- tags: integrales_impropias, convergencia, calculo_2
- source: corpus_seed_v3

## Learning goal

Entender como extender la integral definida a intervalos infinitos o funciones
con discontinuidades no acotadas.

## Formal definition

Una integral impropia se define mediante un limite cuando el intervalo es
infinito o cuando el integrando se vuelve no acotado en algun punto.

## Intuition

No se integra directamente sobre una situacion infinita o singular, sino sobre
integrales ordinarias y luego se pasa al limite.

## Why it matters

Permite decidir si una acumulacion infinita converge o diverge.

## Key formulas

- `integral_a^infinito f(x) dx = lim integral_a^b f(x) dx`

## Step by step explanation

1. Identifica donde esta la impropiedad.
2. Reemplaza el extremo problematico por una variable.
3. Evalua la integral ordinaria.
4. Toma el limite.
5. Decide si converge o diverge.

## Common mistakes

- Evaluar la integral sin introducir el limite.
- Concluir convergencia sin revisar el limite final.
- Mezclar varios puntos impropios sin separarlos.

## Mini example

`integral_1^infinito 1/x^2 dx` converge porque el limite del valor acumulado es
finito.

## Related topics

- limites
- fracciones_parciales
