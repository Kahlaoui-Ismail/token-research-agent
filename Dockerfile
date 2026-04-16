# ── Stage 1: build the React frontend ───────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python API + built frontend ────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Replace the placeholder frontend dir with the compiled Vite output
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Default: start the web server.
# Override for the CLI: docker compose run cli python -m agent.main <address>
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
