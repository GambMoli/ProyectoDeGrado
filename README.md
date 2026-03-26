# Tutor de Calculo con IA

MVP funcional de una plataforma web para estudiantes que resuelve ejercicios de calculo desde texto o imagen, y tambien explica temarios usando un corpus propio con un flujo RAG ligero.

## Stack

- Frontend: React + TypeScript + Vite
- Backend: FastAPI + SQLAlchemy + Alembic
- Base de datos: PostgreSQL
- Motor matematico: SymPy
- OCR: interfaz desacoplada con implementacion inicial en Tesseract
- LLM: Ollama local o remoto
- Contenedores: Docker + Docker Compose
- Proxy opcional: Nginx

## Estructura

```text
.
|- backend
|  |- alembic
|  |- app
|  |- tests
|  `- Dockerfile
|- frontend
|  |- src
|  `- Dockerfile
|- knowledge
|  |- calculo_1
|  |- calculo_2
|  |- metodos_numericos
|  |- datasets
|  `- templates
|- infra
|  `- nginx
|- docs
|  |- ARCHITECTURE_DECISIONS.md
|  `- DEPLOY_VPS_UBUNTU.md
`- docker-compose.yml
```

## Flujo principal

1. El estudiante envia texto o una imagen desde la interfaz tipo chat.
2. El backend crea o reutiliza un usuario anonimo y una conversacion.
3. Si la consulta es teorica, el `intent_router_service` la enruta al modo RAG y el `topic_explanation_service` responde usando el corpus en `knowledge/`.
4. Si la consulta es un ejercicio, el `ocr_service` extrae texto si hace falta, el `math_parser_service` detecta el tipo de problema y el `sympy_solver_service` lo resuelve.
5. El `explanation_service` genera una explicacion pedagogica usando Ollama o una plantilla de respaldo.
6. Se guardan conversacion, mensajes, ejercicio y solucion.
7. El frontend muestra problema detectado, tipo, resultado y explicacion.

## Corpus de teoria

El proyecto incluye una base inicial en [knowledge/README.md](knowledge/README.md) para explicar:

- Calculo 1
- Calculo 2
- Metodos numericos

El corpus trae:

- plantillas Markdown para redactar contenido coherente,
- fichas semilla por curso,
- datasets `JSONL` para recuperacion semantica.

Ejemplos de consultas teoricas:

- `explicame biseccion`
- `que es continuidad de funciones`
- `para que sirve integracion por partes`

Ejemplos de consultas de ejercicio:

- `resuelve 2*x + 3 = 7`
- `integral de x^2 dx`
- `derivada de x^3`

El endpoint `POST /api/chat` acepta un campo opcional `mode` con valores `auto`, `theory` y `exercise`. Si no se envia, el backend detecta el tipo de consulta automaticamente.

Si no detecta un ejercicio claro, el chat no se bloquea: pasa al modo de tutor matematico abierto y mantiene la conversacion dentro del contexto de calculo y metodos numericos.

## Variables de entorno

### Raiz

Copia `.env.example` a `.env` si quieres personalizar puertos o conexion con Ollama.

Variables principales:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `BACKEND_PORT`
- `FRONTEND_PORT`
- `VITE_API_BASE_URL`
- `OLLAMA_ENABLED`
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `OLLAMA_TIMEOUT_SECONDS`
- `OCR_PROVIDER`
- `KNOWLEDGE_DATASETS_DIR`
- `RAG_TOP_K`

### Backend

Referencia: [backend/.env.example](backend/.env.example)

Variables clave:

- `DATABASE_URL`
- `CORS_ORIGINS`
- `OLLAMA_ENABLED`
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `OCR_PROVIDER`
- `OCR_LANGUAGE`
- `MAX_UPLOAD_SIZE_MB`
- `KNOWLEDGE_DATASETS_DIR`
- `RAG_TOP_K`

### Frontend

Referencia: [frontend/.env.example](frontend/.env.example)

- `VITE_API_BASE_URL`

## Ejecutar con Docker

### Modo recomendado para desarrollo local

```bash
docker compose up --build
```

Servicios:

- Frontend: `http://localhost:8080`
- Backend: `http://localhost:8000`
- OpenAPI: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

### Activar Ollama

Si ya tienes Ollama corriendo fuera del stack:

```env
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2:3b
```

Si quieres levantar el contenedor opcional:

```bash
docker compose --profile ollama up --build
```

### Activar Nginx

```bash
docker compose --profile proxy up --build
```

## Ejecucion local sin Docker

### Backend

Recomendado: Python 3.12.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Endpoints principales

- `POST /api/chat`
- `POST /api/upload-exercise-image`
- `GET /api/conversations`
- `GET /api/conversations/{id}`
- `GET /api/health`

Documentacion automatica:

- `/docs`
- `/redoc`

## Estado del MVP

Casos implementados en SymPy:

- derivadas basicas,
- integrales basicas,
- simplificacion algebraica,
- ecuaciones simples,
- limites en formato textual basico.

Comportamientos de error:

- mensaje claro si el OCR falla,
- mensaje claro si el parser no entiende el ejercicio,
- mensaje claro si SymPy no logra resolver el caso,
- mensaje claro si el corpus teorico no tiene suficiente contexto todavia.

## Verificacion realizada

- compilacion sintactica del backend con `python -m compileall`,
- pruebas del nucleo matematico y del RAG ligero sobre el corpus,
- compilacion de produccion del frontend con `npm run build`.

## Decisiones de arquitectura

- Se usa un usuario anonimo simple almacenado en `localStorage` para evitar una capa de autenticacion prematura.
- El OCR esta detras de una interfaz; Tesseract es la implementacion inicial por costo y RAM moderados.
- La explicacion no depende obligatoriamente de Ollama: si el modelo no esta disponible, el sistema usa una explicacion base para no romper el MVP.
- `messages`, `exercises` y `solved_exercises` estan separados para conservar trazabilidad entre entrada, extraccion matematica y salida final.
- El backend usa Python 3.12 en Docker por estabilidad del stack FastAPI/Pydantic.

Mas detalle: [docs/ARCHITECTURE_DECISIONS.md](docs/ARCHITECTURE_DECISIONS.md)

## Mejoras futuras

- autenticacion real con cuentas y sesiones,
- parser mas robusto para lenguaje natural y notacion matematica mixta,
- OCR especializado en formulas con proveedor alterno como Pix2Text,
- recuperacion semantica con embeddings y `pgvector`,
- simulacros de examen con banco de preguntas y correccion automatica,
- streaming de respuesta,
- tests de integracion API + UI + base de datos.

## Despliegue en VPS Ubuntu

La guia paso a paso esta en [docs/DEPLOY_VPS_UBUNTU.md](docs/DEPLOY_VPS_UBUNTU.md).
