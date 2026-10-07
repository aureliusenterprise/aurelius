# aurelius-ui

Shared presentational Angular components. This file covers wiring specific to this
lib; workspace-wide rules live in the root `AGENTS.md` and the Angular lib recipe
in `libs/angular/AGENTS.md`.

## Layout

- `src/lib/<component>/` — one folder per component with `.spec.ts` and
  `.stories.ts` colocated; `src/index.ts` is the public API
- `.storybook/` — Storybook config, styles (imports brand tokens), and assets
- `ng-package.json` / `tsconfig.lib*.json` — ng-packagr-lite build config

## Wiring Checklist

- `tsconfig.base.json` — `aurelius-ui` path alias used by the frontend.
- `package.json` — peer deps: keep in sync with the workspace Angular major
  (currently stale at `^21` — update when touching this file).
- Styling comes from `@aurelius/brand` tokens; new colours belong there, not here.
- `chromatic` target depends on `decrypt` (SOPS) for the Chromatic token.

## Commands

```bash
nx storybook aurelius-ui            # dev server, port 4400
nx test aurelius-ui -c ci           # Vitest unit tests
nx test-storybook aurelius-ui       # interaction tests
nx build aurelius-ui                # ng-packagr-lite package build
```

## Conventions

- Every component ships a story; visual regression depends on it.
- Components are dumb: `input()`/`output()` only, no services with side effects
  (exception: `DarkModeService`, which owns theme persistence).
- New components: export from `src/index.ts`, add stories, add unit tests.

## Removal

Part of the spine. Removing it means removing the `aurelius-ui` alias, all
imports in `aurelius-frontend-example`, and its `mkdocs.yaml` entries.
