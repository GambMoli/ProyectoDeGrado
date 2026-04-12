from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_ROOT = ROOT / "knowledge" / "metodos_numericos"
DATASET_PATH = ROOT / "knowledge" / "datasets" / "metodos_numericos_topics.jsonl"
SOURCE = "chapra_5ed_es"
COURSE = "metodos_numericos"

UNIT_IMPORTANCE = {
    "gestion_del_error": (
        "Este bloque ayuda a estimar la confiabilidad de los resultados numericos "
        "y a decidir si una aproximacion ya es aceptable."
    ),
    "raices_de_funciones": (
        "Este bloque es clave para localizar soluciones de ecuaciones no lineales "
        "y para elegir metodos segun robustez o rapidez."
    ),
    "ecuaciones_algebraicas_lineales": (
        "Este bloque aparece en simulacion, diferencias finitas, ajuste de curvas "
        "y muchos otros problemas de ingenieria."
    ),
    "optimizacion": (
        "Este bloque permite encontrar minimos o maximos numericamente cuando no "
        "es practico resolver el problema en forma analitica."
    ),
    "ajuste_de_curvas": (
        "Este bloque sirve para modelar datos experimentales, resumir tendencias y "
        "hacer predicciones utiles."
    ),
    "interpolacion": (
        "Este bloque permite estimar valores intermedios y construir aproximaciones "
        "a partir de datos tabulados."
    ),
    "integracion_numerica": (
        "Este bloque ayuda a aproximar acumulaciones y areas cuando la integral "
        "exacta no esta disponible o los datos son discretos."
    ),
    "derivacion_numerica": (
        "Este bloque permite estimar tasas de cambio con datos tabulados y controlar "
        "mejor los errores de aproximacion."
    ),
    "ecuaciones_diferenciales_ordinarias": (
        "Este bloque modela cambios dinamicos paso a paso y es central en simulacion "
        "cientifica e ingenieril."
    ),
    "ecuaciones_diferenciales_parciales": (
        "Este bloque aproxima fenomenos distribuidos como calor, potencial y "
        "difusion en una o mas dimensiones."
    ),
}

UNIT_LABELS = {
    "gestion_del_error": "Gestion del error",
    "raices_de_funciones": "Raices de funciones",
    "ecuaciones_algebraicas_lineales": "Ecuaciones algebraicas lineales",
    "optimizacion": "Optimizacion",
    "ajuste_de_curvas": "Ajuste de curvas",
    "interpolacion": "Interpolacion",
    "integracion_numerica": "Integracion numerica",
    "derivacion_numerica": "Derivacion numerica",
    "ecuaciones_diferenciales_ordinarias": "Ecuaciones diferenciales ordinarias",
    "ecuaciones_diferenciales_parciales": "Ecuaciones diferenciales parciales",
}


@dataclass(frozen=True)
class TopicCard:
    title: str
    unit: str
    topic: str
    subtopic: str
    difficulty: str
    tags: tuple[str, ...]
    summary: str
    example: str
    book_reference: str
    formulas: tuple[str, ...] = ()
    related: tuple[str, ...] = ()
    prerequisites: tuple[str, ...] = ()
    content_type: str = "concept_card"

    @property
    def markdown_path(self) -> Path:
        return KNOWLEDGE_ROOT / self.unit / f"{self.topic}.md"

    @property
    def markdown_path_str(self) -> str:
        relative = self.markdown_path.relative_to(ROOT)
        return relative.as_posix()

    @property
    def dataset_id(self) -> str:
        unit_prefix = {
            "gestion_del_error": "error",
            "raices_de_funciones": "raices",
            "ecuaciones_algebraicas_lineales": "lineales",
            "optimizacion": "opt",
            "ajuste_de_curvas": "ajuste",
            "interpolacion": "interp",
            "integracion_numerica": "integ",
            "derivacion_numerica": "deriv",
            "ecuaciones_diferenciales_ordinarias": "edo",
            "ecuaciones_diferenciales_parciales": "edp",
        }[self.unit]
        return f"mn_{unit_prefix}_{self.topic}_01"

    def to_dataset_row(self) -> dict:
        return {
            "id": self.dataset_id,
            "course": COURSE,
            "unit": self.unit,
            "topic": self.topic,
            "subtopic": self.subtopic,
            "content_type": self.content_type,
            "difficulty": self.difficulty,
            "tags": list(self.tags),
            "source": SOURCE,
            "markdown_path": self.markdown_path_str,
            "text": self.summary,
        }

    def render_markdown(self) -> str:
        lines = [
            f"# {self.title}",
            "",
            "## Metadata",
            "",
            f"- id: {self.dataset_id.removesuffix('_01')}",
            f"- course: {COURSE}",
            f"- unit: {self.unit}",
            f"- topic: {self.topic}",
            f"- subtopic: {self.subtopic}",
            f"- content_type: {self.content_type}",
            f"- difficulty: {self.difficulty}",
        ]
        if self.prerequisites:
            lines.append(f"- prerequisites: {', '.join(self.prerequisites)}")
        lines.extend(
            [
                f"- tags: {', '.join(self.tags)}",
                f"- source: {SOURCE}",
                f"- book_reference: {self.book_reference}",
                "",
                "## Learning goal",
                "",
                f"Entender {self.title.lower()} y reconocer cuando conviene usarlo dentro del bloque de {UNIT_LABELS[self.unit].lower()}.",
                "",
                "## Formal definition",
                "",
                self.summary,
                "",
                "## Intuition",
                "",
                self.example,
                "",
                "## Why it matters",
                "",
                UNIT_IMPORTANCE[self.unit],
            ]
        )
        if self.formulas:
            lines.extend(["", "## Key formulas", ""])
            lines.extend(f"- `{formula}`" for formula in self.formulas)
        lines.extend(["", "## Mini example", "", self.example])
        if self.related:
            lines.extend(["", "## Related topics", ""])
            lines.extend(f"- {topic}" for topic in self.related)
        lines.append("")
        return "\n".join(lines)


def topic(**kwargs: object) -> TopicCard:
    return TopicCard(**kwargs)


TOPICS: list[TopicCard] = [
    topic(
        title="Propagacion del error",
        unit="gestion_del_error",
        topic="propagacion_del_error",
        subtopic="sensibilidad_y_acumulacion",
        difficulty="medio",
        tags=("propagacion_del_error", "sensibilidad", "errores", "metodos_numericos"),
        summary="La propagacion del error estudia como los errores presentes en datos, parametros o pasos intermedios se transmiten y amplifican en el resultado final de un calculo numerico.",
        example="Si una salida depende de varias mediciones aproximadas, una pequena variacion en cada entrada puede acumularse y cambiar la respuesta final mas de lo esperado.",
        formulas=("delta y ~= (dy/dx) delta x",),
        related=("gestion_del_error", "error_numerico_total"),
        book_reference="chapra_capitulo_4",
    ),
    topic(
        title="Error numerico total",
        unit="gestion_del_error",
        topic="error_numerico_total",
        subtopic="balance_entre_truncamiento_y_redondeo",
        difficulty="medio",
        tags=("error_numerico_total", "truncamiento", "redondeo", "metodos_numericos"),
        summary="El error numerico total combina el error de truncamiento y el error de redondeo, y muestra que reducir el paso no siempre mejora indefinidamente la precision.",
        example="En una derivada numerica, hacer h demasiado grande aumenta truncamiento, pero hacerla demasiado pequena puede disparar el redondeo y empeorar el resultado.",
        related=("gestion_del_error", "propagacion_del_error"),
        book_reference="chapra_capitulo_4",
    ),
    topic(
        title="Incertidumbre en los datos",
        unit="gestion_del_error",
        topic="incertidumbre_en_los_datos",
        subtopic="errores_de_modelo_y_medicion",
        difficulty="basico",
        tags=("incertidumbre", "datos", "medicion", "modelo", "metodos_numericos"),
        summary="La incertidumbre en los datos recuerda que un metodo numerico puede estar bien implementado y aun asi producir una salida limitada por errores de medicion, formulacion o modelo.",
        example="Si la constante usada en un problema experimental viene medida con ruido, ninguna tecnica numerica podra recuperar una exactitud superior a la calidad de ese dato.",
        related=("gestion_del_error", "propagacion_del_error"),
        book_reference="chapra_capitulo_4",
    ),
    topic(
        title="Metodos graficos",
        unit="raices_de_funciones",
        topic="metodos_graficos",
        subtopic="inspeccion_visual_de_raices",
        difficulty="basico",
        tags=("metodos_graficos", "raices", "visualizacion", "metodos_numericos"),
        summary="Los metodos graficos usan la visualizacion de f(x) para detectar cambios de signo, estimar intervalos iniciales y anticipar si hay varias raices o regiones problematicas.",
        example="Graficar una funcion antes de aplicar biseccion ayuda a ver si el intervalo realmente encierra una raiz o si la curva apenas toca el eje.",
        related=("biseccion", "busqueda_por_incrementos"),
        book_reference="chapra_capitulo_5",
    ),
    topic(
        title="Busqueda por incrementos",
        unit="raices_de_funciones",
        topic="busqueda_por_incrementos",
        subtopic="deteccion_de_cambios_de_signo",
        difficulty="basico",
        tags=("busqueda_por_incrementos", "raices", "intervalos", "metodos_numericos"),
        summary="La busqueda por incrementos recorre un dominio con pasos sucesivos para localizar subintervalos donde la funcion cambia de signo y luego aplicar un metodo cerrado.",
        example="Si no conoces un intervalo inicial valido, puedes barrer x desde un valor pequeno hasta otro mayor y registrar donde f(x) pasa de negativa a positiva.",
        related=("biseccion", "regula_falsi"),
        book_reference="chapra_capitulo_5",
    ),
    topic(
        title="Raices multiples",
        unit="raices_de_funciones",
        topic="raices_multiples",
        subtopic="degradacion_de_la_convergencia",
        difficulty="medio",
        tags=("raices_multiples", "newton_raphson", "convergencia", "metodos_numericos"),
        summary="Las raices multiples suelen degradar la rapidez de convergencia de metodos como Newton-Raphson porque la funcion y varias derivadas se vuelven pequenas cerca de la raiz.",
        example="Una funcion que toca el eje sin cruzarlo puede hacer que Newton avance con pasos cortos y pierda la convergencia cuadratica que suele esperarse.",
        related=("newton_raphson", "metodo_de_la_secante"),
        book_reference="chapra_capitulo_6",
    ),
    topic(
        title="Sistemas no lineales",
        unit="raices_de_funciones",
        topic="sistemas_no_lineales",
        subtopic="newton_multivariable",
        difficulty="medio",
        tags=("sistemas_no_lineales", "newton", "jacobiano", "raices", "metodos_numericos"),
        summary="Los sistemas no lineales extienden la busqueda de raices a varias ecuaciones e incognitas, usualmente mediante versiones matriciales de Newton que emplean el jacobiano.",
        example="En dos ecuaciones con dos incognitas, cada iteracion corrige simultaneamente ambas variables resolviendo un sistema lineal asociado al jacobiano.",
        related=("newton_raphson", "eliminacion_de_gauss"),
        book_reference="chapra_capitulo_6",
    ),
    topic(
        title="Metodo de Muller",
        unit="raices_de_funciones",
        topic="metodo_de_muller",
        subtopic="interpolacion_cuadratica_para_raices",
        difficulty="medio",
        tags=("muller", "raices_de_polinomios", "interpolacion", "metodos_numericos"),
        summary="El metodo de Muller aproxima la funcion con una parabola construida a partir de tres puntos y usa la raiz de esa interpolacion cuadratica para producir una nueva estimacion.",
        example="Frente a funciones donde la secante progresa lento, Muller puede capturar mejor la curvatura local y acercarse a la raiz con menos iteraciones.",
        related=("metodo_de_la_secante", "raices_multiples"),
        book_reference="chapra_capitulo_7",
    ),
    topic(
        title="Metodo de Bairstow",
        unit="raices_de_funciones",
        topic="metodo_de_bairstow",
        subtopic="factores_cuadraticos_de_polinomios",
        difficulty="alto",
        tags=("bairstow", "raices_de_polinomios", "factores_cuadraticos", "metodos_numericos"),
        summary="El metodo de Bairstow encuentra pares de raices de un polinomio al ajustar iterativamente factores cuadraticos, por lo que es util cuando se esperan raices reales o complejas conjugadas.",
        example="En un polinomio de grado alto, Bairstow permite ir extrayendo factores cuadraticos y reducir el problema en etapas sucesivas.",
        related=("metodo_de_muller", "descomposicion_lu"),
        book_reference="chapra_capitulo_7",
    ),
    topic(
        title="Gauss-Jordan",
        unit="ecuaciones_algebraicas_lineales",
        topic="gauss_jordan",
        subtopic="reduccion_completa_por_filas",
        difficulty="medio",
        tags=("gauss_jordan", "sistemas_lineales", "matrices", "metodos_numericos"),
        summary="Gauss-Jordan extiende la eliminacion de Gauss para anular tanto por debajo como por encima de la diagonal, con el fin de llevar el sistema a una forma reducida que deje la solucion directamente visible.",
        example="En lugar de terminar con una matriz triangular y usar sustitucion hacia atras, Gauss-Jordan continua hasta dejar la diagonal como unos y el resto como ceros.",
        related=("eliminacion_de_gauss", "matriz_inversa"),
        book_reference="chapra_capitulo_9",
    ),
    topic(
        title="Matrices especiales",
        unit="ecuaciones_algebraicas_lineales",
        topic="matrices_especiales",
        subtopic="bandeadas_simetricas_y_estructura",
        difficulty="medio",
        tags=("matrices_especiales", "bandeadas", "simetricas", "metodos_numericos"),
        summary="Las matrices especiales, como las bandeadas o simetricas, permiten algoritmos mas eficientes porque su estructura reduce operaciones y almacenamiento innecesario.",
        example="Una matriz tridiagonal no necesita tratarse como una matriz llena; aprovechar su forma ahorra tiempo y memoria en cada iteracion.",
        related=("gauss_seidel", "descomposicion_lu"),
        book_reference="chapra_capitulo_11",
    ),
    topic(
        title="Matriz inversa",
        unit="ecuaciones_algebraicas_lineales",
        topic="matriz_inversa",
        subtopic="resolucion_y_analisis_de_sistemas",
        difficulty="medio",
        tags=("matriz_inversa", "sistemas_lineales", "matrices", "metodos_numericos"),
        summary="La matriz inversa convierte formalmente el sistema A x = b en x = A^-1 b, aunque en computacion numerica suele preferirse factorizar o eliminar antes que calcular la inversa explicitamente.",
        example="La inversa ayuda a interpretar el problema y a estudiar sensibilidad, pero para resolver muchos sistemas concretos LU suele ser mas estable y eficiente.",
        formulas=("x = A^-1 b",),
        related=("descomposicion_lu", "condicion_del_sistema"),
        book_reference="chapra_capitulo_10",
    ),
    topic(
        title="Condicion del sistema",
        unit="ecuaciones_algebraicas_lineales",
        topic="condicion_del_sistema",
        subtopic="sensibilidad_a_perturbaciones",
        difficulty="medio",
        tags=("condicion_del_sistema", "sensibilidad", "matrices", "metodos_numericos"),
        summary="La condicion del sistema mide que tan sensible es la solucion de un sistema lineal frente a pequenas perturbaciones en datos o coeficientes.",
        example="Un sistema mal condicionado puede cambiar mucho su solucion ante una variacion minima en b, incluso si el algoritmo numerico esta bien implementado.",
        related=("propagacion_del_error", "matriz_inversa"),
        book_reference="chapra_capitulo_10",
    ),
    topic(
        title="Busqueda de la seccion dorada",
        unit="optimizacion",
        topic="busqueda_de_la_seccion_dorada",
        subtopic="optimizacion_unidimensional_sin_derivadas",
        difficulty="medio",
        tags=("seccion_dorada", "optimizacion", "minimos", "metodos_numericos"),
        summary="La busqueda de la seccion dorada localiza minimos o maximos en una variable usando un intervalo que se reduce con una proporcion fija, sin necesidad de derivadas.",
        example="Si sabes que un costo tiene un unico minimo dentro de un intervalo, la seccion dorada va descartando partes del dominio de manera eficiente y estable.",
        related=("interpolacion_cuadratica_optimizacion", "newton_para_optimizacion"),
        book_reference="chapra_capitulo_13",
    ),
    topic(
        title="Interpolacion cuadratica para optimizacion",
        unit="optimizacion",
        topic="interpolacion_cuadratica_optimizacion",
        subtopic="aproximacion_local_del_extremo",
        difficulty="medio",
        tags=("interpolacion_cuadratica", "optimizacion", "extremos", "metodos_numericos"),
        summary="La interpolacion cuadratica para optimizacion ajusta una parabola local a varios puntos y usa el vertice como nueva aproximacion al extremo buscado.",
        example="Si una funcion es suave cerca de un minimo, una parabola construida con tres evaluaciones puede indicar rapidamente donde se encuentra el siguiente candidato.",
        related=("busqueda_de_la_seccion_dorada", "newton_para_optimizacion"),
        book_reference="chapra_capitulo_13",
    ),
    topic(
        title="Metodo de Newton para optimizacion",
        unit="optimizacion",
        topic="newton_para_optimizacion",
        subtopic="uso_de_derivadas_para_extremos",
        difficulty="medio",
        tags=("newton_optimizacion", "optimizacion", "derivadas", "metodos_numericos"),
        summary="El metodo de Newton para optimizacion busca puntos estacionarios usando primera y segunda derivada, por lo que puede converger muy rapido si el punto inicial es razonable.",
        example="En una funcion convexa, usar f' y f'' cerca del minimo suele dar saltos mas informados que un metodo sin derivadas.",
        formulas=("x_(k+1) = x_k - f'(x_k) / f''(x_k)",),
        related=("busqueda_de_la_seccion_dorada", "metodos_con_gradiente"),
        book_reference="chapra_capitulo_13",
    ),
    topic(
        title="Metodos directos de optimizacion",
        unit="optimizacion",
        topic="metodos_directos_de_optimizacion",
        subtopic="busqueda_sin_gradiente",
        difficulty="medio",
        tags=("metodos_directos", "optimizacion", "sin_gradiente", "metodos_numericos"),
        summary="Los metodos directos de optimizacion avanzan usando solo evaluaciones de la funcion objetivo, de modo que resultan utiles cuando el gradiente no esta disponible o es costoso.",
        example="Si el modelo es una caja negra y solo devuelve el valor del costo, un metodo directo puede explorar direcciones sin derivadas explicitas.",
        related=("busqueda_de_la_seccion_dorada", "metodos_con_gradiente"),
        book_reference="chapra_capitulo_14",
    ),
    topic(
        title="Metodos con gradiente",
        unit="optimizacion",
        topic="metodos_con_gradiente",
        subtopic="descenso_segundo_bloque",
        difficulty="medio",
        tags=("gradiente", "optimizacion", "descenso", "metodos_numericos"),
        summary="Los metodos con gradiente usan la informacion direccional de la derivada para mover la solucion hacia regiones de menor o mayor valor objetivo.",
        example="Si una funcion aumenta en la direccion del gradiente, para minimizarla conviene moverse en la direccion opuesta con un tamano de paso adecuado.",
        formulas=("x_(k+1) = x_k - alpha_k grad f(x_k)",),
        related=("newton_para_optimizacion", "programacion_lineal"),
        book_reference="chapra_capitulo_14",
    ),
    topic(
        title="Programacion lineal",
        unit="optimizacion",
        topic="programacion_lineal",
        subtopic="restricciones_y_funcion_objetivo_lineales",
        difficulty="medio",
        tags=("programacion_lineal", "optimizacion", "restricciones", "metodos_numericos"),
        summary="La programacion lineal optimiza una funcion objetivo lineal sujeta a restricciones lineales y aparece en asignacion de recursos, mezclas y planificacion.",
        example="Un problema de costo minimo con varias fuentes de suministro y limites de capacidad puede formularse como programacion lineal.",
        related=("optimizacion_restringida_no_lineal", "metodos_con_gradiente"),
        book_reference="chapra_capitulo_15",
    ),
    topic(
        title="Optimizacion restringida no lineal",
        unit="optimizacion",
        topic="optimizacion_restringida_no_lineal",
        subtopic="extremos_con_restricciones_no_lineales",
        difficulty="alto",
        tags=("optimizacion_restringida", "no_lineal", "restricciones", "metodos_numericos"),
        summary="La optimizacion restringida no lineal busca extremos respetando restricciones curvas o no lineales, por lo que requiere estrategias mas generales que la programacion lineal.",
        example="Disenar un sistema con relaciones geometricas y fisicas no lineales suele llevar a un problema donde el optimo debe satisfacer varias restricciones simultaneas.",
        related=("programacion_lineal", "newton_para_optimizacion"),
        book_reference="chapra_capitulo_15",
    ),
    topic(
        title="Regresion lineal",
        unit="ajuste_de_curvas",
        topic="regresion_lineal",
        subtopic="ajuste_de_recta_por_minimos_cuadrados",
        difficulty="basico",
        tags=("regresion_lineal", "minimos_cuadrados", "datos", "metodos_numericos"),
        summary="La regresion lineal ajusta la mejor recta a un conjunto de datos al minimizar la suma de cuadrados de los residuos entre observaciones y modelo.",
        example="Si una nube de puntos muestra una tendencia ascendente aproximadamente recta, la regresion lineal resume esa relacion con pendiente e intercepto.",
        formulas=("y = a0 + a1 x",),
        related=("regresion_por_minimos_cuadrados", "regresion_lineal_multiple"),
        book_reference="chapra_capitulo_17",
    ),
    topic(
        title="Regresion polinomial",
        unit="ajuste_de_curvas",
        topic="regresion_polinomial",
        subtopic="ajuste_curvilineo",
        difficulty="medio",
        tags=("regresion_polinomial", "minimos_cuadrados", "datos", "metodos_numericos"),
        summary="La regresion polinomial ajusta un polinomio de grado elegido para capturar curvaturas en datos experimentales sin imponer una interpolacion exacta.",
        example="Si la tendencia sube y luego baja, una parabola por minimos cuadrados puede describir mejor los datos que una recta.",
        related=("regresion_lineal", "regresion_no_lineal"),
        book_reference="chapra_capitulo_17",
    ),
    topic(
        title="Regresion lineal multiple",
        unit="ajuste_de_curvas",
        topic="regresion_lineal_multiple",
        subtopic="varias_variables_independientes",
        difficulty="medio",
        tags=("regresion_lineal_multiple", "minimos_cuadrados", "multivariable", "metodos_numericos"),
        summary="La regresion lineal multiple modela una variable dependiente como combinacion lineal de varias variables independientes.",
        example="Una propiedad fisica puede depender simultaneamente de temperatura y presion, y un modelo lineal multiple ayuda a estimar el peso relativo de cada factor.",
        related=("regresion_lineal", "regresion_no_lineal"),
        book_reference="chapra_capitulo_17",
    ),
    topic(
        title="Regresion no lineal",
        unit="ajuste_de_curvas",
        topic="regresion_no_lineal",
        subtopic="parametros_en_modelos_curvos",
        difficulty="medio",
        tags=("regresion_no_lineal", "ajuste_de_curvas", "parametros", "metodos_numericos"),
        summary="La regresion no lineal ajusta modelos cuyos parametros aparecen de forma no lineal y, por lo general, requiere procesos iterativos de estimacion.",
        example="Un modelo de saturacion o crecimiento exponencial rara vez se ajusta bien con una recta directa y suele necesitar iteraciones para estimar sus parametros.",
        related=("regresion_polinomial", "newton_raphson"),
        book_reference="chapra_capitulo_17",
    ),
    topic(
        title="Aproximacion de Fourier",
        unit="ajuste_de_curvas",
        topic="aproximacion_de_fourier",
        subtopic="componentes_senoidales",
        difficulty="medio",
        tags=("fourier", "aproximacion_de_fourier", "sinusoidales", "metodos_numericos"),
        summary="La aproximacion de Fourier representa una senal o conjunto de datos como suma de componentes sinusoidales con distintas amplitudes y frecuencias.",
        example="Un comportamiento periodico puede entenderse como mezcla de una frecuencia principal y varios armonicos superpuestos.",
        related=("transformada_discreta_de_fourier", "transformada_rapida_de_fourier"),
        book_reference="chapra_capitulo_19",
    ),
    topic(
        title="Transformada discreta de Fourier",
        unit="ajuste_de_curvas",
        topic="transformada_discreta_de_fourier",
        subtopic="analisis_frecuencial_de_datos_muestreados",
        difficulty="medio",
        tags=("tdf", "transformada_discreta_de_fourier", "fourier", "metodos_numericos"),
        summary="La transformada discreta de Fourier descompone una secuencia finita de datos muestreados en sus componentes de frecuencia.",
        example="Si tienes una senal medida en tiempos discretos, la TDF muestra que frecuencias dominan su comportamiento periodico.",
        related=("aproximacion_de_fourier", "transformada_rapida_de_fourier"),
        book_reference="chapra_capitulo_19",
    ),
    topic(
        title="Transformada rapida de Fourier",
        unit="ajuste_de_curvas",
        topic="transformada_rapida_de_fourier",
        subtopic="algoritmo_eficiente_fft",
        difficulty="medio",
        tags=("fft", "transformada_rapida_de_fourier", "fourier", "metodos_numericos"),
        summary="La transformada rapida de Fourier es un algoritmo eficiente para calcular la TDF reduciendo drasticamente el costo computacional del analisis frecuencial.",
        example="En lugar de evaluar todas las combinaciones de la TDF de forma directa, la FFT reorganiza los calculos y acelera mucho el procesamiento de senales.",
        related=("transformada_discreta_de_fourier", "aproximacion_de_fourier"),
        book_reference="chapra_capitulo_19",
    ),
    topic(
        title="Coeficientes del polinomio interpolante",
        unit="interpolacion",
        topic="coeficientes_del_polinomio_interpolante",
        subtopic="representacion_explicita",
        difficulty="medio",
        tags=("coeficientes", "polinomio_interpolante", "interpolacion", "metodos_numericos"),
        summary="Calcular los coeficientes del polinomio interpolante permite expresar la interpolacion en su forma expandida y evaluar o manipular la aproximacion de manera directa.",
        example="Una vez hallados los coeficientes de un polinomio que pasa por ciertos datos, ya no necesitas reconstruir la base de Newton o Lagrange en cada evaluacion.",
        related=("newton", "lagrange"),
        book_reference="chapra_capitulo_18",
    ),
    topic(
        title="Interpolacion inversa",
        unit="interpolacion",
        topic="interpolacion_inversa",
        subtopic="estimacion_de_la_entrada",
        difficulty="medio",
        tags=("interpolacion_inversa", "interpolacion", "datos", "metodos_numericos"),
        summary="La interpolacion inversa estima el valor de la variable independiente que corresponde a una salida dada, invirtiendo el enfoque usual de la interpolacion.",
        example="Si sabes la presion objetivo y tienes una tabla presion-volumen, la interpolacion inversa ayuda a estimar el volumen asociado.",
        related=("newton", "biseccion"),
        book_reference="chapra_capitulo_18",
    ),
    topic(
        title="Integracion con segmentos desiguales",
        unit="integracion_numerica",
        topic="integracion_con_segmentos_desiguales",
        subtopic="datos_no_uniformes",
        difficulty="medio",
        tags=("segmentos_desiguales", "integracion_numerica", "datos", "metodos_numericos"),
        summary="La integracion con segmentos desiguales adapta las formulas de cuadratura cuando los datos no estan espaciados uniformemente en el eje independiente.",
        example="Si una tabla experimental tiene mediciones tomadas a intervalos irregulares, no conviene aplicar sin mas la formula compuesta con h constante.",
        related=("trapecios", "integrales_multiples"),
        book_reference="chapra_capitulo_21",
    ),
    topic(
        title="Formulas de integracion abierta",
        unit="integracion_numerica",
        topic="formulas_de_integracion_abierta",
        subtopic="evitar_extremos_problematicos",
        difficulty="medio",
        tags=("integracion_abierta", "newton_cotes", "integracion_numerica", "metodos_numericos"),
        summary="Las formulas de integracion abierta evitan evaluar la funcion en los extremos del intervalo, lo cual es util cuando esos extremos son singularidades o puntos poco confiables.",
        example="Si f(x) se vuelve muy dificil de evaluar justo en un extremo, una regla abierta usa solo nodos interiores para aproximar la integral.",
        related=("trapecios", "integrales_impropias"),
        book_reference="chapra_capitulo_21",
    ),
    topic(
        title="Integrales multiples",
        unit="integracion_numerica",
        topic="integrales_multiples",
        subtopic="acumulacion_en_varias_dimensiones",
        difficulty="medio",
        tags=("integrales_multiples", "integracion_numerica", "doble_integral", "metodos_numericos"),
        summary="Las integrales multiples extienden la cuadratura numerica a dos o mas dimensiones, usualmente aplicando integracion iterada sobre cada variable.",
        example="Para calcular un promedio sobre una placa rectangular, puedes integrar primero en x para cada y y luego completar la integracion en la otra direccion.",
        related=("integracion_con_segmentos_desiguales", "cuadratura_de_gauss"),
        book_reference="chapra_capitulo_21",
    ),
    topic(
        title="Integrales impropias",
        unit="integracion_numerica",
        topic="integrales_impropias",
        subtopic="limites_infinitos_o_singularidades",
        difficulty="medio",
        tags=("integrales_impropias", "integracion_numerica", "singularidades", "metodos_numericos"),
        summary="Las integrales impropias requieren tratamiento especial porque involucran limites infinitos o integrandos no acotados dentro del intervalo.",
        example="Una integral con una singularidad en un extremo puede reformularse con cambio de variable o con reglas abiertas para evitar evaluar justo en el punto conflictivo.",
        related=("formulas_de_integracion_abierta", "integracion_de_romberg"),
        book_reference="chapra_capitulo_22",
    ),
    topic(
        title="Formulas de diferenciacion de alta exactitud",
        unit="derivacion_numerica",
        topic="formulas_de_diferenciacion_de_alta_exactitud",
        subtopic="esquemas_con_mas_puntos",
        difficulty="medio",
        tags=("alta_exactitud", "derivacion_numerica", "diferencias_finitas", "metodos_numericos"),
        summary="Las formulas de diferenciacion de alta exactitud usan mas puntos del entorno para reducir el error de truncamiento respecto de esquemas basicos progresivos o centrales.",
        example="Un esquema central con varios nodos vecinos suele aproximar mejor una derivada que uno de dos puntos cuando la funcion es suave.",
        related=("primera_derivada", "segunda_derivada"),
        book_reference="chapra_capitulo_23",
    ),
    topic(
        title="Extrapolacion de Richardson",
        unit="derivacion_numerica",
        topic="extrapolacion_de_richardson",
        subtopic="cancelacion_de_error_dominante",
        difficulty="medio",
        tags=("richardson", "derivacion_numerica", "extrapolacion", "metodos_numericos"),
        summary="La extrapolacion de Richardson combina aproximaciones obtenidas con distintos tamanos de paso para cancelar el termino dominante del error y mejorar la precision.",
        example="Si calculas una derivada con h y con h/2, Richardson puede mezclarlas para producir una estimacion mas fina que cualquiera de las dos por separado.",
        related=("integracion_de_romberg", "formulas_de_diferenciacion_de_alta_exactitud"),
        book_reference="chapra_capitulo_23",
    ),
    topic(
        title="Derivadas de datos irregularmente espaciados",
        unit="derivacion_numerica",
        topic="derivadas_de_datos_irregularmente_espaciados",
        subtopic="pasos_no_uniformes",
        difficulty="medio",
        tags=("datos_irregulares", "derivacion_numerica", "diferencias_finitas", "metodos_numericos"),
        summary="Cuando los datos no tienen espaciamiento uniforme, las formulas de derivacion deben adaptarse para incorporar pasos distintos entre nodos consecutivos.",
        example="Una tabla experimental tomada con tiempos desiguales no puede tratarse con la misma formula central que supone h constante.",
        related=("formulas_de_diferenciacion_de_alta_exactitud", "integracion_con_segmentos_desiguales"),
        book_reference="chapra_capitulo_23",
    ),
    topic(
        title="Derivadas e integrales con datos con errores",
        unit="derivacion_numerica",
        topic="derivadas_e_integrales_con_datos_con_errores",
        subtopic="suavizado_y_ruido_experimental",
        difficulty="medio",
        tags=("datos_con_errores", "derivacion_numerica", "integracion_numerica", "metodos_numericos"),
        summary="Derivar o integrar datos con ruido exige cautela porque la diferenciacion suele amplificar errores de medicion y la integracion puede acumular sesgos de los datos.",
        example="Una serie experimental ruidosa puede requerir suavizado o ajuste previo antes de calcular una derivada numerica util.",
        related=("propagacion_del_error", "regresion_por_minimos_cuadrados"),
        book_reference="chapra_capitulo_23",
    ),
    topic(
        title="Mejoras del metodo de Euler",
        unit="ecuaciones_diferenciales_ordinarias",
        topic="mejoras_del_metodo_de_euler",
        subtopic="heun_y_punto_medio",
        difficulty="medio",
        tags=("heun", "punto_medio", "euler_mejorado", "edo", "metodos_numericos"),
        summary="Las mejoras del metodo de Euler, como Heun y el punto medio, usan pendientes adicionales dentro del paso para reducir el error local respecto del esquema basico.",
        example="En vez de usar solo la pendiente al inicio, Heun promedia una pendiente inicial y otra al final estimado del paso.",
        related=("metodo_de_euler", "metodos_de_runge_kutta"),
        book_reference="chapra_capitulo_25",
    ),
    topic(
        title="Sistemas de EDO",
        unit="ecuaciones_diferenciales_ordinarias",
        topic="sistemas_de_edo",
        subtopic="varias_variables_de_estado",
        difficulty="medio",
        tags=("sistemas_de_edo", "edo", "runge_kutta", "metodos_numericos"),
        summary="Los sistemas de EDO modelan varias variables de estado acopladas y se integran actualizando todas las ecuaciones de manera coordinada en cada paso.",
        example="Un modelo depredador-presa o un circuito dinamico no se describe con una sola ecuacion, sino con un conjunto de ecuaciones acopladas.",
        related=("metodos_de_runge_kutta", "gauss_seidel"),
        book_reference="chapra_capitulo_25",
    ),
    topic(
        title="Runge-Kutta adaptativo",
        unit="ecuaciones_diferenciales_ordinarias",
        topic="runge_kutta_adaptativo",
        subtopic="control_automatico_del_paso",
        difficulty="medio",
        tags=("runge_kutta_adaptativo", "edo", "paso_variable", "metodos_numericos"),
        summary="Los metodos adaptativos de Runge-Kutta ajustan automaticamente el tamano de paso para equilibrar precision y costo computacional durante la integracion.",
        example="Si la solucion cambia rapidamente, el metodo reduce h; si la curva es suave, puede aumentarlo para avanzar mas eficientemente.",
        related=("metodos_de_runge_kutta", "rigidez"),
        book_reference="chapra_capitulo_25",
    ),
    topic(
        title="Rigidez",
        unit="ecuaciones_diferenciales_ordinarias",
        topic="rigidez",
        subtopic="escalas_de_tiempo_muy_distintas",
        difficulty="alto",
        tags=("rigidez", "edo", "estabilidad", "metodos_numericos"),
        summary="La rigidez aparece cuando un sistema de EDO mezcla escalas de tiempo muy distintas y obliga a pasos muy pequenos por estabilidad, incluso si la solucion cambia lentamente en apariencia.",
        example="Un sistema quimico puede contener variables que se acomodan casi instantaneamente y otras que evolucionan lento, lo que dificulta usar metodos explicitos simples.",
        related=("runge_kutta_adaptativo", "metodos_de_pasos_multiples"),
        book_reference="chapra_capitulo_26",
    ),
    topic(
        title="Metodos de pasos multiples",
        unit="ecuaciones_diferenciales_ordinarias",
        topic="metodos_de_pasos_multiples",
        subtopic="uso_de_historial_previo",
        difficulty="medio",
        tags=("pasos_multiples", "edo", "adams", "metodos_numericos"),
        summary="Los metodos de pasos multiples reutilizan informacion de varios pasos anteriores para avanzar la solucion con menor costo por iteracion una vez inicializados.",
        example="En lugar de calcular muchas pendientes nuevas como en RK4, un metodo multipaso aprovecha pendientes ya almacenadas del historial reciente.",
        related=("metodos_de_runge_kutta", "rigidez"),
        book_reference="chapra_capitulo_26",
    ),
    topic(
        title="Problemas de valores en la frontera",
        unit="ecuaciones_diferenciales_ordinarias",
        topic="problemas_de_valores_en_la_frontera",
        subtopic="condiciones_en_extremos_distintos",
        difficulty="medio",
        tags=("valores_en_la_frontera", "edo", "frontera", "metodos_numericos"),
        summary="Los problemas de valores en la frontera especifican condiciones en puntos distintos del dominio, por lo que no se resuelven igual que un problema de valor inicial.",
        example="Una barra con temperatura fijada en ambos extremos requiere encontrar una solucion que satisfaga simultaneamente las condiciones de frontera.",
        related=("sistemas_de_edo", "ecuacion_de_laplace"),
        book_reference="chapra_capitulo_27",
    ),
    topic(
        title="Problemas de valores propios",
        unit="ecuaciones_diferenciales_ordinarias",
        topic="problemas_de_valores_propios",
        subtopic="modos_y_parametros_especiales",
        difficulty="alto",
        tags=("valores_propios", "edo", "autovalores", "metodos_numericos"),
        summary="Los problemas de valores propios buscan parametros especiales para los cuales existe una solucion no trivial que satisface ciertas condiciones de frontera.",
        example="En vibraciones, solo ciertas frecuencias producen modos admisibles del sistema y esas frecuencias se interpretan como valores propios.",
        related=("problemas_de_valores_en_la_frontera", "metodo_del_elemento_finito"),
        book_reference="chapra_capitulo_27",
    ),
    topic(
        title="Ecuacion de Laplace",
        unit="ecuaciones_diferenciales_parciales",
        topic="ecuacion_de_laplace",
        subtopic="potenciales_en_equilibrio",
        difficulty="medio",
        tags=("laplace", "edp", "elipticas", "metodos_numericos"),
        summary="La ecuacion de Laplace describe campos en equilibrio, como distribuciones de potencial o temperatura estacionaria sin fuentes internas.",
        example="Una placa en regimen estacionario y sin generacion interna de calor puede modelarse con una ecuacion eliptica de tipo Laplace.",
        related=("metodo_del_volumen_de_control", "ecuacion_de_conduccion_de_calor"),
        book_reference="chapra_capitulo_29",
    ),
    topic(
        title="Metodo del volumen de control",
        unit="ecuaciones_diferenciales_parciales",
        topic="metodo_del_volumen_de_control",
        subtopic="balances_locales_discretizados",
        difficulty="medio",
        tags=("volumen_de_control", "edp", "balances", "metodos_numericos"),
        summary="El metodo del volumen de control discretiza ecuaciones diferenciales aplicando balances sobre pequenos volumenes, lo que preserva de forma natural principios de conservacion.",
        example="En transferencia de calor o masa, cada celda recibe flujos entrantes y salientes que se equilibran con acumulacion o fuentes internas.",
        related=("ecuacion_de_laplace", "metodos_explicitos"),
        book_reference="chapra_capitulo_29",
    ),
    topic(
        title="Ecuacion de conduccion de calor",
        unit="ecuaciones_diferenciales_parciales",
        topic="ecuacion_de_conduccion_de_calor",
        subtopic="dinamica_parabolica",
        difficulty="medio",
        tags=("conduccion_de_calor", "edp", "parabolicas", "metodos_numericos"),
        summary="La ecuacion de conduccion de calor modela la evolucion temporal de la temperatura cuando el calor se difunde en el espacio.",
        example="Si una barra se calienta en un extremo, la distribucion de temperatura cambia con el tiempo siguiendo una EDP parabolica.",
        related=("metodos_explicitos", "crank_nicolson"),
        book_reference="chapra_capitulo_30",
    ),
    topic(
        title="Metodos explicitos para ecuaciones parabolicas",
        unit="ecuaciones_diferenciales_parciales",
        topic="metodos_explicitos",
        subtopic="avance_directo_en_el_tiempo",
        difficulty="medio",
        tags=("metodos_explicitos", "edp", "parabolicas", "metodos_numericos"),
        summary="Los metodos explicitos avanzan la solucion de una EDP usando solo informacion del paso actual, por lo que son faciles de implementar pero sensibles a restricciones de estabilidad.",
        example="En la ecuacion de calor, un esquema explicito actualiza cada nodo con vecinos del tiempo anterior y exige una relacion adecuada entre paso temporal y espacial.",
        related=("ecuacion_de_conduccion_de_calor", "metodo_implicito_simple"),
        book_reference="chapra_capitulo_30",
    ),
    topic(
        title="Metodo implicito simple",
        unit="ecuaciones_diferenciales_parciales",
        topic="metodo_implicito_simple",
        subtopic="estabilidad_mejorada",
        difficulty="medio",
        tags=("metodo_implicito", "edp", "parabolicas", "metodos_numericos"),
        summary="El metodo implicito simple evalua la ecuacion en el nuevo instante de tiempo, lo que mejora estabilidad pero obliga a resolver un sistema lineal en cada paso.",
        example="Frente a un esquema explicito inestable, una formulacion implicita permite usar pasos temporales mas grandes a cambio de mayor trabajo algebraico.",
        related=("metodos_explicitos", "crank_nicolson"),
        book_reference="chapra_capitulo_30",
    ),
    topic(
        title="Crank-Nicolson",
        unit="ecuaciones_diferenciales_parciales",
        topic="crank_nicolson",
        subtopic="promedio_entre_esquemas",
        difficulty="medio",
        tags=("crank_nicolson", "edp", "parabolicas", "metodos_numericos"),
        summary="Crank-Nicolson combina informacion explicita e implicita promediando en el tiempo, con lo que ofrece buen equilibrio entre precision y estabilidad en ecuaciones parabolicas.",
        example="Para la difusion de calor, Crank-Nicolson usa tanto el estado actual como el futuro y suele producir mejores resultados que un esquema completamente explicito.",
        related=("metodos_explicitos", "metodo_implicito_simple"),
        book_reference="chapra_capitulo_30",
    ),
    topic(
        title="Metodo del elemento finito",
        unit="ecuaciones_diferenciales_parciales",
        topic="metodo_del_elemento_finito",
        subtopic="aproximacion_por_elementos",
        difficulty="alto",
        tags=("elemento_finito", "edp", "mallado", "metodos_numericos"),
        summary="El metodo del elemento finito divide el dominio en elementos pequenos y construye una aproximacion global a partir de funciones locales ensambladas.",
        example="En geometria compleja, en lugar de usar una malla rectangular simple, el elemento finito adapta el dominio a triangulos o elementos mas flexibles.",
        related=("ecuacion_de_laplace", "problemas_de_valores_propios"),
        book_reference="chapra_capitulo_31",
    ),
]


def ensure_unit_readmes(cards: list[TopicCard]) -> None:
    grouped: dict[str, list[TopicCard]] = {}
    for card in cards:
        grouped.setdefault(card.unit, []).append(card)

    for unit, topics in grouped.items():
        readme_path = KNOWLEDGE_ROOT / unit / "README.md"
        if readme_path.exists():
            continue
        readme_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"# {UNIT_LABELS.get(unit, unit.replace('_', ' ').title())}", "", "Temas agregados desde `Chapra.pdf`:", ""]
        for card in sorted(topics, key=lambda item: item.topic):
            lines.append(f"- {card.topic}")
        lines.append("")
        readme_path.write_text("\n".join(lines), encoding="utf-8")


def write_markdown_files(cards: list[TopicCard]) -> None:
    for card in cards:
        card.markdown_path.parent.mkdir(parents=True, exist_ok=True)
        card.markdown_path.write_text(card.render_markdown(), encoding="utf-8")


def update_dataset(cards: list[TopicCard]) -> None:
    card_ids = {card.dataset_id for card in cards}
    existing_rows: list[dict] = []
    if DATASET_PATH.exists():
        for raw_line in DATASET_PATH.read_text(encoding="utf-8").splitlines():
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            payload = json.loads(raw_line)
            if payload.get("id") in card_ids:
                continue
            existing_rows.append(payload)

    generated_rows = [card.to_dataset_row() for card in cards]
    generated_rows.sort(key=lambda row: (row["unit"], row["topic"]))
    combined = existing_rows + generated_rows
    text = "\n".join(json.dumps(row, ensure_ascii=False) for row in combined) + "\n"
    DATASET_PATH.write_text(text, encoding="utf-8")


def main() -> None:
    ensure_unit_readmes(TOPICS)
    write_markdown_files(TOPICS)
    update_dataset(TOPICS)
    print(f"Generated {len(TOPICS)} Chapra-derived topic cards.")


if __name__ == "__main__":
    main()
