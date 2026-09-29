# Build context = repository root (monorepo convention, see tools/plugins/docker.ts):
#   docker build -f backend/pyatlas/Dockerfile .
FROM python:3.12-slim

# fixed ids: Kubernetes can check runAsNonRoot
RUN addgroup --system --gid 10001 pyatlas && adduser --system --uid 10001 --ingroup pyatlas pyatlas

WORKDIR /app
COPY backend/pyatlas/pyproject.toml backend/pyatlas/README.md backend/pyatlas/LICENSE backend/pyatlas/NOTICE ./
COPY backend/pyatlas/pyatlas ./pyatlas
RUN pip install --no-cache-dir .

COPY backend/pyatlas/models ./models
COPY backend/pyatlas/ui ./ui
COPY backend/pyatlas/conf ./conf
# demo content for a first tenant (PYATLAS_IMPORT_ON_START=/app/sample-data/sample_data.zip, or aurelius-admin
# tenant create ... --sample-data /app/sample-data/sample_data.zip)
COPY backend/m4i-atlas-post-install/data/sample_data.zip backend/m4i-atlas-post-install/data/atlas-dev-quality.json \
     ./sample-data/
RUN mkdir -p /app/data/downloads /app/data/import && chown -R pyatlas:pyatlas /app/data

ENV PYATLAS_MODELS_DIR=/app/models \
    PYATLAS_UI_DIR=/app/ui \
    PYATLAS_USERS_FILE=/app/conf/users-credentials.properties \
    PYATLAS_AUTHZ_POLICY_FILE=/app/conf/atlas-simple-authz-policy.json \
    PYATLAS_DOWNLOAD_DIR=/app/data/downloads \
    PYATLAS_IMPORT_DIR=/app/data/import

USER 10001
EXPOSE 21000
CMD ["python", "-m", "pyatlas", "--host", "0.0.0.0", "--port", "21000"]
