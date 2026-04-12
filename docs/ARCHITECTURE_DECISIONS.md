# Decisiones de Arquitectura

## 1. Usuario anonimo primero

Se evito una autenticacion compleja en esta primera version. El frontend genera un `user_id` persistente en `localStorage` y el backend crea el registro si no existe. Esto mantiene el historial por navegador sin subir todavia el costo de producto.

## 2. Pipeline desacoplado

El backend separa explicitamente:

- `ocr_service`
- `math_parser_service`
- `sympy_solver_service`
- `explanation_service`
- `conversation_service`

Esto permite cambiar OCR o componentes del flujo conversacional sin romper el resto del sistema.

## 3. Ollama como dependencia obligatoria

El proyecto asume Ollama como base del flujo conversacional. La explicacion teorica, la explicacion pedagogica de ejercicios, la generacion de practica y el enrutamiento interno dependen del modelo, por lo que no se mantiene un modo alterno sin LLM.

## 4. Tesseract como OCR inicial

Se eligio Tesseract porque:

- Tiene costo cero.
- Consume menos RAM que alternativas basadas en modelos pesados.
- Es suficiente para una primera version con fotos simples o ejercicios impresos.

Limitacion documentada: el reconocimiento de notacion matematica compleja todavia puede fallar.

## 5. Persistencia separada por intencion

Se separaron tablas para:

- `users`
- `conversations`
- `messages`
- `exercises`
- `solved_exercises`

Con esto queda trazabilidad entre la entrada original, la extraccion matematica y la salida final.

## 6. Python 3.12 en contenedores

Durante la validacion local aparecio un problema de resolucion de dependencias con Python 3.13 en Windows para `pydantic-core`. Para reducir riesgo operativo, el contenedor del backend quedo fijado en Python 3.12.
