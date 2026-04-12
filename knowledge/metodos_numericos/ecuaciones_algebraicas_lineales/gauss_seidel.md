# Metodo de Gauss-Seidel

## Metadata

- id: mn_lineales_gauss_seidel
- course: metodos_numericos
- unit: ecuaciones_algebraicas_lineales
- topic: gauss_seidel
- subtopic: iteracion_para_sistemas_lineales
- content_type: concept_card
- difficulty: medio
- prerequisites: algebra_lineal_basica, sistemas_lineales
- tags: gauss_seidel, iterativo, matrices, convergencia, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_11

## Learning goal

Entender como aproximar la solucion de un sistema lineal usando iteraciones que
reutilizan de inmediato los valores mas recientes.

## Formal definition

El metodo de Gauss-Seidel despeja cada ecuacion respecto de una variable y
actualiza `x1, x2, ..., xn` de forma secuencial dentro de cada iteracion,
aprovechando los valores nuevos tan pronto como se calculan.

## Intuition

Cada barrido por el sistema corrige la estimacion anterior. Si la matriz es
favorable, por ejemplo diagonalmente dominante o bien condicionada, las
aproximaciones se acercan a la solucion.

## Why it matters

Es una alternativa a los metodos directos cuando el sistema es grande y conviene
trabajar de manera iterativa, especialmente en problemas provenientes de
diferencias finitas y ecuaciones diferenciales.

## Key formulas

- `x_i^(k+1) = (b_i - sum(a_ij x_j^(k+1)) - sum(a_ij x_j^(k))) / a_ii`
- `i = 1, 2, ..., n`

## Step by step explanation

1. Reescribe cada ecuacion despejando una variable.
2. Elige una aproximacion inicial.
3. Actualiza `x1` con los valores disponibles.
4. Continua con `x2`, `x3` y las demas usando inmediatamente los nuevos datos.
5. Repite hasta que el cambio entre iteraciones sea pequeno.

## Common mistakes

- Usarlo sin revisar si el sistema tiene condiciones razonables de convergencia.
- Confundirlo con Jacobi, que no reutiliza de inmediato los valores nuevos.
- Detenerse por numero fijo de iteraciones sin mirar el error aproximado.

## Mini example

Si al iniciar con ceros se obtiene un nuevo `x1`, ese valor ya se usa al calcular
`x2` dentro de la misma vuelta. Ese detalle suele acelerar la convergencia frente
a otros metodos iterativos basicos.

## Related topics

- eliminacion_de_gauss
- descomposicion_lu
