# Ejemplo: Integral por Metodo de Sustitucion (Cambio de Variable)

## Metadata

- id: calc2_801_sustitucion_01
- course: calculo_2
- unit: tecnicas_de_integracion_e_integrales_impropias
- topic: metodo_de_sustitucion
- subtopic: cambio_de_variable
- content_type: worked_example
- difficulty: basico
- tags: sustitucion, cambio_de_variable, calculo_2
- source: 801_Integrales

## Problem

Calcular: `integral 2x * cos(x^2) dx`

## Goal

Mostrar como identificar un termino y su derivada dentro de un integrando continuo, y aplicar el metodo de sustitucion (o cambio de variable) para simplificar la integral.

## Guided solution

1. Observamos que `2x` esta en el integrando, el cual corresponde a la derivada de la expresion interna `x^2`.
2. Elegimos nuestro cambio de variable como `u = x^2`.
3. Calculamos la diferencial que corresponde:
   `du = 2x dx`.
4. Reemplazamos todos los terminos originales (en terminos de x) usando las nuevas variables (en u):
   `integral cos(u) du`
5. Calculamos la integral basica en factor de u. La antiderivada de cos(u) es sin(u).
   `sin(u) + c`
6. Devolvemos la funcion a su variable original, cambiando `u` por `x^2`.
   = `sin(x^2) + c`

## Interpretation

El metodo de sustitucion equivale a aplicar la regla de la cadena de las derivadas, pero en direccion inversa. Buscamos encontrar la funcion original donde derivamos `f(g(x)) * g'(x)`.

## Common mistake to avoid

Olvidar sustituir la variable `u` de vuelta a la variable `x` original dejandolo expresado en `u`. Tambien olvidar derivar el diferencial original (ejemplo derivar pero olvidarse del 2 quedando `x dx = du`).
