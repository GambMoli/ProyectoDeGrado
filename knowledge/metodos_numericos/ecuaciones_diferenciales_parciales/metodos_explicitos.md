# Metodos explicitos para ecuaciones parabolicas

## Metadata

- id: mn_edp_metodos_explicitos
- course: metodos_numericos
- unit: ecuaciones_diferenciales_parciales
- topic: metodos_explicitos
- subtopic: avance_directo_en_el_tiempo
- content_type: concept_card
- difficulty: medio
- tags: metodos_explicitos, edp, parabolicas, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_30

## Learning goal

Entender metodos explicitos para ecuaciones parabolicas y reconocer cuando conviene usarlo dentro del bloque de ecuaciones diferenciales parciales.

## Formal definition

Los metodos explicitos avanzan la solucion de una EDP usando solo informacion del paso actual, por lo que son faciles de implementar pero sensibles a restricciones de estabilidad.

## Intuition

En la ecuacion de calor, un esquema explicito actualiza cada nodo con vecinos del tiempo anterior y exige una relacion adecuada entre paso temporal y espacial.

## Why it matters

Este bloque aproxima fenomenos distribuidos como calor, potencial y difusion en una o mas dimensiones.

## Mini example

En la ecuacion de calor, un esquema explicito actualiza cada nodo con vecinos del tiempo anterior y exige una relacion adecuada entre paso temporal y espacial.

## Related topics

- ecuacion_de_conduccion_de_calor
- metodo_implicito_simple
