# Decisiones de Arquitectura

## 1. Usuario anónimo primero

Se evitó una autenticación compleja en esta primera versión. El frontend genera un `user_id` persistente en `localStorage` y el backend crea el registro si no existe. Esto mantiene el historial por navegador sin subir todavía el costo de producto.

## 2. Pipeline desacoplado

El backend separa explícitamente:

- `ocr_service`
- `math_parser_service`
- `sympy_solver_service`
- `explanation_service`
- `conversation_service`

Esto permite cambiar OCR o LLM sin romper el resto del flujo.

## 3. Explicación con degradación elegante

Ollama es opcional. Si el modelo no responde o está apagado, el sistema usa una explicación derivada de la salida de SymPy. Así el MVP sigue siendo funcional y barato en VPS pequeños.

## 4. Tesseract como OCR inicial

Se eligió Tesseract porque:

- Tiene costo cero.
- Consume menos RAM que alternativas basadas en modelos pesados.
- Es suficiente para una primera versión con fotos simples o ejercicios impresos.

Limitación documentada: el reconocimiento de notación matemática compleja todavía puede fallar.

## 5. Persistencia separada por intención

Se separaron tablas para:

- `users`
- `conversations`
- `messages`
- `exercises`
- `solved_exercises`

Con esto queda trazabilidad entre la entrada original, la extracción matemática y la salida final.

## 6. Python 3.12 en contenedores

Durante la validación local apareció un problema de resolución de dependencias con Python 3.13 en Windows para `pydantic-core`. Para reducir riesgo operativo, el contenedor del backend quedó fijado en Python 3.12.
