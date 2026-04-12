# Metodo de Newton para optimizacion

## Metadata

- id: mn_opt_newton_para_optimizacion
- course: metodos_numericos
- unit: optimizacion
- topic: newton_para_optimizacion
- subtopic: uso_de_derivadas_para_extremos
- content_type: concept_card
- difficulty: medio
- tags: newton_optimizacion, optimizacion, derivadas, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_13

## Learning goal

Entender metodo de newton para optimizacion y reconocer cuando conviene usarlo dentro del bloque de optimizacion.

## Formal definition

El metodo de Newton para optimizacion busca puntos estacionarios usando primera y segunda derivada, por lo que puede converger muy rapido si el punto inicial es razonable.

## Intuition

En una funcion convexa, usar f' y f'' cerca del minimo suele dar saltos mas informados que un metodo sin derivadas.

## Why it matters

Este bloque permite encontrar minimos o maximos numericamente cuando no es practico resolver el problema en forma analitica.

## Key formulas

- `x_(k+1) = x_k - f'(x_k) / f''(x_k)`

## Mini example

En una funcion convexa, usar f' y f'' cerca del minimo suele dar saltos mas informados que un metodo sin derivadas.

## Related topics

- busqueda_de_la_seccion_dorada
- metodos_con_gradiente
