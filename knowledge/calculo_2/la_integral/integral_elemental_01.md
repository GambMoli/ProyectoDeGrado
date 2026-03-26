# Ejemplo: Integral Elemental de un Polinomio

## Metadata

- id: calc2_801_elemental_01
- course: calculo_2
- unit: la_integral
- topic: antiderivadas_e_integrales_indefinidas
- subtopic: regla_de_potencia
- content_type: worked_example
- difficulty: basico
- tags: integral_elemental, polinomio, regla_de_potencia, calculo_2
- source: 801_Integrales (1.3)

## Problem

Calcular: `integral (3x^2 + 2x + 1) dx`

## Goal

Mostrar como se usan las formulas fundamentales de integracion para polinomios, aplicando la linealidad de la integral y la regla de la potencia.

## Guided solution

1. Separamos la integral en una suma de integrales usando la propiedad de linealidad:
   `integral (3x^2) dx + integral (2x) dx + integral (1) dx`
2. Sacamos las constantes fuera de las integrales:
   `3 * integral (x^2) dx + 2 * integral (x) dx + integral (1) dx`
3. Aplicamos la regla de la potencia `integral x^n dx = (x^(n+1))/(n+1)` a cada termino:
   - Para x^2: x^3 / 3
   - Para x: x^2 / 2
   - Para 1 (x^0): x
4. Multiplicamos y simplificamos:
   `3 * (x^3 / 3) + 2 * (x^2 / 2) + x + c`
   = `x^3 + x^2 + x + c`

## Interpretation

Como las matematicas son reversibles en este contexto, podemos verificar derivando el resultado:
`d/dx (x^3 + x^2 + x + c)`
`= 3x^2 + 2x + 1`,
que es justamente la funcion original que teniamos.

## Common mistake to avoid

1. Olvidar sumar la constante de intergracion `+ c` al final del proceso. 
2. Elevar la potencia pero olvidar dividir entre la misma potencia `+ 1`.
