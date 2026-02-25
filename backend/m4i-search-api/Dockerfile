# Use the official Python image as a base
FROM python:3.8-slim

# Set environment variables
ENV WSGI_PORT=6970

# Expose the port that the app runs on
EXPOSE ${WSGI_PORT}

# Set the working directory
WORKDIR /app

# Copy the wheel file into the container
COPY ../../dist/backend/m4i-search-api/*.whl .

# Install the wheel file, enforce compatible Werkzeug, then remove wheels
RUN pip install --no-cache-dir *.whl && \
  pip install --no-cache-dir 'werkzeug>=2.1,<3.0' && \
  rm *.whl

# Create a non-root user
RUN addgroup --system m4i-search-api && \
  adduser --system --ingroup m4i-search-api m4i-search-api

# Copy the configuration file into the container
COPY --chown=m4i-search-api:m4i-search-api backend/m4i-search-api/conf.py .

# Switch to the non-root user
USER m4i-search-api

# Command to run the application
CMD ["sh", "-c", "gunicorn 'm4i_search_api:register_get_app()' --bind 0.0.0.0:${WSGI_PORT}"]
