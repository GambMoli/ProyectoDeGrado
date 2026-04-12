# Metodo de Euler

## Metadata

- id: mn_edo_metodo_de_euler
- course: metodos_numericos
- unit: ecuaciones_diferenciales_ordinarias
- topic: metodo_de_euler
- subtopic: integracion_explicita_de_primer_orden
- content_type: concept_card
- difficulty: basico
- prerequisites: derivadas, ecuaciones_diferenciales_basicas
- tags: euler, edo, integracion_explicita, paso_a_paso, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_25

## Learning goal

Comprender la idea basica de avanzar una solucion de EDO usando la pendiente
actual y un tamano de paso fijo.

## Formal definition

Para una ecuacion `y' = f(x, y)` con condicion inicial, el metodo de Euler
aproxima la solucion mediante la actualizacion
`y_(i+1) = y_i + h f(x_i, y_i)`.

## Intuition

En cada paso se reemplaza la curva real por su recta tangente local y se avanza
una distancia `h`.

## Why it matters

Es el punto de partida conceptual para muchos integradores de EDO y permite
entender claramente el papel del paso, el error local y el error global.

## Key formulas

- `x_(i+1) = x_i + h`
- `y_(i+1) = y_i + h f(x_i, y_i)`

## Step by step explanation

1. Parte de la condicion inicial.
2. Evalua la pendiente `f(x_i, y_i)`.
3. Avanza en `x` una cantidad `h`.
4. Corrige `y` con la pendiente actual.
5. Repite hasta cubrir el intervalo deseado.

## Common mistakes

- Elegir un paso demasiado grande y acumular mucho error.
- Creer que la aproximacion lineal local sirve igual de bien para cualquier EDO.
- No distinguir entre error local en un paso y error global acumulado.

## Mini example

Si `y' = f(x, y)` y en el punto actual la pendiente vale `8.5`, con `h = 0.5`
Euler avanza `0.5 * 8.5 = 4.25` unidades en la variable dependiente.

## Related topics

- metodos_de_runge_kutta
- serie_de_taylor
