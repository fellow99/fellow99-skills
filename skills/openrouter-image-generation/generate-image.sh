#!/bin/bash
# OpenRouter Image Generation Script
# Usage: ./generate-image.sh "<prompt>" [model] [aspect_ratio] [image_size]
#
# Environment variables:
#   OPENROUTER_BASE_URL  - API base URL (default: https://openrouter.ai/api/v1)
#   OPENROUTER_API_KEY   - API key (required)
#   OPENROUTER_MODEL     - Model name (default: openai/gpt-5.4-image-2)
#
# Windows PowerShell usage:
#   powershell -ExecutionPolicy Bypass -File generate-image.sh "<prompt>" [model] [aspect_ratio] [image_size]

set -e

# ============================================================
# Parameter parsing
# ============================================================
PROMPT="$1"
MODEL="${2:-}"
ASPECT_RATIO="${3:-}"
IMAGE_SIZE="${4:-}"

if [ -z "$PROMPT" ]; then
    echo "Usage: $0 \"<prompt>\" [model] [aspect_ratio] [image_size]"
    echo "Example: $0 \"A beautiful sunset over mountains\" openai/gpt-5.4-image-2 16:9 2K"
    echo ""
    echo "Environment variables:"
    echo "  OPENROUTER_BASE_URL  - API base URL (default: https://openrouter.ai/api/v1)"
    echo "  OPENROUTER_API_KEY   - API key (required)"
    echo "  OPENROUTER_MODEL     - Model name (default: openai/gpt-5.4-image-2)"
    exit 1
fi

# ============================================================
# Configuration
# ============================================================
BASE_URL="${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}"
API_KEY="${OPENROUTER_API_KEY}"
MODEL="${MODEL:-${OPENROUTER_MODEL:-openai/gpt-5.4-image-2}}"

# Validate API Key
if [ -z "$API_KEY" ]; then
    echo "Error: OPENROUTER_API_KEY is not set"
    echo "Please set: export OPENROUTER_API_KEY=\"sk-or-v1-xxx\""
    exit 1
fi

# Remove trailing slash from base URL if present
BASE_URL="${BASE_URL%/}"

# ============================================================
# Build JSON payload
# ============================================================
# Start with required fields
JSON_PAYLOAD="{\"model\":\"$MODEL\",\"messages\":[{\"role\":\"user\",\"content\":\"$PROMPT\"}],\"modalities\":[\"image\",\"text\"]"

# Add image_config if aspect_ratio or image_size is specified
if [ -n "$ASPECT_RATIO" ] || [ -n "$IMAGE_SIZE" ]; then
    JSON_PAYLOAD="$JSON_PAYLOAD,\"image_config\":{"
    if [ -n "$ASPECT_RATIO" ]; then
        JSON_PAYLOAD="$JSON_PAYLOAD\"aspect_ratio\":\"$ASPECT_RATIO\""
    fi
    if [ -n "$ASPECT_RATIO" ] && [ -n "$IMAGE_SIZE" ]; then
        JSON_PAYLOAD="$JSON_PAYLOAD,"
    fi
    if [ -n "$IMAGE_SIZE" ]; then
        JSON_PAYLOAD="$JSON_PAYLOAD\"image_size\":\"$IMAGE_SIZE\""
    fi
    JSON_PAYLOAD="$JSON_PAYLOAD}"
fi

JSON_PAYLOAD="$JSON_PAYLOAD}"

# ============================================================
# Execute API call
# ============================================================
echo "======================================"
echo "OpenRouter Image Generation"
echo "======================================"
echo "Base URL: $BASE_URL"
echo "Model: $MODEL"
echo "Prompt: $PROMPT"
if [ -n "$ASPECT_RATIO" ]; then
    echo "Aspect Ratio: $ASPECT_RATIO"
fi
if [ -n "$IMAGE_SIZE" ]; then
    echo "Image Size: $IMAGE_SIZE"
fi
echo "======================================"
echo "Calling API..."
echo ""

RESPONSE=$(curl --silent --show-error --location --max-time 1800 \
    "$BASE_URL/chat/completions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $API_KEY" \
    -d "$JSON_PAYLOAD")

# ============================================================
# Parse response and save image
# ============================================================
# Check if jq is available
if command -v jq &> /dev/null; then
    # Check for error in response
    ERROR_MSG=$(echo "$RESPONSE" | jq -r '.error.message // empty' 2>/dev/null)
    if [ -n "$ERROR_MSG" ]; then
        echo "======================================"
        echo "API Error"
        echo "======================================"
        echo "Error: $ERROR_MSG"
        echo "Full response:"
        echo "$RESPONSE" | jq .
        exit 1
    fi

    # Extract image data URL
    IMAGE_DATA_URL=$(echo "$RESPONSE" | jq -r '.choices[0].message.images[0].image_url.url // empty' 2>/dev/null)

    if [ -n "$IMAGE_DATA_URL" ]; then
        # Extract base64 data (remove data:image/png;base64, prefix)
        BASE64_DATA=$(echo "$IMAGE_DATA_URL" | sed 's/^data:image\/[a-z]*;base64,//')

        # Generate filename with timestamp
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        OUTPUT_FILE="generated_${TIMESTAMP}.png"

        # Decode and save
        echo "$BASE64_DATA" | base64 -d > "$OUTPUT_FILE"

        echo "======================================"
        echo "Image generated successfully!"
        echo "======================================"
        echo "Saved to: $OUTPUT_FILE"
        echo "======================================"
    else
        echo "======================================"
        echo "No image found in response"
        echo "======================================"
        echo "Full response:"
        echo "$RESPONSE" | jq .
        exit 1
    fi
else
    # Fallback: use python3 for JSON parsing
    if command -v python3 &> /dev/null; then
        IMAGE_DATA_URL=$(echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'error' in data:
    print(f'ERROR:{data[\"error\"].get(\"message\", \"Unknown error\")}')
    sys.exit(1)
try:
    url = data['choices'][0]['message']['images'][0]['image_url']['url']
    print(url)
except (KeyError, IndexError):
    print('NO_IMAGE')
")
        if [[ "$IMAGE_DATA_URL" == ERROR:* ]]; then
            echo "======================================"
            echo "API Error"
            echo "======================================"
            echo "Error: ${IMAGE_DATA_URL#ERROR:}"
            echo "Full response:"
            echo "$RESPONSE" | python3 -m json.tool
            exit 1
        elif [ "$IMAGE_DATA_URL" = "NO_IMAGE" ] || [ -z "$IMAGE_DATA_URL" ]; then
            echo "======================================"
            echo "No image found in response"
            echo "======================================"
            echo "Full response:"
            echo "$RESPONSE" | python3 -m json.tool
            exit 1
        else
            BASE64_DATA=$(echo "$IMAGE_DATA_URL" | sed 's/^data:image\/[a-z]*;base64,//')
            TIMESTAMP=$(date +%Y%m%d_%H%M%S)
            OUTPUT_FILE="generated_${TIMESTAMP}.png"
            echo "$BASE64_DATA" | base64 -d > "$OUTPUT_FILE"
            echo "======================================"
            echo "Image generated successfully!"
            echo "======================================"
            echo "Saved to: $OUTPUT_FILE"
            echo "======================================"
        fi
    else
        echo "======================================"
        echo "Error: Neither jq nor python3 is available"
        echo "Please install jq or python3 for JSON parsing"
        echo "======================================"
        echo "Raw response:"
        echo "$RESPONSE"
        exit 1
    fi
fi
