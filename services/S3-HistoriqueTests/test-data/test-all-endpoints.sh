#!/bin/bash

# Script de test pour tous les endpoints de l'API historique-tests
# Usage: ./test-all-endpoints.sh

BASE_URL="http://localhost:8080"
COMMIT_SHA="abc123def456"
BUILD_ID="build-2024-001"
BRANCH="main"

echo "🚀 Test de tous les endpoints de l'API historique-tests"
echo "========================================================"
echo ""

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher le résultat
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
    echo ""
}

# ======================
# 1. COVERAGE ENDPOINTS
# ======================
echo -e "${BLUE}📊 1. Testing Coverage Endpoints${NC}"
echo "-----------------------------------"

# 1.1 Upload JaCoCo report
echo "1.1. Upload JaCoCo report..."
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/coverage/jacoco" \
  -H "accept: */*" \
  -F "file=@jacoco-sample.xml" \
  -F "commit=$COMMIT_SHA" \
  -F "buildId=$BUILD_ID" \
  -F "branch=$BRANCH")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    print_result 0 "JaCoCo upload successful"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    print_result 1 "JaCoCo upload failed (HTTP $http_code)"
    echo "$body"
fi

# 1.2 Upload PIT mutation report
echo "1.2. Upload PIT mutation report..."
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/coverage/pit" \
  -H "accept: */*" \
  -F "file=@pit-sample.xml" \
  -F "commit=$COMMIT_SHA")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    print_result 0 "PIT upload successful"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    print_result 1 "PIT upload failed (HTTP $http_code)"
    echo "$body"
fi

# 1.3 Get coverage for commit
echo "1.3. Get coverage summary for commit..."
response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/coverage/commit/$COMMIT_SHA" \
  -H "accept: */*")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    print_result 0 "Coverage summary retrieved"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    print_result 1 "Coverage summary failed (HTTP $http_code)"
    echo "$body"
fi

# 1.4 Get coverage history for class
echo "1.4. Get coverage history for UserService..."
response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/coverage/class/com.example.service.UserService" \
  -H "accept: */*")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    print_result 0 "Coverage history retrieved"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    print_result 1 "Coverage history failed (HTTP $http_code)"
    echo "$body"
fi

# 1.5 Get low coverage classes
echo "1.5. Get classes with coverage < 80%..."
response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/coverage/low-coverage?threshold=80" \
  -H "accept: */*")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    print_result 0 "Low coverage classes retrieved"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    print_result 1 "Low coverage query failed (HTTP $http_code)"
    echo "$body"
fi

# ======================
# 2. TEST RESULTS ENDPOINTS
# ======================
echo -e "${BLUE}🧪 2. Testing Test Results Endpoints${NC}"
echo "--------------------------------------"

# 2.1 Upload Surefire report
echo "2.1. Upload Surefire test report..."
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/tests/surefire" \
  -H "accept: */*" \
  -F "file=@surefire-sample.xml" \
  -F "commit=$COMMIT_SHA" \
  -F "buildId=$BUILD_ID" \
  -F "branch=$BRANCH")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    print_result 0 "Surefire upload successful"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    print_result 1 "Surefire upload failed (HTTP $http_code)"
    echo "$body"
fi

# 2.2 Get test summary for commit
echo "2.2. Get test summary for commit..."
response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/tests/commit/$COMMIT_SHA" \
  -H "accept: */*")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    print_result 0 "Test summary retrieved"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    print_result 1 "Test summary failed (HTTP $http_code)"
    echo "$body"
fi

# 2.3 Get failed tests
echo "2.3. Get failed tests for commit..."
response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/tests/failed/$COMMIT_SHA" \
  -H "accept: */*")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    print_result 0 "Failed tests retrieved"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    print_result 1 "Failed tests query failed (HTTP $http_code)"
    echo "$body"
fi

# 2.4 Get test history
echo "2.4. Get test history..."
response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/tests/history/com.example.service.UserServiceTest/testDeleteUser" \
  -H "accept: */*")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    print_result 0 "Test history retrieved"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    print_result 1 "Test history failed (HTTP $http_code)"
    echo "$body"
fi

# ======================
# 3. METRICS ENDPOINTS
# ======================
echo -e "${BLUE}📈 3. Testing Metrics Endpoints${NC}"
echo "--------------------------------"

# 3.1 Get aggregated metrics
echo "3.1. Get aggregated metrics for commit..."
response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/metrics/commit/$COMMIT_SHA" \
  -H "accept: */*")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    print_result 0 "Aggregated metrics retrieved"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    print_result 1 "Aggregated metrics failed (HTTP $http_code)"
    echo "$body"
fi

# ======================
# 4. FLAKINESS ENDPOINTS
# ======================
echo -e "${BLUE}🔄 4. Testing Flakiness Endpoints${NC}"
echo "----------------------------------"

# 4.1 Calculate flakiness
echo "4.1. Calculate flakiness..."
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/flakiness/calculate" \
  -H "accept: */*" \
  -H "Content-Type: application/json")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    print_result 0 "Flakiness calculated"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    print_result 1 "Flakiness calculation failed (HTTP $http_code)"
    echo "$body"
fi

# 4.2 Get most flaky tests
echo "4.2. Get most flaky tests..."
response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/flakiness/most-flaky?limit=10" \
  -H "accept: */*")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    print_result 0 "Most flaky tests retrieved"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    print_result 1 "Most flaky tests query failed (HTTP $http_code)"
    echo "$body"
fi

# 4.3 Get flaky tests
echo "4.3. Get all flaky tests..."
response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/flakiness/flaky" \
  -H "accept: */*")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    print_result 0 "Flaky tests retrieved"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    print_result 1 "Flaky tests query failed (HTTP $http_code)"
    echo "$body"
fi

# ======================
# 5. TEST DEBT ENDPOINTS
# ======================
echo -e "${BLUE}💰 5. Testing Test Debt Endpoints${NC}"
echo "----------------------------------"

# 5.1 Calculate test debt
echo "5.1. Calculate test debt for commit..."
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/debt/calculate/$COMMIT_SHA" \
  -H "accept: */*")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    print_result 0 "Test debt calculated"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    print_result 1 "Test debt calculation failed (HTTP $http_code)"
    echo "$body"
fi

# 5.2 Get high debt classes
echo "5.2. Get classes with high test debt..."
response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/debt/high-debt?threshold=5.0" \
  -H "accept: */*")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    print_result 0 "High debt classes retrieved"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    print_result 1 "High debt query failed (HTTP $http_code)"
    echo "$body"
fi

# 5.3 Get debt summary
echo "5.3. Get debt summary for commit..."
response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/api/debt/commit/$COMMIT_SHA" \
  -H "accept: */*")

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" -eq 200 ]; then
    print_result 0 "Debt summary retrieved"
    echo "$body" | jq . 2>/dev/null || echo "$body"
else
    print_result 1 "Debt summary failed (HTTP $http_code)"
    echo "$body"
fi

echo ""
echo -e "${GREEN}✅ Tests terminés !${NC}"
echo "===================="

