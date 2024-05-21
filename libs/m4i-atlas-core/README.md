# M4I Atlas Core

Welcome to the M4I Atlas Core library!

This library is designed to streamline your interactions with Aurelius Atlas, providing a comprehensive data object model for all entities related to Aurelius Atlas and a set of functions to facilitate communication with the Aurelius Atlas API.

With this library, you can easily create, retrieve, and manage Atlas entities, enabling a seamless integration with the Aurelius Atlas Data Governance solution.

In this `README`, you will find detailed instructions on how to install, configure, and use the M4I Atlas Core library to simplify your work with the Aurelius Atlas platform.

- [M4I Atlas Core](#m4i-atlas-core)
  - [Features](#features)
  - [Installation](#installation)
    - [Using the Dev Container](#using-the-dev-container)
      - [Using the Dev Container with Visual Studio Code](#using-the-dev-container-with-visual-studio-code)
      - [Using the Dev Container with GitHub Codespaces](#using-the-dev-container-with-github-codespaces)
    - [Local installation](#local-installation)
  - [How to use](#how-to-use)
    - [Submodules](#submodules)
    - [Authentication](#authentication)
    - [Configuration](#configuration)
      - [Keyloak authentication](#keyloak-authentication)
      - [Atlas authentication](#atlas-authentication)
    - [Example Scripts](#example-scripts)
  - [Testing](#testing)

## Features

The M4I Atlas Core library offers a comprehensive set of features designed to simplify your interactions with the Aurelius Atlas platform. The main features of the library include:

- A rich data object model for all entities related to Aurelius Atlas
- A set of API functions to facilitate communication with the Apache Atlas API
- A centralized configuration store for managing settings and credentials

## Installation

Below are instructions on various ways to install this project.

### Using the Dev Container

This project includes a Visual Studio Code development container to simplify the setup process and provide a consistent development environment. You can use the dev container with either Visual Studio Code locally or with GitHub Codespaces.

#### Using the Dev Container with Visual Studio Code

> **Note**: The following instructions assume that you have already installed [Docker](https://www.docker.com/) and [Visual Studio Code](https://code.visualstudio.com/).

1. Install the [Remote Development extension pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack) in Visual Studio Code.

2. Open the project folder in Visual Studio Code.

3. Press `F1` to open the command palette, and then type "Remote-Containers: Open Folder in Container..." and select it from the list. Alternatively, you can click on the green icon in the bottom-left corner of the VS Code window and select "Reopen in Container" from the popup menu.

4. VS Code will automatically build the container and connect to it. This might take some time for the first run as it downloads the required Docker images and installs extensions.

5. Once connected, you'll see "Dev Container: M4I Atlas Core Dev Container" in the bottom-left corner of the VS Code window, indicating that you are now working inside the container.

6. You're all set! You can now develop, build, and test the project using the provided development environment.

#### Using the Dev Container with GitHub Codespaces

> **Note**: GitHub Codespaces is a paid service. At the time of writing, it offers 60 hours of development time for free every month. Use with care.

1. Ensure that you have access to [GitHub Codespaces](https://github.com/features/codespaces).

2. Navigate to the GitHub repository for the project.

3. Click the "Code" button and then select "Open with Codespaces" from the dropdown menu.

4. Click on the "+ New codespace" button to create a new Codespace for the project.

5. GitHub Codespaces will automatically build the container and connect to it. This might take some time for the first run as it downloads the required Docker images and installs extensions.

6. Once connected, you'll see "Dev Container: M4I Atlas Core Dev Container" in the bottom-left corner of the VS Code window, indicating that you are now working inside the container.

7. You're all set! You can now develop, build, and test the project using the provided development environment.

### Local installation

If you prefer not to use the dev container, you'll need to manually set up your development environment. Please follow the instructions below:

Please ensure your `Python` environment is on version `3.9`. Some dependencies do not work with any previous versions of `Python`.

To install `m4i-atlas-core` and all required dependencies to your active `Python` environment, please run the following command from the project root folder:

```sh
pip install -e . --user
```

To install the project including development dependencies, please run the following command:

```sh
pip install -e .[dev] --user
```

## How to use

This section provides an overview of how to use the M4I Atlas Core library, including configuration options and example scripts to help you get started.

### Submodules

The M4I Atlas Core library consists of several submodules to help you efficiently interact with the Aurelius Atlas platform. Each submodule serves a specific purpose and contains related functionality. Below is a brief description of each submodule:

- [`api`](./m4i_atlas_core/api/README.md): This submodule provides a set of functions that facilitate communication with the Apache Atlas API. It includes functions for creating, retrieving, updating, and deleting entities, as well as handling relationships, classifications, and other aspects of the Aurelius Atlas platform.

- [`config`](./m4i_atlas_core/config/README.md): This submodule includes the `ConfigStore` class, which is responsible for managing configuration settings for the library. It allows you to store, access, and update the configuration settings required to interact with the Atlas API.

- [`entities`](./m4i_atlas_core/entities/atlas/README.md): This submodule contains the data objects related to the Apache Atlas API and the Aurelius Atlas metamodel.

### Authentication

All Aurelius Atlas API endpoints are protected through Keycloak, which requires a valid authentication token for every request. The [`api`](./m4i_atlas_core/api/README.md) module includes functions for retrieving an authentication token from Keycloak. When using API functions, you should pass the authentication token through the `access_token` parameter.

Here's an example of how to authenticate an API request:

```python
from m4i_atlas_core import get_entity_by_guid, get_keycloak_token

access_token = get_keycloak_token()

entity = await get_entity_by_guid("1234", access_token=access_token)
```

Refer to the [Configuration](#configuration) section for details on setting up the required parameters for Keycloak authentication.

### Configuration

Before you begin using any functions from the library, you will need to configure certain parameters and credentials for Atlas.

In the scripts directory, make a copy of `config.sample.py` and `credentials.sample.py` and rename the files to `config.py` and `credentials.py`, respectively. Set the configuration parameters and credentials for Atlas as needed.

> **Note**: When using the Dev Container, the sample files are copied for you automatically. However, you will still have to set the configuration parameters yourself.

| Name               | Required | Description                                                                             |
| ------------------ | -------- | --------------------------------------------------------------------------------------- |
| `atlas.server.url` | True     | The base url for the Apache Atlas API. E.g. `https://www.aurelius-atlas.com/api/atlas`. |

All configuration parameters should to be loaded into the `ConfigStore` on application startup. [Find more detailed documentation about the `ConfigStore` here.](./m4i_atlas_core/config/README.md)

#### Keyloak authentication

When using the default Keycloak authentication, the following additional configuration parameters should be provided:

| Name                            | Required | Description                                                                 |
| ------------------------------- | -------- | --------------------------------------------------------------------------- |
| `keycloak.server.url`           | True     | The url of the Keycloak server. E.g. `https://www.aurelius-atlas.com/auth`. |
| `keycloak.client.id`            | True     | The name of the Keycloak client. The default client id is `m4i_atlas`.      |
| `keycloak.realm.name`           | True     | The name of the Keycloak realm. The default realm name is `m4i`.            |
| `keycloak.client.secret.key`    | True     | The public RS256 key associated with the Keycloak realm.                    |
| `keycloak.credentials.username` | False    | The username of the Keycloak user. The built-in username is `atlas`.        |
| `keycloak.credentials.password` | False    | The password of the Keycloak user.                                          |

> **Note**: Keycloak credentials for built-in Aurelius Atlas users are automatically generated upon deployment and are available from the deployment log.

#### Atlas authentication

When Keycloak authentication is disabled, the default Apache Atlas user management system authenticates all requests. In this case, set the following additional configuration parameters:

| Name                         | Required | Description                                                       |
| ---------------------------- | -------- | ----------------------------------------------------------------- |
| `atlas.credentials.username` | True     | Your username for Apache Atlas. The built-in username is `atlas`. |
| `atlas.credentials.password` | True     | Your password for Apache Atlas.                                   |

### Example Scripts

The library includes example scripts to demonstrate how to interact with the Atlas API using the provided data object models and functions. These scripts can be found in the scripts directory of the project. Below is a brief overview of some example scripts:

- `load_type_defs.py`: This script loads the type definitions into Atlas. The main function in `load_type_defs.py` can be adjusted to determine which set of type definitions to load. Please note that if a subset of the set already exists, the loading of the type definitions will fail.

## Testing

This project uses `pytest` as its unit testing framework.
To run the unit tests, please install `pytest` and then execute the `pytest` command from the project root folder.

Unit tests are grouped per module.
Unit test modules are located in the same folder as their respective covered modules.
They can be recognized by the `test__` module name prefix, followed by the name of the covered module.
