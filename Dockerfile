# HydraRoute Agent - AMD Developer Hackathon ACT II
# Build: docker build --platform linux/amd64 -t hydraroute:latest .
# Run:   docker run --platform linux/amd64 \
#          -e FIREWORKS_API_KEY=$FIREWORKS_API_KEY \
#          -e ALLOWED_MODELS=$ALLOWED_MODELS \
#          -v $(pwd)/input:/input -v $(pwd)/output:/output \
#          hydraroute:latest

FROM python:3.11-slim

# Set non-interactive mode
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install dependencies first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create output dir (will be overridden by volume mount)
RUN mkdir -p /input /output

# Health check - ensure python can import main
RUN python -c "import src.config; import src.cache; import src.router; print('HydraRoute health check: OK')"

# Run the agent
CMD ["python", "-m", "src.main"]
