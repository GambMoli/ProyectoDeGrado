# Metodos de Runge-Kutta

## Metadata

- id: mn_edo_metodos_de_runge_kutta
- course: metodos_numericos
- unit: ecuaciones_diferenciales_ordinarias
- topic: metodos_de_runge_kutta
- subtopic: evaluacion_multiple_de_pendientes
- content_type: concept_card
- difficulty: medio
- prerequisites: metodo_de_euler, ecuaciones_diferenciales_basicas
- tags: runge_kutta, edo, rk4, pendientes, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_25

## Learning goal

Entender como mejorar la aproximacion de Euler combinando varias pendientes
evaluadas dentro del mismo paso.

## Formal definition

Los metodos de Runge-Kutta son integradores de un paso para ecuaciones
diferenciales ordinarias que construyen una pendiente efectiva a partir de varias
evaluaciones de `f(x, y)` dentro del intervalo `h`.

## Intuition

En vez de confiar solo en la pendiente del inicio, el metodo sondea tambien
puntos intermedios o finales del paso para representar mejor la curvatura de la
solucion.

## Why it matters

Ofrecen mucha mas exactitud que Euler sin requerir derivadas de orden superior,
por eso son de los metodos mas usados para EDO no rigidas.

## Key formulas

- `k1 = f(x_i, y_i)`
- `k2 = f(x_i + h/2, y_i + h k1 / 2)`
- `k3 = f(x_i + h/2, y_i + h k2 / 2)`
- `k4 = f(x_i + h, y_i + h k3)`
- `y_(i+1) = y_i + (h/6)(k1 + 2k2 + 2k3 + k4)`

## Step by step explanation

1. Evalua una primera pendiente en el inicio del paso.
2. Evalua pendientes adicionales en puntos intermedios o al final.
3. Combina esas pendientes con pesos especificos.
4. Usa la pendiente efectiva para actualizar `y`.
5. Repite en el siguiente paso.

## Common mistakes

- Copiar las formulas de `k1` a `k4` sin respetar los desplazamientos.
- Usar un paso fijo grande y esperar precision automatica.
- Pensar que todos los metodos RK tienen el mismo orden o el mismo costo.

## Mini example

En RK4 clasico se calculan cuatro pendientes y se da mas peso a las dos
intermedias, lo que mejora notablemente la aproximacion frente a Euler con el
mismo tamano de paso.

## Related topics

- metodo_de_euler
- integracion_de_romberg
