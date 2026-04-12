# Metodos con gradiente

## Metadata

- id: mn_opt_metodos_con_gradiente
- course: metodos_numericos
- unit: optimizacion
- topic: metodos_con_gradiente
- subtopic: descenso_segundo_bloque
- content_type: concept_card
- difficulty: medio
- tags: gradiente, optimizacion, descenso, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_14

## Learning goal

Entender metodos con gradiente y reconocer cuando conviene usarlo dentro del bloque de optimizacion.

## Formal definition

Los metodos con gradiente usan la informacion direccional de la derivada para mover la solucion hacia regiones de menor o mayor valor objetivo.

## Intuition

Si una funcion aumenta en la direccion del gradiente, para minimizarla conviene moverse en la direccion opuesta con un tamano de paso adecuado.

## Why it matters

Este bloque permite encontrar minimos o maximos numericamente cuando no es practico resolver el problema en forma analitica.

## Key formulas

- `x_(k+1) = x_k - alpha_k grad f(x_k)`

## Mini example

Si una funcion aumenta en la direccion del gradiente, para minimizarla conviene moverse en la direccion opuesta con un tamano de paso adecuado.

## Related topics

- newton_para_optimizacion
- programacion_lineal
