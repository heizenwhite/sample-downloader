# backend/entrypoint.sh
#!/usr/bin/env bash
set -e

# Fetch the Firebase JSON from Secrets Manager into the container
aws secretsmanager get-secret-value \
  --secret-id my-firebase-key \
  --query SecretString --output text \
  > /app/serviceAccountKey.json

# Now run the original CMD (uvicorn ...)
exec "$@"