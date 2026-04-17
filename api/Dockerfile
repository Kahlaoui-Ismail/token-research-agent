FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Only copy the source packages needed by the API
COPY agent/ ./agent/
COPY api/ ./api/

CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
