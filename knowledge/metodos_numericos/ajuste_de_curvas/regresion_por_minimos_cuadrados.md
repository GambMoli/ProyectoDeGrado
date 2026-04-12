# Regresion por minimos cuadrados

## Metadata

- id: mn_ajuste_regresion_por_minimos_cuadrados
- course: metodos_numericos
- unit: ajuste_de_curvas
- topic: regresion_por_minimos_cuadrados
- subtopic: ajuste_global_con_error_experimental
- content_type: concept_card
- difficulty: medio
- prerequisites: algebra_basica, estadistica_descriptiva
- tags: regresion, minimos_cuadrados, ajuste_de_curvas, datos_experimentales, metodos_numericos
- source: chapra_5ed_es
- book_reference: chapra_capitulo_17

## Learning goal

Entender como ajustar una funcion que capture la tendencia global de datos con
ruido sin exigir que pase exactamente por todos los puntos.

## Formal definition

La regresion por minimos cuadrados elige los parametros de un modelo para
minimizar la suma de los cuadrados de los residuos entre los datos observados y
la curva ajustada.

## Intuition

Cuando los datos tienen error experimental, forzar una interpolacion exacta suele
sobreajustar. La regresion busca un equilibrio entre todos los puntos.

## Why it matters

Permite construir modelos empiricos, calibrar relaciones entre variables y hacer
predicciones mas estables que una interpolacion exacta sobre datos ruidosos.

## Key formulas

- `S_r = sum((y_i - y_modelo_i)^2)`
- `y = a0 + a1 x`
- `a1 = (n sum(x_i y_i) - sum(x_i) sum(y_i)) / (n sum(x_i^2) - (sum(x_i))^2)`
- `a0 = y_prom - a1 x_prom`

## Step by step explanation

1. Elige una familia de modelos.
2. Define los residuos entre datos y modelo.
3. Minimiza la suma de sus cuadrados.
4. Interpreta los parametros obtenidos.
5. Revisa si el ajuste respeta la tendencia fisica del problema.

## Common mistakes

- Confundir regresion con interpolacion exacta.
- Ajustar un modelo complejo sin justificarlo con los datos.
- Usar una recta cuando la relacion exige transformacion o un modelo no lineal.

## Mini example

Si varias mediciones de laboratorio muestran dispersion, una recta por minimos
cuadrados resume mejor la tendencia que un polinomio alto que pase por todos los
datos.

## Related topics

- interpolacion_por_splines
- lagrange
