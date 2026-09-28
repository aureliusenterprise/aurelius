# Build context = repository root (monorepo convention, see tools/plugins/docker.ts):
#   docker build -f backend/pyatlas/Dockerfile .
FROM python:3.12-slim

RUN addgroup --system pyatlas && adduser --system --ingroup pyatlas pyatlas

WORKDIR /app
COPY backend/pyatlas/pyproject.toml backend/pyatlas/README.md backend/pyatlas/LICENSE backend/pyatlas/NOTICE ./
COPY backend/pyatlas/pyatlas ./pyatlas
RUN pip install --no-cache-dir .

COPY backend/pyatlas/models ./models
COPY backend/pyatlas/ui ./ui
COPY backend/pyatlas/conf ./conf
RUN mkdir -p /app/data/downloads /app/data/import && chown -R pyatlas:pyatlas /app/data

ENV PYATLAS_MODELS_DIR=/app/models \
    PYATLAS_UI_DIR=/app/ui \
    PYATLAS_USERS_FILE=/app/conf/users-credentials.properties \
    PYATLAS_AUTHZ_POLICY_FILE=/app/conf/atlas-simple-authz-policy.json \
    PYATLAS_DOWNLOAD_DIR=/app/data/downloads \
    PYATLAS_IMPORT_DIR=/app/data/import

USER pyatlas
EXPOSE 21000
CMD ["python", "-m", "pyatlas", "--host", "0.0.0.0", "--port", "21000"]
