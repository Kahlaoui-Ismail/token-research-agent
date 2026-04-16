FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default: start the web server.
# Override for the CLI: docker compose run cli python -m agent.main <address>
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
