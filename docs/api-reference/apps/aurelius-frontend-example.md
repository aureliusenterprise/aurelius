# aurelius-frontend-example

[![SonarQube Cloud](https://sonarcloud.io/images/project_badges/sonarcloud-light.svg)](https://sonarcloud.io/summary/new_code?id=aurelius-frontend-example)

This is an example frontend application built with Angular.

## Deployment

Deploy using the provided Dockerfile. By default, the app listens on [http://localhost:8080](http://localhost:8080).

## Configuration

The following configuration is required to run the application:

### Client-Facing Configuration

The application is configured at runtime via an externally mounted `config.json` file. This client-facing configuration
file contains the necessary settings for the frontend to communicate with the backend and authentication services.
Below is an example `config.json` file:

```json
{
    "keycloak": {
        "clientId": "aurelius",
        "realm": "master",
        "url": "http://keycloak.localhost:8181"
    }
}
```

Mount the `config.json` file into the container at `/usr/share/nginx/html/config.json` via a Docker volume or
Docker `configs` mechanism.

### Nginx Configuration

The application uses Nginx as a reverse proxy to forward API requests to the Aurelius backend. The Nginx configuration
is **not bundled** in the image; it must be provided externally at runtime.

Mount your `nginx.conf` into the container at `/etc/nginx/conf.d/default.conf` via a Docker volume or Docker
configs` mechanism. Below is an example configuration that serves the static frontend and proxies API requests
to the backend:

```nginx
server {
    listen       8080;
    listen  [::]:8080;
    server_name  localhost;

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }

    location /api/ {
        rewrite ^/api(/.*)$ $1 break;
        proxy_pass http://backend-host:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_redirect off;
    }
}
```

You are free to modify the Nginx configuration as needed, but ensure that API requests are correctly proxied to
the backend and that the static frontend files are served properly.
