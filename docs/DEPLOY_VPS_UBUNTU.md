# Despliegue en VPS Ubuntu

## Requisitos

- Ubuntu 22.04 o 24.04
- 2 vCPU y 4 GB RAM como base razonable para el MVP
- Docker y Docker Compose plugin

## 1. Instalar Docker

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

Abre una sesión nueva después de agregar tu usuario al grupo `docker`.

## 2. Clonar el proyecto

```bash
git clone <tu-repo>
cd <tu-repo>
cp .env.example .env
```

## 3. Configurar variables

Edita `.env` con lo mínimo:

```env
POSTGRES_DB=calc_tutor
POSTGRES_USER=postgres
POSTGRES_PASSWORD=cambia_esta_clave
BACKEND_PORT=8000
FRONTEND_PORT=8080
VITE_API_BASE_URL=http://TU_IP_O_DOMINIO:8000/api
OLLAMA_ENABLED=false
```

Si vas a usar Ollama remoto:

```env
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.2:3b
```

## 4. Levantar el stack

```bash
docker compose up -d --build
```

Verifica:

```bash
docker compose ps
docker compose logs -f backend
```

## 5. Exponer con Nginx opcional

Si quieres publicar con un único punto de entrada:

```bash
docker compose --profile proxy up -d --build
```

Con esto tendrás:

- Frontend y backend detrás de `nginx`
- API accesible por `/api`
- Docs de FastAPI accesibles por `/docs`

## 6. HTTPS recomendado

Opciones simples:

- Poner este stack detrás de un Nginx del host con Certbot.
- Usar un proxy externo como Caddy o Traefik.


## 7. Actualizar la aplicación

```bash
git pull
docker compose up -d --build
```

## 8. Backups mínimos

Base de datos:

```bash
docker exec calc-tutor-db pg_dump -U postgres calc_tutor > backup.sql
```

Volúmenes:

- `postgres_data`
- `ollama_data` si usas el perfil de Ollama

## 9. Observabilidad mínima

Comandos útiles:

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker stats
```

## 10. Recomendaciones de costo

- Empieza sin contenedor de Ollama si el VPS es pequeño.
- Usa el modo de explicación por plantilla mientras validas usuarios.
- Si activas Ollama local, usa un modelo pequeño de 3B o similar.
- Mantén PostgreSQL en el mismo host al inicio para reducir complejidad.
