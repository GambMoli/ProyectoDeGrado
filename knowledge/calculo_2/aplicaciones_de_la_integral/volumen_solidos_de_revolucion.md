# Volumen de solidos de revolucion

## Metadata

- id: calc2_aplicaciones_volumen_solidos_de_revolucion
- course: calculo_2
- unit: aplicaciones_de_la_integral
- topic: volumen_solidos_de_revolucion
- subtopic: disco_anillo_y_capa_cilindrica
- content_type: concept_card
- difficulty: medio
- prerequisites: integrales_definidas, area_entre_curvas
- tags: volumen, disco, anillo, capa_cilindrica, calculo_2
- source: corpus_seed_v3

## Learning goal

Entender como calcular volumenes generados al rotar regiones planas alrededor de
un eje.

## Formal definition

Los metodos mas comunes son:

- disco
- anillo
- capa cilindrica

Cada uno modela el volumen con secciones transversales de geometria simple.

## Intuition

Al girar una region, aparecen piezas tridimensionales que pueden sumarse con una
integral si se describe correctamente su radio, espesor o altura.

## Why it matters

Permite resolver problemas geometricos y fisicos de volumen con gran flexibilidad.

## Key formulas

- disco: `V = pi integral R(x)^2 dx`
- anillo: `V = pi integral (R(x)^2 - r(x)^2) dx`
- capa cilindrica: `V = 2 pi integral (radio)(altura) dx`

## Step by step explanation

1. Dibuja la region y el eje de giro.
2. Decide si conviene usar secciones perpendiculares o capas.
3. Identifica radios y alturas.
4. Plantea la integral con el metodo adecuado.

## Common mistakes

- Confundir radio exterior con interior.
- Elegir el metodo sin mirar el eje de rotacion.
- Mezclar variables de integracion y geometria del problema.

## Mini example

Si una region gira alrededor del eje `x`, el metodo de discos usa radios
medidos verticalmente desde el eje.

## Related topics

- area_entre_curvas
- integracion_por_sustitucion_e_integracion_numerica
