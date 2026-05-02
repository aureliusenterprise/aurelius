FROM dhi.io/nginx:1.30-alpine3.22

ARG VERSION=local

# Add image metadata
LABEL org.opencontainers.image.authors="Aurelius Enterprise"
LABEL org.opencontainers.image.description="This is an example frontend application."
LABEL org.opencontainers.image.licenses=UNLICENSED
LABEL org.opencontainers.image.source=https://github.com/aureliusenterprise/project-template
LABEL org.opencontainers.image.title="Aurelius Frontend Example"
LABEL org.opencontainers.image.version="${VERSION}"

# Copy the built application files to the Nginx HTML directory
COPY --chown=root:root --chmod=0755 dist/apps/aurelius-frontend-example/browser /usr/share/nginx/html

# Switch to the nginx user to run the application
USER nginx

# Expose port 8080 for the application
EXPOSE 8080
