# Ejemplo: Integracion por Partes (Producto de x y funcion trascendente)

## Metadata

- id: calc2_801_por_partes_01
- course: calculo_2
- unit: tecnicas_de_integracion_e_integrales_impropias
- topic: integracion_por_partes
- subtopic: regla_ILATE
- content_type: worked_example
- difficulty: basico
- tags: integracion_por_partes, ILATE, regla_producto, calculo_2
- source: 801_Integrales

## Problem

Calcular: `integral x * e^x dx`

## Goal

Demostrar la tecnica de integracion por partes `integral u dv = u*v - integral v du` usando la palabra mnemotecnica tipica ILATE (Inversa, Logaritmica, Algebraica, Trigonometrica, Exponencial) para escoger el `u`.

## Guided solution

1. Identificamos los dos factores multiplicandose: uno es Algebraico (`x`) y el otro Exponencial (`e^x`).
2. Segun la regla ILATE, "A" viene antes que "E", por lo que elegimos `u` como la algebraica:
   `u = x`
   Por lo tanto, `dv` sera todo lo restante en la integral:
   `dv = e^x dx`
3. Calculamos `du` derivando `u`, y `v` integrando `dv`:
   - `du = 1 dx`
   - `v = integral e^x dx = e^x`
4. Aplicamos la formula general: `integral u dv = u*v - integral v du`
   `= (x * e^x) - integral (e^x * dx)`
5. Ahora obtenemos una integral comun mas sencilla y la resolvemos de forma elemental:
   `= (x * e^x) - e^x + c`
6. Opcionalmente (y recomendado), factorizamos `e^x` de la ecuacion:
   `= e^x * (x - 1) + c`

## Interpretation

Esta tecnica nos ayuda a simplificar integrales que no tenian ninguna manera directa de resolverse con integrales inmediatas o sustitucion, deshaciendo la regla del producto de las derivadas de manera inversa.

## Common mistake to avoid

Seleccionar equivocadamente las dos partes para el `u` y el `dv`. Por ejemplo, elegir `u = e^x` y `dv = x dx` crearia una integral nueva mas grande (`v = x^2/2`, haciendo mas dificil la cuenta `integral v du`).
