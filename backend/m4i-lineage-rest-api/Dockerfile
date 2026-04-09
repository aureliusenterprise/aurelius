# Use the official Python image as a base
FROM python:3.8-slim

# Set environment variables
ENV WSGI_PORT=6969

# Expose the port that the app runs on
EXPOSE ${WSGI_PORT}

# Create a non-root user
RUN addgroup --system m4i-lineage-api && \
  adduser --system --ingroup m4i-lineage-api m4i-lineage-api

# Set the working directory
WORKDIR /app

# Copy the wheel file into the container
COPY --chown=m4i-lineage-api:m4i-lineage-api --chmod=0755 \
  backend/m4i-lineage-rest-api/dist/*.whl \
  backend/m4i-lineage-rest-api/conf.py \
  ./

# Install the wheel file
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
  pip install *.whl

# Switch to the non-root user
USER m4i-lineage-api

# Command to run the application
CMD ["sh", "-c", "m4i_lineage_rest_api:register_get_app() -c /app/conf.py --bind 0.0.0.0:${WSGI_PORT}"]
