# Use the official Python image as a base
FROM python:3.8-slim

# Set environment variables
ENV WSGI_PORT=7200

# Expose the port that the app runs on
EXPOSE ${WSGI_PORT}

# Set the working directory
WORKDIR /app

# Copy the wheel file into the container
COPY ../../dist/backend/m4i-validate-entity/*.whl .

# Install the wheel file and remove it afterwards
RUN pip install --no-cache-dir *.whl && \
  rm *.whl

# Create a non-root user
RUN addgroup --system m4i-validate-entity && \
  adduser --system --ingroup m4i-validate-entity m4i-validate-entity

# Switch to the non-root user
USER m4i-validate-entity

# Command to run the application
CMD ["sh", "-c", "gunicorn m4i_validate_entity:app --bind 0.0.0.0:${WSGI_PORT}"]
