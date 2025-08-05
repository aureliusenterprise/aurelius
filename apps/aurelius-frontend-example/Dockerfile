FROM nginx:1.29

# Copy the Nginx configuration file into the container
COPY --chown=root:root --chmod=0755 apps/aurelius-frontend-example/docker/nginx /etc/nginx/templates

# Copy the startup script into the container
COPY --chown=root:root --chmod=0755 apps/aurelius-frontend-example/docker/entrypoint /docker-entrypoint.d

# Copy the built application files to the Nginx HTML directory
COPY --chown=root:root --chmod=0644 dist/apps/aurelius-frontend-example/browser /usr/share/nginx/html

# Periodically check if the Nginx service is running
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD [ "service", "nginx", "status", "||", "exit", "1" ]
