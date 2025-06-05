FROM flink:1.17.0

# Create a non-root user
RUN addgroup --system m4i-publish-state && \
  adduser --system --ingroup m4i-publish-state m4i-publish-state

# Install Python 3.8
RUN apt-get update && \
  apt-get install -y --no-install-recommends software-properties-common && \
  apt-get update && \
  add-apt-repository ppa:deadsnakes/ppa && \
  apt-get update && \
  apt-get install -y --no-install-recommends python3.8 python3.8-distutils && \
  curl -sS https://bootstrap.pypa.io/pip/3.8/get-pip.py | python3.8 && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the wheel file into the container
COPY ../../dist/backend/m4i-publish-state/*.whl .

# Install the wheel file and remove it afterwards
RUN pip3 install --no-cache-dir *.whl && \
  rm *.whl

# Copy the main script into the container
COPY --chown=m4i-publish-state:m4i-publish-state --chmod=0400 backend/m4i-publish-state/main.py .

# Copy the jar files into the container
COPY --chown=m4i-publish-state:m4i-publish-state --chmod=0400 backend/m4i-publish-state/*.jar ./jars/

# Switch to the non-root user
USER m4i-publish-state

# Command to run the application
CMD ["/opt/flink/bin/flink", "run", "-d", "-py", "main.py"]
