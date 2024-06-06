# Use the official Python image as a base
FROM python:3.8-slim

# Set environment variables
ENV WSGI_PORT=7100

# Expose the port that the app runs on
EXPOSE ${WSGI_PORT}

# Set the working directory
WORKDIR /app

# Copy the wheel file into the container
COPY ../../dist/backend/m4i-lineage-model/*.whl .

# Install the wheel file and remove it afterwards
RUN pip install --no-cache-dir *.whl && \
  rm *.whl

# Create a non-root user
RUN addgroup --system m4i-lineage-model && \
  adduser --system --ingroup m4i-lineage-model m4i-lineage-model

# Copy the configuration file into the container
COPY --chown=m4i-lineage-model:m4i-lineage-model backend/m4i-lineage-model/conf.py .

# Switch to the non-root user
USER m4i-lineage-model

# Command to run the application
CMD ["sh", "-c", "gunicorn m4i_lineage_model:app -c /app/conf.py --bind 0.0.0.0:${WSGI_PORT}"]
