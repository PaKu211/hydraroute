#!/bin/bash
set -euo pipefail

echo "🔨 Building HydraRoute Docker image for linux/amd64..."
docker build --platform linux/amd64 -t hydraroute:latest .
echo "✅ Build complete: hydraroute:latest"
