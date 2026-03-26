# Teorema fundamental del calculo

## Metadata

- id: calc2_la_integral_teorema_fundamental
- course: calculo_2
- unit: la_integral
- topic: teorema_fundamental_del_calculo
- subtopic: conexion_entre_integral_y_derivada
- content_type: theorem_card
- difficulty: medio
- prerequisites: antiderivadas, integrales_definidas
- tags: teorema_fundamental, derivadas, integrales, calculo_2
- source: corpus_seed_v3

## Learning goal

Entender la relacion estructural entre derivar y calcular integrales definidas.

## Formal definition

Si `F` es una antiderivada de `f` en `[a,b]`, entonces:

- `integral_a^b f(x) dx = F(b) - F(a)`

Ademas, si `G(x) = integral_a^x f(t) dt`, entonces `G'(x) = f(x)`.

## Intuition

La derivada mide cambio instantaneo y la integral acumula cambio. El teorema
fundamental muestra que ambos procesos son inversos en el marco adecuado.

## Why it matters

Convierte el calculo de integrales definidas en una tarea de antiderivacion.

## Key formulas

- `integral_a^b f(x) dx = F(b) - F(a)`
- `d/dx [integral_a^x f(t) dt] = f(x)`

## Step by step explanation

1. Busca una antiderivada de la funcion.
2. Evalua esa antiderivada en el limite superior.
3. Evalua en el limite inferior.
4. Resta ambos valores.

## Common mistakes

- Olvidar evaluar en ambos extremos.
- Confundir integral definida con integral indefinida.
- Ignorar las condiciones de continuidad.

## Mini example

`integral_0^2 x dx = [x^2/2]_0^2 = 2`

## Related topics

- antiderivadas_e_integrales_indefinidas
- integrales_definidas_y_sumas_de_riemann
