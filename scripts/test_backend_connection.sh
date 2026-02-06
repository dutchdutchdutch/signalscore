#!/bin/bash
# scripts/test_backend_connection.sh

echo "Testing Backend Connection..."
echo "----------------------------"

# 1. Health Check
echo "1. Checking /health..."
HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ "$HEALTH_STATUS" -eq 200 ]; then
    echo "✅ Backend is UP (Status: 200)"
else
    echo "❌ Backend is DOWN or Unreachable (Status: $HEALTH_STATUS)"
    echo "   Ensure uvicorn is running: 'cd execution/backend && source .venv/bin/activate && uvicorn app.main:app --reload'"
    exit 1
fi

# 2. Test specific company (Shopify - expected to be complete or cached)
echo ""
echo "2. Testing GET /api/v1/scores/shopify.com..."
SHOPIFY_RESP=$(curl -s -w "\n%{http_code}" http://localhost:8000/api/v1/scores/shopify.com)
SHOPIFY_BODY=$(echo "$SHOPIFY_RESP" | head -n 1)
SHOPIFY_CODE=$(echo "$SHOPIFY_RESP" | tail -n 1)

if [ "$SHOPIFY_CODE" -eq 200 ]; then
    echo "✅ Shopify score retrieval successful (200)"
elif [ "$SHOPIFY_CODE" -eq 202 ]; then
    echo "⚠️ Shopify is processing (202) - unexpected if it was previously cached"
else
    echo "❌ Failed to retrieve Shopify score (Status: $SHOPIFY_CODE)"
    echo "   Response: $SHOPIFY_BODY"
fi

echo ""
echo "Done."
