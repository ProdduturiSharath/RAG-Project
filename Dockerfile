FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY requirements.lock ./
COPY migrations ./migrations
COPY src ./src

RUN python -m pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.lock

EXPOSE 8000

CMD ["uvicorn", "rag_service.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
