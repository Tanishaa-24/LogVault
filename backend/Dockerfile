FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl build-essential ca-certificates \
    && update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=5s --start-period=60s --retries=10 \
  CMD curl -fsS http://localhost:5000/healthz || exit 1

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "--timeout", "60", "app:app"]
