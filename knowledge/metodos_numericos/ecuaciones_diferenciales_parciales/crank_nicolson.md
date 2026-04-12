# Crank-Nicolson

## Metadata

- id: mn_edp_crank_nicolson
- course: metodos_numericos
- unit: ecuaciones_diferenciales_parciales
- topic: crank_nicolson
- subtopic: promedio_entre_esquemas
- content_type: concept_card
- difficulty: medio
- tags: crank_nicolson, edp, parabolicas, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_30

## Learning goal

Entender crank-nicolson y reconocer cuando conviene usarlo dentro del bloque de ecuaciones diferenciales parciales.

## Formal definition

Crank-Nicolson combina informacion explicita e implicita promediando en el tiempo, con lo que ofrece buen equilibrio entre precision y estabilidad en ecuaciones parabolicas.

## Intuition

Para la difusion de calor, Crank-Nicolson usa tanto el estado actual como el futuro y suele producir mejores resultados que un esquema completamente explicito.

## Why it matters

Este bloque aproxima fenomenos distribuidos como calor, potencial y difusion en una o mas dimensiones.

## Mini example

Para la difusion de calor, Crank-Nicolson usa tanto el estado actual como el futuro y suele producir mejores resultados que un esquema completamente explicito.

## Related topics

- metodos_explicitos
- metodo_implicito_simple
