#!/bin/bash
set -euo pipefail

echo "🚀 Running HydraRoute..."
docker run --platform linux/amd64 \
  -e FIREWORKS_API_KEY="$FIREWORKS_API_KEY" \
  -e FIREWORKS_BASE_URL="${FIREWORKS_BASE_URL:-https://api.fireworks.ai/inference/v1}" \
  -e ALLOWED_MODELS="$ALLOWED_MODELS" \
  -v "$(pwd)/input:/input" \
  -v "$(pwd)/output:/output" \
  hydraroute:latest
echo "✅ Run complete. Results at ./output/results.json"
