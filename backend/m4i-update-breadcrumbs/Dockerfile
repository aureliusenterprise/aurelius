FROM python:3.8-slim

WORKDIR /app

# Install poetry
RUN pip install poetry==1.4.2

# Copy dependency files
COPY pyproject.toml ./

# Copy local dependencies
COPY ../../libs/m4i-atlas-core /libs/m4i-atlas-core

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Copy application code
COPY . .

# Set the entrypoint
ENTRYPOINT ["python", "main.py"]
