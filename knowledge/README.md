# Knowledge Corpus for Calculo 1, 2 y Metodos Numericos

Esta carpeta contiene una base inicial de conocimiento para construir un modo
de explicacion teorica con RAG dentro del tutor de calculo.

## Objetivo

El corpus esta pensado para responder preguntas como:

- "Explicame la regla de la cadena"
- "Que significa continuidad uniforme"
- "Como funciona el metodo de biseccion"
- "Que diferencia hay entre trapecios y Simpson 1/3"

No reemplaza el flujo de resolucion simbolica con SymPy. Lo complementa para
explicar temarios, conceptos, teoremas y errores comunes.

## Estructura

```text
knowledge/
├─ templates/
│  ├─ topic_card_template.md
│  ├─ worked_example_template.md
│  ├─ faq_template.md
│  └─ common_mistake_template.md
├─ datasets/
│  ├─ calculo_1_topics.jsonl
│  ├─ calculo_2_topics.jsonl
│  └─ metodos_numericos_topics.jsonl
├─ calculo_1/
├─ calculo_2/
└─ metodos_numericos/
```

## Regla editorial

Cada pieza del corpus debe poder responder estas cuatro preguntas:

1. Que es.
2. Para que sirve.
3. Como se interpreta.
4. En que suele fallar el estudiante.

## Tipos de contenido recomendados

- `concept_card`
- `theorem_card`
- `formula_card`
- `worked_example`
- `common_mistake`
- `faq`

## Metadata minima recomendada

Todos los chunks o registros JSONL deben incluir:

- `id`
- `course`
- `unit`
- `topic`
- `subtopic`
- `content_type`
- `difficulty`
- `tags`
- `text`
- `source`

## Flujo recomendado

1. Escribe o mejora una ficha en Markdown.
2. Convierte esa ficha en uno o varios registros JSONL.
3. Genera embeddings.
4. Guarda embeddings y metadata en PostgreSQL con `pgvector`.
5. Recupera 3 a 5 chunks por consulta teorica.

## Criterios de calidad

- Usa lenguaje claro y academico.
- Separa definicion, intuicion y ejemplo.
- Evita bloques gigantes de texto.
- No mezcles demasiados temas en una misma ficha.
- Anota errores comunes reales.

## Siguiente evolucion sugerida

- Agregar una tabla `knowledge_documents`.
- Agregar una tabla `knowledge_chunks`.
- Crear un indexador que lea esta carpeta y cargue el corpus a la base.
- Crear un `topic_explanation_service` que use recuperacion semantica y Ollama.
