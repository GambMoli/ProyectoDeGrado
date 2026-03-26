# Biseccion

## Metadata

- id: mn_raices_biseccion
- course: metodos_numericos
- unit: raices_de_funciones
- topic: biseccion
- subtopic: metodo_de_intervalo
- content_type: concept_card
- difficulty: basico
- prerequisites: continuidad, cambio_de_signo
- tags: biseccion, raices, intervalo, metodos_numericos
- source: corpus_seed_v2

## Learning goal

Entender como localizar una raiz encerrandola en un intervalo y reduciendo ese
intervalo a la mitad en cada iteracion.

## Formal definition

Si `f(a)` y `f(b)` tienen signos opuestos y `f` es continua, entonces existe al
menos una raiz en `[a, b]`. El metodo toma el punto medio y conserva el
subintervalo donde persiste el cambio de signo.

## Intuition

Cada paso descarta la mitad del intervalo sin perder la raiz.

## Why it matters

Es uno de los metodos mas robustos para encontrar raices cuando se conoce un
intervalo inicial valido.

## Key formulas

- `c = (a + b) / 2`

## Step by step explanation

1. Elige un intervalo con cambio de signo.
2. Calcula el punto medio.
3. Evalua la funcion en el punto medio.
4. Conserva el subintervalo con cambio de signo.
5. Repite hasta cumplir la tolerancia.

## Common mistakes

- Empezar sin verificar cambio de signo.
- Pensar que converge rapido en pocas iteraciones.
- Olvidar definir un criterio de parada.

## Mini example

Si `f(1) < 0` y `f(2) > 0`, la raiz esta en `[1, 2]`. El primer punto medio es
`1.5`.

## Related topics

- regula_falsi
- error_iterativo
