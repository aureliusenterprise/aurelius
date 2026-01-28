# Use the official Python image as a base
FROM python:3.8-slim

# Set environment variables
ENV WSGI_PORT=6969

# Expose the port that the app runs on
EXPOSE ${WSGI_PORT}

# Set the working directory
WORKDIR /app

# Copy the wheel file into the container
COPY ../../dist/backend/m4i-lineage-rest-api/*.whl .
# Copy requirements and install pinned Python packages, then the wheel
COPY backend/m4i-lineage-rest-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
  pip install --no-cache-dir *.whl && \
  rm *.whl requirements.txt

# Create a non-root user
RUN addgroup --system m4i-lineage-rest-api && \
  adduser --system --ingroup m4i-lineage-rest-api m4i-lineage-rest-api

# Copy the configuration file into the container
COPY --chown=m4i-lineage-rest-api:m4i-lineage-rest-api backend/m4i-lineage-rest-api/conf.py .

# Switch to the non-root user
USER m4i-lineage-rest-api

# Command to run the application
CMD ["sh", "-c", "m4i_lineage_rest_api:register_get_app() -c /app/conf.py --bind 0.0.0.0:${WSGI_PORT}"]
