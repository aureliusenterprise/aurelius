# aurelius-dev-atlas-reference

The reference Apache Atlas for recording parity fixtures. This file covers wiring specific
to this project; workspace-wide rules live in the root `AGENTS.md`.

## Layout

- `reference.sh` — wraps Atlas's own `dev-support/atlas-docker` (borrowed, not copied: ADR 045)
- `.atlas-src/` — the cloned Atlas source tag (gitignored)
- `project.json` — `prepare`, `build-atlas`, `up`, `down`

## Wiring Checklist

- `ATLAS_TAG` (default `release-2.4.0`) must match DD-001 and the `reference` recorded in
  every fixture. Changing it means re-recording every fixture (a new design-log entry).
- No `docker-compose.yaml` lives here on purpose: the compose files are Atlas's own, inside
  `.atlas-src/`, so the compose Nx plugin does not infer targets for this project.
- Nothing depends on this project; it is started by hand when recording.

## Commands

```bash
nx build-atlas aurelius-dev-atlas-reference
nx up aurelius-dev-atlas-reference
nx down aurelius-dev-atlas-reference
```

## Conventions

- Never point tests at the running reference; tests compare against recorded fixtures.

## Removal

Removing it means fixtures can no longer be re-recorded; parity tests keep working.
