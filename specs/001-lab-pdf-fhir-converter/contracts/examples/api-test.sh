#!/bin/bash
# Lab2FHIR API Testing Examples
# Base URL for local development
BASE_URL="http://localhost:8000"

echo "Lab2FHIR API Testing Examples"
echo "=============================="
echo ""

# 1. Create a patient profile
echo "1. Creating patient profile..."
PATIENT_RESPONSE=$(curl -s -X POST "$BASE_URL/api/patients" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "John Doe",
    "patient_type": "human",
    "notes": "Test patient"
  }')

PATIENT_ID=$(echo $PATIENT_RESPONSE | jq -r '.id')
echo "   Created patient with ID: $PATIENT_ID"
echo ""

# 2. List patients
echo "2. Listing all patients..."
curl -s -X GET "$BASE_URL/api/patients" | jq '.items[] | {id, display_name, patient_type}'
echo ""

# 3. Upload a PDF (simulated with placeholder)
echo "3. Uploading lab PDF..."
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/api/uploads" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample-lab-report.pdf" \
  -F "patient_id=$PATIENT_ID")

UPLOAD_ID=$(echo $UPLOAD_RESPONSE | jq -r '.id')
echo "   Created upload with ID: $UPLOAD_ID"
echo "   Status: $(echo $UPLOAD_RESPONSE | jq -r '.status')"
echo ""

# 4. Check upload status
echo "4. Checking upload status..."
curl -s -X GET "$BASE_URL/api/uploads/$UPLOAD_ID" | jq '{id, file_name, status, uploaded_at}'
echo ""

# 5. List all uploads
echo "5. Listing all uploads..."
curl -s -X GET "$BASE_URL/api/uploads?limit=10" | jq '.items[] | {id, file_name, status}'
echo ""

# 6. Get intermediate representation (wait for processing)
echo "6. Retrieving intermediate representation..."
echo "   (Wait for status to be 'review_pending' first)"
# curl -s -X GET "$BASE_URL/api/uploads/$UPLOAD_ID/intermediate" | jq '.'
echo ""

# 7. Edit intermediate representation
echo "7. Editing intermediate representation..."
echo "   (After reviewing and finding an error)"
# curl -s -X PUT "$BASE_URL/api/uploads/$UPLOAD_ID/intermediate" \
#   -H "Content-Type: application/json" \
#   -d @edited-intermediate.json | jq '.'
echo ""

# 8. Generate FHIR bundle
echo "8. Generating FHIR bundle..."
BUNDLE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/uploads/$UPLOAD_ID/generate-fhir" \
  -H "Content-Type: application/json" \
  -d '{}')
echo "   Bundle generated: $(echo $BUNDLE_RESPONSE | jq -r '.id')"
echo ""

# 9. Download FHIR bundle
echo "9. Downloading FHIR bundle..."
curl -s -X GET "$BASE_URL/api/uploads/$UPLOAD_ID/bundle" \
  -H "Accept: application/fhir+json" \
  -o "fhir_bundle_$UPLOAD_ID.json"
echo "   Saved to: fhir_bundle_$UPLOAD_ID.json"
echo ""

# 10. List uploads with filtering
echo "10. Listing completed uploads..."
curl -s -X GET "$BASE_URL/api/uploads?status=completed&limit=5" | jq '.items[] | {id, file_name, status}'
echo ""

echo "=============================="
echo "Testing complete!"
