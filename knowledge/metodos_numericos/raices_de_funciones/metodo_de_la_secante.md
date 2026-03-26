# Metodo de la secante

## Metadata

- id: mn_raices_metodo_de_la_secante
- course: metodos_numericos
- unit: raices_de_funciones
- topic: metodo_de_la_secante
- subtopic: iteracion_sin_derivada
- content_type: concept_card
- difficulty: medio
- prerequisites: newton_raphson, recta_secante
- tags: secante, raices, iterativo, metodos_numericos
- source: corpus_seed_v2

## Learning goal

Entender como aproximar una raiz sin derivada explicita usando dos iteraciones
anteriores.

## Formal definition

El metodo usa dos valores previos para aproximar la derivada y calcular el
siguiente punto.

## Intuition

Es parecido a Newton, pero en lugar de usar la tangente exacta usa la secante
determinada por las dos aproximaciones mas recientes.

## Why it matters

Es util cuando calcular la derivada es costoso o poco practico.

## Key formulas

- `x_(n+1) = x_n - f(x_n)(x_n - x_(n-1)) / (f(x_n) - f(x_(n-1)))`

## Step by step explanation

1. Elige dos aproximaciones iniciales.
2. Evalua la funcion en ambos puntos.
3. Construye la secante.
4. Calcula la nueva aproximacion.
5. Repite usando siempre los dos ultimos valores.

## Common mistakes

- Empezar con dos puntos casi iguales.
- No controlar divisiones por valores muy pequenos.
- Suponer que siempre es estable.

## Mini example

Si ya tienes dos aproximaciones cercanas a la raiz, la secante puede avanzar
mas rapido que un metodo de intervalo.

## Related topics

- newton_raphson
- regula_falsi
