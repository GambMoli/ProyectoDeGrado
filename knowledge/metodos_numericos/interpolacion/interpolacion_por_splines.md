# Interpolacion por splines

## Metadata

- id: mn_interpolacion_splines
- course: metodos_numericos
- unit: interpolacion
- topic: interpolacion_por_splines
- subtopic: trazadores_cubicos_y_suavidad
- content_type: concept_card
- difficulty: medio
- prerequisites: interpolacion, polinomios
- tags: splines, trazadores, interpolacion, suavidad, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_18

## Learning goal

Entender por que los splines interpolan de forma mas suave y estable que un
polinomio global de grado alto.

## Formal definition

La interpolacion por splines construye una funcion por tramos, usualmente con
polinomios cubicos, que pasa por los datos y ademas impone continuidad en la
funcion y en algunas de sus derivadas en los nodos.

## Intuition

En lugar de forzar una sola curva global que puede oscilar demasiado, se unen
pequenas curvas suaves entre pares de puntos vecinos.

## Why it matters

Suele producir mejores aproximaciones locales y menos oscilacion cuando hay
muchos datos o cambios bruscos en una region especifica.

## Key formulas

- `S_i(x) = a_i + b_i(x - x_i) + c_i(x - x_i)^2 + d_i(x - x_i)^3`
- `S_i(x_i) = y_i`
- `S_i(x_(i+1)) = y_(i+1)`

## Step by step explanation

1. Divide el dominio en intervalos entre nodos consecutivos.
2. Asigna un polinomio a cada intervalo.
3. Impone continuidad en los nodos.
4. Agrega condiciones de frontera, por ejemplo spline natural.
5. Evalua el tramo correspondiente al punto que quieres estimar.

## Common mistakes

- Tratar un spline como si fuera un unico polinomio global.
- Olvidar las condiciones de frontera.
- Pensar que siempre conviene un grado muy alto para mejorar el ajuste.

## Mini example

Con muchos datos experimentales, un spline cubico suele seguir la forma general
sin introducir las oscilaciones artificiales que aparecen en polinomios globales
de alto grado.

## Related topics

- newton
- lagrange
