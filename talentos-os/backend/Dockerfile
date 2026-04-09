FROM python:3.11-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

FROM base AS development
COPY requirements-dev.txt* ./
RUN pip install -r requirements-dev.txt 2>/dev/null || true
COPY . .
RUN mkdir -p logs uploads
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--reload"]

FROM base AS production
COPY . .
RUN mkdir -p logs uploads && addgroup --system appgroup && adduser --system --ingroup appgroup appuser && chown -R appuser:appgroup /app
USER appuser
EXPOSE 5000
CMD ["gunicorn","--bind","0.0.0.0:5000","--workers","4","--worker-class","gevent","--timeout","120","--access-logfile","logs/access.log","--error-logfile","logs/error.log","run:app"]
