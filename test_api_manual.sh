#!/bin/bash
# Manual API testing script
# This script demonstrates all API endpoints with curl

set -e

API_URL="http://localhost:8000"

echo "=== Smart Workflow Assistant - API Test Script ==="
echo ""
echo "Testing API at: $API_URL"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test 1: Health check
echo -e "${BLUE}1. Health Check${NC}"
curl -s "$API_URL/health" | jq .
echo ""
echo ""

# Test 2: Register a user
echo -e "${BLUE}2. Register User${NC}"
USER_EMAIL="demo@example.com"
USER_PASSWORD="demo123456"

REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$USER_EMAIL\",
    \"password\": \"$USER_PASSWORD\",
    \"role\": \"user\"
  }")

echo $REGISTER_RESPONSE | jq .
USER_ID=$(echo $REGISTER_RESPONSE | jq -r '.id')
echo -e "${GREEN}✓ User registered with ID: $USER_ID${NC}"
echo ""
echo ""

# Test 3: Login
echo -e "${BLUE}3. Login${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$USER_EMAIL\",
    \"password\": \"$USER_PASSWORD\"
  }")

echo $LOGIN_RESPONSE | jq .
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo -e "${GREEN}✓ Logged in, got access token${NC}"
echo ""
echo ""

# Test 4: Create a workflow
echo -e "${BLUE}4. Create Workflow${NC}"
WORKFLOW_RESPONSE=$(curl -s -X POST "$API_URL/workflows/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Workflow"
  }')

echo $WORKFLOW_RESPONSE | jq .
WORKFLOW_ID=$(echo $WORKFLOW_RESPONSE | jq -r '.id')
echo -e "${GREEN}✓ Workflow created with ID: $WORKFLOW_ID${NC}"
echo ""
echo ""

# Test 5: List workflows
echo -e "${BLUE}5. List Workflows${NC}"
curl -s -X GET "$API_URL/workflows/" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""
echo ""

# Test 6: Create steps
echo -e "${BLUE}6. Create Steps${NC}"
STEP1_RESPONSE=$(curl -s -X POST "$API_URL/workflows/$WORKFLOW_ID/steps/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Planning",
    "order": 1,
    "expected_duration_hours": 2.0
  }')

echo "Step 1:"
echo $STEP1_RESPONSE | jq .
STEP1_ID=$(echo $STEP1_RESPONSE | jq -r '.id')

STEP2_RESPONSE=$(curl -s -X POST "$API_URL/workflows/$WORKFLOW_ID/steps/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Implementation",
    "order": 2,
    "expected_duration_hours": 8.0
  }')

echo "Step 2:"
echo $STEP2_RESPONSE | jq .
STEP2_ID=$(echo $STEP2_RESPONSE | jq -r '.id')
echo -e "${GREEN}✓ Created 2 steps${NC}"
echo ""
echo ""

# Test 7: List steps
echo -e "${BLUE}7. List Steps${NC}"
curl -s -X GET "$API_URL/workflows/$WORKFLOW_ID/steps/" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""
echo ""

# Test 8: Create a task
echo -e "${BLUE}8. Create Task${NC}"
TASK_RESPONSE=$(curl -s -X POST "$API_URL/tasks/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"step_id\": $STEP1_ID,
    \"title\": \"Define requirements\",
    \"description\": \"Gather and document all project requirements\"
  }")

echo $TASK_RESPONSE | jq .
TASK_ID=$(echo $TASK_RESPONSE | jq -r '.id')
echo -e "${GREEN}✓ Task created with ID: $TASK_ID${NC}"
echo ""
echo ""

# Test 9: Get task
echo -e "${BLUE}9. Get Task${NC}"
curl -s -X GET "$API_URL/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""
echo ""

# Test 10: Transition task to in_progress
echo -e "${BLUE}10. Transition Task to 'in_progress'${NC}"
curl -s -X POST "$API_URL/tasks/$TASK_ID/transition" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "desired_state": "in_progress"
  }' | jq .
echo -e "${GREEN}✓ Task transitioned to in_progress${NC}"
echo ""
echo ""

# Test 11: Try invalid transition (should fail)
echo -e "${BLUE}11. Try Invalid Transition (in_progress -> pending)${NC}"
INVALID_RESPONSE=$(curl -s -X POST "$API_URL/tasks/$TASK_ID/transition" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "desired_state": "pending"
  }')
echo $INVALID_RESPONSE | jq .
echo -e "${GREEN}✓ Invalid transition correctly rejected${NC}"
echo ""
echo ""

# Test 12: Transition task to done
echo -e "${BLUE}12. Transition Task to 'done'${NC}"
curl -s -X POST "$API_URL/tasks/$TASK_ID/transition" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "desired_state": "done"
  }' | jq .
echo -e "${GREEN}✓ Task completed${NC}"
echo ""
echo ""

# Test 13: Get workflow analytics
echo -e "${BLUE}13. Get Workflow Analytics/Bottlenecks${NC}"
curl -s -X GET "$API_URL/analytics/workflow/$WORKFLOW_ID/bottlenecks" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""
echo ""

echo -e "${GREEN}=== All Tests Completed Successfully! ===${NC}"
echo ""
echo "You can now:"
echo "  - Open http://localhost:8000/docs to explore the API interactively"
echo "  - Test WebSocket at ws://localhost:8000/ws/workflow/$WORKFLOW_ID?token=$TOKEN"
echo ""
