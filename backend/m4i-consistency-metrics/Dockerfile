# Use the official Python image as a base
FROM python:3.8-slim

# Set environment variables
ENV WSGI_PORT=7000

# Expose the port that the app runs on
EXPOSE ${WSGI_PORT}

# Set the working directory
WORKDIR /app

# Copy the wheel file into the container
COPY ../../dist/backend/m4i-consistency-metrics/*.whl .

# Install the wheel file and remove it afterwards
RUN pip install --no-cache-dir *.whl && \
  rm *.whl

# Create a non-root user
RUN addgroup --system m4i-consistency-metrics && \
  adduser --system --ingroup m4i-consistency-metrics m4i-consistency-metrics

# Switch to the non-root user
USER m4i-consistency-metrics

# Command to run the application
CMD ["sh", "-c", "gunicorn m4i_consistency_metrics:app --bind 0.0.0.0:${WSGI_PORT}"]
