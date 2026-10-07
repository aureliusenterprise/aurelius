# Angular Libraries (libs/angular)

This directory holds shared Angular libraries consumed by the frontend apps.
This file is the recipe for adding or modifying a library here; each library's own
`AGENTS.md`/`README.md` covers its specifics.

## Adding a New Library

1. **Generate**: `nx g @nx/angular:library libs/angular/<name> --buildable`
   (use `--publishable --importPath=@aurelius/<name>` if it will be published).
2. **Switch the builder** to `@nx/angular:ng-packagr-lite` in `project.json` —
   the workspace convention (it skips strict ng-packagr entry-point rules).
3. **Path alias**: register the bare package name (e.g. `aurelius-<name>`) in
   `tsconfig.base.json` `paths` — the workspace convention is unscoped aliases
   pointing at `src/index.ts` (only `@aurelius/brand` is scoped, as a `file:` npm
   dependency).
4. **`README.md`** — what the library does and when to use it. This is the
   canonical description: each library documents itself here, so no central list
   of libraries is maintained anywhere.
5. **`AGENTS.md`** — wiring and conventions for the library itself.
6. **Styles**: if the library ships SCSS using brand tokens, `@use` them from
   `@aurelius/brand` rather than redefining colours.
7. **Storybook**: for component libraries, copy the Storybook targets from
   `aurelius-ui` (`storybook`, `build-storybook`, `static-storybook`,
   `test-storybook`, `chromatic`) and add `.stories.ts` per component.

## Conventions

- Standalone components only; zoneless-compatible (no `zone.js` assumptions).
- Libraries never inject app-level state or call HTTP directly unless they are
  data-access libraries (see `aurelius-data-access`).
- Public API is `src/index.ts` — re-export only intended symbols.
- Tests are `.spec.ts` files co-located with source (Vitest via
  `@nx/angular:unit-test`); run with `nx test <lib> -c ci`.
- Peer dependencies must match the workspace Angular major — check
  `package.json` after generating (a stale `^21` peer range exists in
  `aurelius-ui` as a known issue).

## Removal

Delete the directory, remove its `tsconfig.base.json` path alias, remove imports
from consuming apps, and delete any `mkdocs.yaml` nav/API-reference entries.
