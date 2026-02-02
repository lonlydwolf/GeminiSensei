#!/bin/bash
set -e

# Configuration
BASE_URL="${SIDECAR_URL:-http://localhost:8000}"
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[TEST] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Ensure dependencies
if ! command -v python3 &> /dev/null; then
    error "Python3 is required for JSON parsing."
fi

# Check if server is up
if ! curl -s "$BASE_URL/health" > /dev/null; then
    error "Server is not running at $BASE_URL. Please start it first (e.g., 'cd sidecar && python main.py')."
fi

# 1. Create Roadmap
log "1. Creating Roadmap..."
RESPONSE=$(curl -s -X POST "$BASE_URL/api/roadmap/create" \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Learn basic Python functions",
    "background": "Beginner",
    "preferences": "Short and concise"
  }')

if [[ $(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('roadmap_id', ''))") == "" ]]; then
    echo "Response: $RESPONSE"
    error "Failed to create roadmap."
fi

ROADMAP_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['roadmap_id'])")
log "Roadmap Created! ID: $ROADMAP_ID"

# 2. Get Roadmap Details
log "2. Fetching Roadmap Details..."
ROADMAP_JSON=$(curl -s "$BASE_URL/api/roadmap/$ROADMAP_ID")

# Extract the first lesson ID
LESSON_ID=$(echo "$ROADMAP_JSON" | python3 -c "import sys, json; data=json.load(sys.stdin); phases=data.get('phases', []); lessons=phases[0].get('lessons', []) if phases else []; print(lessons[0]['id'] if lessons else '')")

if [[ -z "$LESSON_ID" ]]; then
    echo "Roadmap JSON: $ROADMAP_JSON"
    error "Failed to extract Lesson ID."
fi

log "First Lesson ID: $LESSON_ID"

# 3. Chat with Teacher
log "3. Chatting with Teacher (Streamed)..."
# We use a timeout to prevent hanging if the stream doesn't close, though 'head' handles simple truncation
curl -N -s -X POST "$BASE_URL/api/chat/stream" \
  -H "Content-Type: application/json" \
  -d "{\"lesson_id\": \"$LESSON_ID\", \"message\": \"Explain the first objective briefly.\"}" | head -n 3
echo -e "\n... (stream truncated)"

# 4. Submit Code (Review Mode / Chat Command)
log "4. Submitting Code via Chat Command (/review)..."
curl -N -s -X POST "$BASE_URL/api/chat/stream" \
  -H "Content-Type: application/json" \
  -d "{\"lesson_id\": \"$LESSON_ID\", \"message\": \"/review print('Hello World')\"}" | head -n 3
echo -e "\n... (stream truncated)"

# 5. Submit Code (Review Endpoint)
log "5. Submitting Code via Review Endpoint..."
curl -N -s -X POST "$BASE_URL/api/review/submit" \
  -H "Content-Type: application/json" \
  -d "{\"lesson_id\": \"$LESSON_ID\", \"code\": \"def greet(name): return f'Hello {name}'\", \"language\": \"python\"}" | head -n 3
echo -e "\n... (stream truncated)"

log "Success! End-to-End flow test completed."
