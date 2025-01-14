# Front end container

This project uses Docker to configure and deploy the Aurelius Atlas web application alongside its landing page, using Apache HTTP Server (httpd).

## Project Structure

- `atlas/`: Contains the main page of the Aurelius Atlas application.

- `htdocs/`: Contains the landing website.

- `conf/`: Holds the main Apache HTTP Server configuration file (httpd.conf).

- `conf.d/`: Contains additional modular configuration files for Apache. These can include virtual host definitions, security settings, or other modular configurations.

- `init/`: Contains initialization scripts. These scripts:

- Rewrite URL paths to include namespaces.

- Replace the Enterprise Search token with the appropriate value.

## Running the Container

The container is intended to be run within the context of the [Helm chart](/k8s/README.md).
