FROM nginx:1.29

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This is an example frontend application."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/project-template
LABEL org.opencontainers.image.title="Aurelius Frontend Example"

# Copy the Nginx configuration file into the container
COPY --chown=root:root --chmod=0755 apps/aurelius-frontend-example/docker/nginx /etc/nginx/templates

# Copy the startup script into the container
COPY --chown=root:root --chmod=0755 apps/aurelius-frontend-example/docker/entrypoint /docker-entrypoint.d

# Copy the built application files to the Nginx HTML directory
COPY --chown=root:root --chmod=0644 dist/apps/aurelius-frontend-example/browser /usr/share/nginx/html

# Periodically check if the Nginx service is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD [ "service", "nginx", "status", "||", "exit", "1" ]
