# HydraRoute Agent - AMD Developer Hackathon ACT II
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
RUN mkdir -p /input /output

RUN python -c "import src.config; import src.cache; import src.router; print('Health check: OK')"
CMD ["python", "-m", "src.main"]
