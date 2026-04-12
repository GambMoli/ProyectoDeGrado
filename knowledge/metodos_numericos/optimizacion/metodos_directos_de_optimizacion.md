# Metodos directos de optimizacion

## Metadata

- id: mn_opt_metodos_directos_de_optimizacion
- course: metodos_numericos
- unit: optimizacion
- topic: metodos_directos_de_optimizacion
- subtopic: busqueda_sin_gradiente
- content_type: concept_card
- difficulty: medio
- tags: metodos_directos, optimizacion, sin_gradiente, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_14

## Learning goal

Entender metodos directos de optimizacion y reconocer cuando conviene usarlo dentro del bloque de optimizacion.

## Formal definition

Los metodos directos de optimizacion avanzan usando solo evaluaciones de la funcion objetivo, de modo que resultan utiles cuando el gradiente no esta disponible o es costoso.

## Intuition

Si el modelo es una caja negra y solo devuelve el valor del costo, un metodo directo puede explorar direcciones sin derivadas explicitas.

## Why it matters

Este bloque permite encontrar minimos o maximos numericamente cuando no es practico resolver el problema en forma analitica.

## Mini example

Si el modelo es una caja negra y solo devuelve el valor del costo, un metodo directo puede explorar direcciones sin derivadas explicitas.

## Related topics

- busqueda_de_la_seccion_dorada
- metodos_con_gradiente
