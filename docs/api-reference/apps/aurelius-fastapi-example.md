# aurelius-fastapi-example

[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=aurelius-fastapi-example&metric=sqale_rating&token=93a776fa590fa7579e09418bb96224691c27f7d8)](https://sonarcloud.io/summary/new_code?id=aurelius-fastapi-example)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=aurelius-fastapi-example&metric=reliability_rating&token=93a776fa590fa7579e09418bb96224691c27f7d8)](https://sonarcloud.io/summary/new_code?id=aurelius-fastapi-example)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=aurelius-fastapi-example&metric=security_rating&token=93a776fa590fa7579e09418bb96224691c27f7d8)](https://sonarcloud.io/summary/new_code?id=aurelius-fastapi-example)

This is an example FastAPI application.

## Usage

Run the following command to start the application locally:

```bash
python -m aurelius_fastapi_example
```

This launches a Uvicorn server at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Deployment

Deploy using the provided Dockerfile. By default, the app listens on [http://0.0.0.0:8000](http://0.0.0.0:8000).

## Configuration

Configuration is managed via the [`Settings`][aurelius_fastapi_example.models.Settings] model:

??? INFO "Settings"

    ::: aurelius_fastapi_example.models.Settings

You can set configuration options using environment variables or CLI arguments.

??? TIP "View CLI Arguments"

    To see available CLI options, run:

    ```bash
    python -m aurelius_fastapi_example --help
    ```
