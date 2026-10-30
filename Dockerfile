FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY requirements.lock ./

RUN sed '/^-e \.$/d' requirements.lock > /tmp/requirements.lock \
    && python -m pip install --no-cache-dir --default-timeout=180 --retries=10 \
        --extra-index-url https://download.pytorch.org/whl/cpu -r /tmp/requirements.lock \
    && python -m pip install --no-cache-dir --default-timeout=180 --retries=10 \
        "streamlit==1.66.1"

COPY migrations ./migrations
COPY configs ./configs
COPY src ./src

RUN python -m pip install --no-cache-dir --no-deps -e .

EXPOSE 8000

CMD ["uvicorn", "rag_service.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
