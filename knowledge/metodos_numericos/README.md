# Metodos numericos

Bloques iniciales sembrados:

- gestion_del_error
- series_taylor
- raices_de_funciones
- interpolacion
- derivacion_numerica
- integracion_numerica

Bloques incorporados desde `training/data/metodos_numericos/Chapra.pdf`:

- ecuaciones_algebraicas_lineales
- optimizacion
- ajuste_de_curvas
- ecuaciones_diferenciales_ordinarias
- ecuaciones_diferenciales_parciales

Fuente editorial agregada:

- `Chapra.pdf` (Chapra y Canale, quinta edicion en espanol) como apoyo para
  algebra lineal numerica, optimizacion, ajuste de curvas, integracion avanzada,
  EDO y EDP.

Script de sincronizacion:

- `training/scripts/sync_chapra_metodos_topics.py` genera fichas Markdown y
  registros `JSONL` adicionales derivados del libro.

Nota editorial:

- `punto_fijo` se ubico en `raices_de_funciones` porque conceptualmente es un
  metodo iterativo para resolver ecuaciones no lineales.
