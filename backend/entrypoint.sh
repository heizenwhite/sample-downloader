#!/usr/bin/env bash
set -e

# Decode the base64 JSON into the file your app expects
echo "$FIREBASE_KEY_B64" | base64 -d > /app/serviceAccountKey.json

# Hand off to the normal CMD (uvicorn)
exec "$@"
