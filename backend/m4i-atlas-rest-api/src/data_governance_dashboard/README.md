# Gov UI Backend

This repository is related to custom atlas backend. Currently, we have implemented below functions.

    - Mapping Dashboard

## Getting started

Enable API 

`uvicorn run:app --reload`

or Run on a particular [port]

`uvicorn run:app --host 0.0.0.0 --port 8000`


## Swagger Docs

check API documentation based on OpenAPI specification at

`127.0.0.1:8000/docs`


## Code Directory

```

├───gov_ui_backend
│   │   __init__.py
│   │
│   ├───app
│   │   │   app.py
│   │   │   __init__.py
│   │   │
│   │   └───routes
│   │           dashboard.py
│   │           __init__.py
│   │
│   ├───core
│   │   │   __init__.py
│   │   │
│   │   ├───details
│   │   │       Details.py
│   │   │       __init__.py
│   │   │
│   │   ├───domains
│   │   │       Domains.py
│   │   │       __init__.py
│   │   │
│   │   ├───response
│   │   │       Response.py
│   │   │       __init__.py
│   │   │
│   │   └───source
│   │           Source.py
│   │           __init__.py
│   │
│   └───parse_entity
│           ParseEntity.py
│           __init__.py
│
├───scripts
│       main.py
│
│
│   .codeclimate.yml
│   .gitignore
│   .gitlab-ci.yml
│   config.py
│   config.sample.py
│   credentials.py
│   credentials.sample.py
│   README.md
│   run.py
│   setup.py
│   store.py
```