# Newton Raphson

## Metadata

- id: mn_raices_newton_raphson
- course: metodos_numericos
- unit: raices_de_funciones
- topic: newton_raphson
- subtopic: metodo_tangente
- content_type: concept_card
- difficulty: medio
- prerequisites: derivadas, raices_de_funciones
- tags: newton_raphson, tangente, convergencia, metodos_numericos
- source: corpus_seed_v2

## Learning goal

Entender como una tangente puede producir aproximaciones sucesivas a una raiz.

## Formal definition

Partiendo de un valor inicial `x_n`, se calcula:

- `x_(n+1) = x_n - f(x_n) / f'(x_n)`

## Intuition

En cada paso se reemplaza la funcion por su recta tangente local y se usa el
corte de esa tangente con el eje `x` como nueva aproximacion.

## Why it matters

Cuando el punto inicial es bueno y la funcion se comporta bien, converge muy
rapido.

## Key formulas

- `x_(n+1) = x_n - f(x_n) / f'(x_n)`

## Step by step explanation

1. Elige una aproximacion inicial.
2. Evalua la funcion y su derivada.
3. Calcula la nueva iteracion con la formula de Newton.
4. Repite hasta que el cambio sea pequeno.

## Common mistakes

- Usar un punto inicial muy malo.
- No controlar el caso `f'(x_n) = 0`.
- Pensar que siempre converge.

## Mini example

Para resolver `x^2 - 2 = 0`, una eleccion inicial `x_0 = 1.5` produce una
secuencia que se acerca rapidamente a `sqrt(2)`.

## Related topics

- metodo_de_la_secante
- punto_fijo
