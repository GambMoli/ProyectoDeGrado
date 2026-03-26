# Ecuaciones Parametricas

## Metadata

- id: calc2_parametricas_001
- course: calculo_2
- unit: parametricas_y_polares
- topic: ecuaciones_parametricas
- subtopic: concepto_basico
- content_type: concept_card
- difficulty: medio
- tags: parametricas, curvas, parametro, calculo_2
- source: calculo_2_syllabus

## Learning goal

Entender que algunas curvas no pueden ser representadas como simples funciones `y = f(x)`, y que las ecuaciones parametricas resuelven esto al expresar tanto `x` como `y` en funcion de una tercera variable independiente `t` llamada parametro.

## Formal definition

Si `f` y `g` son funciones continuas de una variable `t` en un intervalo `I`, entonces el conjunto de puntos `(x, y)` definidos por:
`x = f(t)`
`y = g(t)`
es una curva parametrica.

## Intuition

Piensa en una mosca volando en una habitacion. Si intentas describir su posicion `y` solo basado en su posicion `x` (con una funcion f(x)), sera imposible porque la mosca puede haber pasado por el mismo `x` muchas veces a diferentes alturas `y`.
Pero si añades un reloj (`t`, de tiempo), puedes saber exactamente donde estaba: a los `t` segundos, la mosca estaba en `x(t)` e `y(t)`.

## Why it matters

Son indispensables en fisica e ingenieria para modelar el movimiento (trayectorias, orbitas) donde el tiempo es el factor conductor; y para trazar curvas complejas con cruces e iteraciones que no pasarian la "prueba de la linea vertical" en funciones normales.

## Key formulas

Derivadas parametricas:
`dy/dx = (dy/dt) / (dx/dt)`

## Step by step explanation

Para graficar una simple curva parametrica:
1. Toma el intervalo de valores para el parametro `t` (e.g. `t` desde 0 a 5).
2. Elige valores de `t` progresivamente.
3. Evalua esos `t` en las ecuaciones de `x = f(t)` e `y = g(t)`.
4. Traza los puntos en tu grafica `(x, y)` indicando la direccion progresiva si el factor `t` tiene orientacion.

## Common mistakes

- Intentar tratar a la variable dependiente `y` como dependiente de `x` sin transformar o aislar correctamente la variable `t` en los terminos.
- Olvidar que una curva parametrica tiene **orientacion** (una direccion en que se dibuja a medida que `t` avanza).

## Mini example

Curva de una circunferencia de radio 1:
`x = cos(t)`
`y = sin(t)`
Para `t` de 0 a 2*PI. A medida que `t` avanza, se dibuja un circulo perfecto en sentido antihorario. Al sustituir te das cuenta que `cos(t)^2 + sin(t)^2 = 1` por lo que `x^2 + y^2 = 1` probando que es un circulo.

## Related topics

- derivadas_en_parametricas
- areas_en_curvas_parametricas
- coordenadas_polares
