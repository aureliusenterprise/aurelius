# Development Environment

Follow the steps below to set up your development environment.

This project includes a [development container](https://containers.dev) to automatically set up your development
environment, including the all tools and dependencies required for local development.

!!! NOTE "Prerequisites"

    [Docker](https://www.docker.com) and the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) must be installed on your system to use the development container.

    If you're using **Rancher Desktop**, follow the instructions in the [Rancher Desktop documentation](https://docs.rancherdesktop.io/how-to-guides/vs-code-remote-containers/)
    to prepare your environment for use with the development container.

!!! TIP "Use WSL on Windows"

    If you are using Windows, we **strongly** recommend cloning the repository into the [WSL](https://learn.microsoft.com/en-us/windows/wsl/)
    filesystem instead of the Windows filesystem. This significantly improves I/O performance when running the development container.

## Configure your SSH Key

Follow the steps below to configure your SSH key for accessing the repository:

1. [Generate an SSH key](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent).
2. [Add the SSH key to your GitHub account](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).

## Configure your SSH Agent

The development container will attempt to pick up your SSH key from your `ssh-agent` when it starts. Follow the
guide on [sharing git credentials with the development container](https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials)
to ensure your SSH key is available inside the container.

## Clone the Repository

To clone the repository, run the following command:

```bash
git clone git@github.com:aureliusenterprise/project-template.git
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
    - `connectors`: Provides Kafka connectors and other integration modules for external systems.
    - `docker`: Includes Dockerfiles and resources for building base images used across the workspace.
    - `docs`: Central location for all project documentation, guides, and reference materials.
    - `libs`: Shared libraries and utilities used by multiple applications within the monorepo.
    - `secrets`: Placeholder for secrets management; this folder is excluded from version control.
    - `services`: Deployment manifests and configuration for supporting infrastructure and services.
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
