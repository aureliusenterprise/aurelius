# Development Environment

Follow the steps below to set up your development environment.

This project includes a [development container](https://containers.dev) to automatically set up your development
environment, including all tools and dependencies required for local development.

!!! NOTE "Prerequisites"

    [Docker](https://www.docker.com) must be installed on your system to use the development container.

!!! TIP "Use WSL on Windows"

    If you are using Windows, we **strongly** recommend cloning the repository into the [WSL](https://learn.microsoft.com/en-us/windows/wsl/)
    filesystem instead of the Windows filesystem. This significantly improves I/O performance when running the development container.

## Configure your SSH Key

Follow the steps below to configure your SSH key for accessing the repository:

1. [Generate an SSH key](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent).
2. [Add the SSH key to your GitHub account](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).

### Configure your SSH Agent

The development container will attempt to pick up your SSH key from your `ssh-agent` when it starts. Follow the
guide on [sharing git credentials with the development container](https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials)
to ensure your SSH key is available inside the container.

!!! TIP "Restart WSL after configuring the SSH agent"

    If you are using WSL on Windows, make sure to restart your WSL instance after configuring the SSH agent to ensure the changes take effect.

## Log into GitHub Container Registry

Aurelius Atlas publishes its Docker images to the GitHub Container Registry. To be able to pull and also publish
images, you need to log into the registry. Run the following command to log in:

```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u <your-github-username> --password-stdin
```

Replace `<your-github-username>` with your GitHub username. The `GITHUB_TOKEN` environment variable should contain
a personal access token with the `read:packages` and `write:packages` scopes.

!!! TIP "Log in once"

    You only need to log in to the container registry once. The credentials will be stored in your Docker configuration and will be available for the development container when it starts.

??? QUESTION "How do I create a personal access token?"

    You can create a personal access token in your GitHub account settings under "Developer settings" > "Personal
    access tokens".

## Clone the Repository

To clone the repository, run the following command:

```bash
git clone git@github.com:aureliusenterprise/aurelius.git
```

This will clone the repository to your local machine using SSH.

## Environment Setup

!!! NOTE "Prerequisites"

    The [Remote Development Extension Pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)
    for Visual Studio Code must be installed to work with development containers.

To get started, navigate to the folder where you cloned the repository and run:

```bash
code .
```

This will open the current directory in Visual Studio Code.

Once Visual Studio Code is open, you will see a notification at the bottom right corner of the window asking if
you want to open the project in a development container. Select `Reopen in Container`.

Your development environment will now be set up automatically.

??? QUESTION "What if I don't see the notification?"

    You can manually open the development container by pressing `F1` to open the command pallette. Type
    `>Dev Containers: Reopen in Container` and press `Enter` to select the command.

??? EXAMPLE "Detailed Setup Guides"

    For more details, refer to the setup guide for your IDE:

    - [Visual Studio Code](https://code.visualstudio.com/docs/devcontainers/tutorial)
    - [PyCharm](https://www.jetbrains.com/help/pycharm/connect-to-devcontainer.html)

## Configure your SOPS Key

Once your development environment is set up, you need to configure your SOPS key, which is used to encrypt and
decrypt the secrets in the repository. Please follow the steps in the [Secrets Management](./secrets-management.md)
guide.

## Explore the Workspace

The workspace is organized as a monorepo, which means that all the projects are stored in a single repository.

??? INFO "Workspace Structure"

    The workspace is divided into the following main directories:

    - `apps`: Contains the main applications and services that make up the workspace.
    - `backend`: Contains backend services and APIs that support the applications in the `apps` directory.
    - `connectors`: Provides Kafka connectors and other integration modules for external systems.
    - `dev`: Contains development infrastructure and configuration files.
    - `docker`: Includes Dockerfiles and resources for building images used across the workspace.
    - `docs`: Central location for all project documentation, guides, and reference materials.
    - `k8s`: Contains the helm chart for deploying the Aurelius Atlas to a Kubernetes cluster.
    - `libs`: Shared libraries and utilities used by multiple applications within the monorepo.
    - `secrets`: Placeholder for secrets management; this folder is excluded from version control.
    - `tools`: Scripts and utilities to assist with development, testing, and deployment workflows.

Workspace automation is managed using [`Nx`](https://nx.dev/). Each project in the workspace has its own set of
configurations and dependencies, allowing for modular development.

!!! TIP "Browse the project graph"

    A great way to start exploring the workspace is to visualize the project graph. You can do this by running the following
    command in the terminal:

    ```bash
    nx graph
    ```

    This will open a new tab in your browser with an interactive graph of the workspace, showing the dependencies
    between the projects. You can click on the nodes to see more details about each project.

## Local Infrastructure

This workspace includes all the necessary services to run the Aurelius Atlas locally, including:

- [Apache Atlas](https://atlas.apache.org) for metadata management.
- [Kafka](https://kafka.apache.org) for event streaming.
- [Schema Registry](https://docs.confluent.io/platform/current/schema-registry/index.html) for managing data schemas.
- [Kafka UI](https://github.com/kafbat/kafka-ui) for managing and monitoring the Kafka cluster.
- [Keycloak](https://www.keycloak.org) for identity and access management.
- [Elasticsearch](https://www.elastic.co/elasticsearch) for search and analytics.
- [Kibana](https://www.elastic.co/kibana) for data visualization and exploration.
- [Enterprise Search](https://www.elastic.co/enterprise-search) for building search experiences.

### Startup

To start the local development infrastructure, run the following command in the terminal:

```bash
nx serve aurelius-atlas-dev
```

This will start the infrastructure services with `docker-compose`.

!!! TIP "Starting individual services"

    You may not always need to start the entire infrastructure. You can start individual services via `docker-compose` as well. For example, to start only the Kafka cluster, run the following command from the root of the repository:

    ```bash
    docker-compose -f dev/docker-compose.yaml up broker schema-registry kafka-ui
    ```

### Initialization

Once the infrastructure is up and running, you need to initialize some of the services before you can start developing.

#### Initialize Atlas Types

Aurelius Atlas uses custom types to represent the metadata in the system. To initialize these types, run the
following command:

```bash
nx run aurelius-atlas-dev:init-atlas-types
```

This will register the custom types with the Atlas instance running in the development environment.

#### Generate Elasticsearch Certificates

To enable secure communication to the Elasticsearch instance, you need to generate SSL certificates. Run the following
command to generate the certificates:

```bash
nx run aurelius-atlas-dev:generate-certs
```

This will generate the necessary SSL certificates and store them in the `dev/certs` directory. This directory
is mounted as a volume in the Elasticsearch container, allowing it to use the certificates for secure communication.

!!! TIP "Automatic Certificate Generation"

    The `generate-certs` target is automatically run when you start the development infrastructure with `nx serve aurelius-atlas-dev`,
    so you don't need to run it manually unless you want to regenerate the certificates.

#### Initialize App Search Engines

Aurelius Atlas uses Enterprise Search to provide search capabilities. To initialize the search engines, run the
following command:

```bash
nx run aurelius-atlas-dev:init-app-search-engines
```

This will create the necessary search engines in Enterprise Search for the Aurelius Atlas application.

#### Upload Sample Data

To upload sample data to the Atlas instance, run the following command:

```bash
nx run aurelius-atlas-dev:upload-sample-data
```

This will upload a set of sample metadata to the Atlas instance, which you can use for testing and development.

!!! TIP "Run the data pipeline first"

    This step only loads the sample metadata into Apache Atlas. To use the full functionality of the Aurelius Atlas, you need to run the data pipeline locally. You can do this by running the following commands in separate terminal windows:

    ```bash
    # Synchronize app search Flink job
    nx run m4i-synchronize-app-search:serve

    # Publish state Flink job
    nx run m4i-publish-state:serve

    # Update gov data quality Flink job
    nx run m4i-update-gov-data-quality:serve

    # Kafka Connect with the Elasticsearch connector
    nx run aurelius-kafka-connect:serve
    ```

#### Update App Search Token

The frontend requires an API token to connect to the Enterprise Search instance. To update the token, run the
following command:

```bash
nx run aurelius-atlas-dev:update-app-search-token
```

This will generate a new API token and update the `environment.ts` file in the frontend project with the new token.

!!! NOTE "Deprecation Notice"

    The `update-app-search-token` target is a temporary solution for managing the API token during development and should be removed as we implement
    an API gateway for Enterprise Search with proper OAuth authentication in the future.
