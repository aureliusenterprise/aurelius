# aurelius-aws-lambda-base

Hardened Docker base image for Python Lambda functions. This file covers wiring
specific to this project; workspace-wide rules live in the root `AGENTS.md`.

## Layout

- `Dockerfile` — multi-stage: builder installs `awslambdaric` + CloudWatch
  Lambda Insights into `/var/task` / `/opt/cloudwatch`; runtime stage runs as
  `nonroot` with `ENTRYPOINT ["python", "-m", "awslambdaric"]`
- `pyproject.toml` — name/version stub so uv-workspace release versioning bumps
  this image alongside the rest

## Wiring Checklist

- `apps/aurelius-aws-lambda-example/Dockerfile` pins
  `FROM ghcr.io/aureliusenterprise/aurelius-aws-lambda-base:${VERSION}` —
  `nx release` keeps the tag in sync; the handler is that image's `CMD`.
- Docker targets (`docker-build`, `docker-publish`, …) are inferred from the
  `Dockerfile` by the docker plugin.
- The RIC and Insights extension versions are pinned in the `Dockerfile`; bump
  them deliberately (they define the Lambda runtime contract).

## Commands

```bash
nx docker-build aurelius-aws-lambda-base   # VERSION defaults to "local"
```

## Conventions

- Keep the image handler-agnostic: the entrypoint is fixed, the handler always
  comes from the consuming image's `CMD`.
- Never install application dependencies here — that's the app image's job.

## Removal

Part of the AWS Lambda slice. Removing it means rebuilding
`aurelius-aws-lambda-example` on a different base — usually done as part of
removing the whole slice per the root `AGENTS.md` module map.
