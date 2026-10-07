# aurelius-license-report

Workspace-level license report generator. This file covers wiring specific to
this project; workspace-wide rules live in the root `AGENTS.md`.

## Layout

- `aurelius_license_report/` — the package (`python -m aurelius_license_report`)
  with Jinja2 templates
- `project.json` — `build` and `package` targets
- `dist/` — generated HTML reports (gitignored); `package` zips them

## Wiring Checklist

- `build` depends on `decrypt` (SOPS) and `docker-license-scan` on every
  Docker-tagged project — it aggregates the `licenses.json` files those scans
  drop into each project directory.
- New Docker projects are picked up automatically via the
  `{ projects: "tag:docker", target: "docker-license-scan" }` dependency, as
  long as they produce `licenses.json`.
- Environment variables are prefixed `AURELIUS_LICENSE_REPORT_` (settings model
  in the package).

## Commands

```bash
nx build aurelius-license-report    # scan + aggregate + render
nx package aurelius-license-report  # zip dist/ for delivery
```

## Conventions

- This project only reads scan artifacts — never add scanning logic here; it
  belongs in the docker plugin's scan targets.

## Removal

Part of the workflow. Removing it means deleting the project and its CI/docs
references; per-project `licenses.json` output stays untouched.
