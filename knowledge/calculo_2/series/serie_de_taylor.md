# Serie de Taylor y Maclaurin

## Metadata

- id: calc2_series_taylor_001
- course: calculo_2
- unit: series
- topic: serie_de_taylor
- subtopic: aproximacion_polinomial
- content_type: concept_card
- difficulty: avanzado
- tags: serie_de_taylor, maclaurin, aproximaciones, calculo_2
- source: calculo_2_syllabus

## Learning goal

Comprender que las series de Taylor permiten aproximar funciones complejas (como senos, exponenciales, logaritmos) usando polinomios infinitos basados en las derivadas evaluadas en un solo punto.

## Formal definition

Si una funcion `f(x)` tiene derivadas de todos los ordenes en un punto `a`, su serie de Taylor centrada en `a` es:
`f(x) = f(a) + f'(a)(x-a) + f''(a)/2! * (x-a)^2 + f'''(a)/3! * (x-a)^3 + ...`
Si `a = 0`, a esta serie se le conoce especificamente como **Serie de Maclaurin**.

## Intuition

Piensa que tratas de modelar un terreno curvo usando plastilina. En un punto `a`, la primera derivada asegura que la inclinacion de la plastilina sea la misma que la del terreno, la segunda derivada que la "curva" coincida, la tercera que el "giro" coincida, y asi sucesivamente. Al tener infinitas derivadas iguales, la plastilina se vuelve identica al terreno original cerca de `a`.

## Why it matters

Las computadoras no y calculadoras no saben obtener el seno, coseno o la exponencial. Solo saben sumar, restar, multiplicar y dividir. La serie de Taylor (y Maclaurin) traduce esas funciones tracendentales en polinomios, para que las calculadoras puedan computarlas con operaciones basicas numericamente.

## Key formulas

Serie de Maclaurin (centrada en a=0):
`f(x) = suma desde n=0 hasta infinito de [ (f^n(0) / n!) * x^n ]`

## Step by step explanation

Para encontrar la serie de Maclaurin de una funcion `f(x)` de grado 3:
1. Deriva la funcion tres veces: `f'(x)`, `f''(x)`, `f'''(x)`.
2. Evalua cada una en `x=0`: `f(0)`, `f'(0)`, `f''(0)`, `f'''(0)`.
3. Multiplica por `x^n / n!` correspondientemente.
4. Suma los resultados.

## Common mistakes

- Olvidar el factorial `!` dividiendo cada termino.
- Confundir el centro `a` de la serie y olvidarse restar `(x-a)^n` cuando la serie no es de Maclaurin (`a != 0`).

## Mini example

La serie de Maclaurin para `e^x` (donde todas las derivadas son `e^x`, que en 0 valen 1):
`e^x = 1/1 + x/1 + x^2/2 + x^3/6 + x^4/24 + ...`

## Related topics

- radio_y_criterio_de_convergencia
- aproximaciones_locales
