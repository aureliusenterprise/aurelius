# Use the official Python image as a base
FROM python:3.8-slim

# Create a non-root user and group
RUN addgroup --system m4i-data-dictionary-io && \
    adduser --system --ingroup m4i-data-dictionary-io m4i-data-dictionary-io

# Set the working directory
WORKDIR /app

# Copy the wheel file into the container
COPY ../../dist/backend/m4i-data-dictionary-io/*.whl .

# Install the wheel file and remove it afterwards
RUN pip install --no-cache-dir *.whl && \
    rm *.whl

# Copy scripts and data into the container
COPY --chown=m4i-data-dictionary-io:m4i-data-dictionary-io --chmod=0550 apps/m4i-data-dictionary-io/m4i_data_dictionary_io/ /app/bin
# Switch to the non-root user
USER m4i-data-dictionary-io

# Run the main script
CMD ["python __main__.py"]
