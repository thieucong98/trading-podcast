FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install minimal OS dependencies for headless Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY bridge/requirements.txt /app/bridge/requirements.txt
RUN pip install --no-cache-dir -r /app/bridge/requirements.txt
RUN playwright install --with-deps chromium

COPY bridge/ /app/bridge/

EXPOSE 8010

CMD ["uvicorn", "bridge.main:app", "--host", "0.0.0.0", "--port", "8010"]
