# Use the official Python image as a base
FROM python:3.8-slim

# Set environment variables
ENV WSGI_PORT=7200

# Expose the port that the app runs on
EXPOSE ${WSGI_PORT}

# Set the working directory
WORKDIR /app

# Create a non-root user
RUN addgroup --system m4i-validate-entity && \
  adduser --system --ingroup m4i-validate-entity m4i-validate-entity

# Copy the wheel file into the container
COPY --chown=m4i-validate-entity:m4i-validate-entity --chmod=0755 \
  backend/m4i-validate-entity/dist/*.whl \
  ./

# Install the wheel file
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
  pip install *.whl

# Switch to the non-root user
USER m4i-validate-entity

# Command to run the application
CMD ["sh", "-c", "gunicorn m4i_validate_entity:app --bind 0.0.0.0:${WSGI_PORT}"]
