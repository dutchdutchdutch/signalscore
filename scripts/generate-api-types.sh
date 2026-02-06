#!/bin/bash
# Generate TypeScript types from backend OpenAPI spec
# 
# Usage: ./scripts/generate-api-types.sh
#
# Requires backend running at http://localhost:8000

set -e

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
OUTPUT_FILE="./execution/frontend/src/lib/api-client/schema.d.ts"

echo "🔄 Generating TypeScript types from OpenAPI spec..."
echo "   Backend: $BACKEND_URL"
echo "   Output: $OUTPUT_FILE"

# Check if backend is reachable
if ! curl -s "$BACKEND_URL/health" > /dev/null; then
    echo "❌ Backend not reachable at $BACKEND_URL"
    echo "   Start the backend first: docker compose up backend"
    exit 1
fi

# Navigate to frontend and run generation
cd "$(dirname "$0")/../execution/frontend"

# Generate types
npx openapi-typescript "$BACKEND_URL/openapi.json" -o src/lib/api-client/schema.d.ts

echo "✅ Types generated successfully!"
echo ""
echo "Types available at: $OUTPUT_FILE"
