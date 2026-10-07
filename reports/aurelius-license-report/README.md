# aurelius-license-report

Aggregates the per-project license scan results (`licenses.json`, produced by the
Trivy-based `docker-license-scan` target) into workspace-level and per-project HTML
reports.

Part of the template **workflow**.

## How it works

- `python -m aurelius_license_report` recursively collects every `licenses.json` in
  the workspace, joins it with project metadata, and renders Jinja2 templates into
  HTML — one report per project plus a workspace summary.
- The `build` target depends on `decrypt` (SOPS) and `docker-license-scan` on all
  Docker-tagged projects, so `nx build aurelius-license-report` runs the scans
  first, then generates the reports.
- Reports are written to `dist/` in this directory; `package` zips them up.

## Configuration

Environment variables are prefixed `AURELIUS_LICENSE_REPORT_` (see the settings
model in the package for the full list).

## Running

```bash
nx build aurelius-license-report   # scan + aggregate + render
nx package aurelius-license-report # zip the reports for delivery
```
