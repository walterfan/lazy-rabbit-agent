#!/bin/bash

# Test script for Admin Multi-Day Recommendations API
# Usage: ./test_admin_multiday.sh

set -e

BASE_URL="http://localhost:8000/api/v1"
ADMIN_EMAIL="walter.fan@gmail.com"  # Update with your admin email
ADMIN_PASSWORD="password"  # Update with your admin password
TARGET_USER_ID=2  # Update with target user ID
CITY_CODE="340100"  # Hefei city code

echo "🧪 Testing Admin Multi-Day Recommendations API"
echo "================================================"
echo ""

# Step 1: Login as admin
echo "📝 Step 1: Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/signin" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\"}")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed. Response:"
  echo "$LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Login successful. Token: ${TOKEN:0:20}..."
echo ""

# Step 2: Generate 3-day recommendations WITHOUT email
echo "📝 Step 2: Generating 3-day recommendations (no email)..."
GEN_RESPONSE=$(curl -s -X POST "${BASE_URL}/admin/recommendations/generate-for-user" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":${TARGET_USER_ID},\"city_code\":\"${CITY_CODE}\",\"send_email\":false}")

echo "$GEN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$GEN_RESPONSE"
echo ""

# Check if successful
if echo "$GEN_RESPONSE" | grep -q '"recommendations"'; then
  echo "✅ 3-day recommendations generated successfully!"
  
  # Extract recommendation count
  REC_COUNT=$(echo "$GEN_RESPONSE" | grep -o '"date_label"' | wc -l | tr -d ' ')
  echo "   - Generated ${REC_COUNT} daily recommendations"
  
  # Extract dates
  echo "   - Dates:"
  echo "$GEN_RESPONSE" | grep -o '"date_label":"[^"]*' | cut -d'"' -f4 | while read label; do
    echo "     • $label"
  done
else
  echo "❌ Failed to generate recommendations"
  exit 1
fi
echo ""

# Step 3: Generate 3-day recommendations WITH email
echo "📝 Step 3: Generating 3-day recommendations (with email)..."
EMAIL_RESPONSE=$(curl -s -X POST "${BASE_URL}/admin/recommendations/generate-for-user" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":${TARGET_USER_ID},\"city_code\":\"${CITY_CODE}\",\"send_email\":true}")

echo "$EMAIL_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$EMAIL_RESPONSE"
echo ""

# Check if email was sent
if echo "$EMAIL_RESPONSE" | grep -q '"email_sent":true'; then
  echo "✅ Email sent successfully!"
else
  echo "⚠️  Email not sent (check email configuration)"
fi
echo ""

# Step 4: Test permission enforcement (non-admin should fail)
echo "📝 Step 4: Testing permission enforcement..."
echo "   (This test requires a regular user account)"
echo "   Skipping for now..."
echo ""

echo "================================================"
echo "✅ All tests completed!"
echo ""
echo "💡 Tips:"
echo "   - Check the database for stored recommendations with forecast_date"
echo "   - Check email inbox if send_email was true"
echo "   - View server logs for detailed execution flow"
echo ""

