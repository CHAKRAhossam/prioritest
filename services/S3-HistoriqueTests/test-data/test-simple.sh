#!/bin/bash

# Test simple et rapide des endpoints principaux
BASE_URL="http://localhost:8080"
COMMIT="test-$(date +%s)"

echo "🧪 Test rapide de l'API"
echo "======================="
echo ""

# 1. Upload JaCoCo
echo "1️⃣  Upload JaCoCo report..."
curl -X POST "$BASE_URL/api/coverage/jacoco" \
  -F "file=@jacoco-sample.xml" \
  -F "commit=$COMMIT" \
  -F "buildId=build001" \
  -F "branch=main" | jq .
echo ""

# 2. Upload Surefire
echo "2️⃣  Upload Surefire report..."
curl -X POST "$BASE_URL/api/tests/surefire" \
  -F "file=@surefire-sample.xml" \
  -F "commit=$COMMIT" \
  -F "buildId=build001" \
  -F "branch=main" | jq .
echo ""

# 3. Upload PIT
echo "3️⃣  Upload PIT report..."
curl -X POST "$BASE_URL/api/coverage/pit" \
  -F "file=@pit-sample.xml" \
  -F "commit=$COMMIT" | jq .
echo ""

# 4. Get coverage summary
echo "4️⃣  Get coverage summary..."
curl -X GET "$BASE_URL/api/coverage/commit/$COMMIT" | jq .
echo ""

# 5. Get test summary
echo "5️⃣  Get test summary..."
curl -X GET "$BASE_URL/api/tests/commit/$COMMIT" | jq .
echo ""

# 6. Get aggregated metrics
echo "6️⃣  Get aggregated metrics..."
curl -X GET "$BASE_URL/api/metrics/commit/$COMMIT" | jq .
echo ""

echo "✅ Tests terminés pour commit: $COMMIT"

