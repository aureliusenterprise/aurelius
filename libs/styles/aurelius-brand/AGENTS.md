# aurelius-brand (`@aurelius/brand`)

SCSS design tokens shared by the Aurelius frontends. This file covers wiring
specific to this lib; workspace-wide rules live in the root `AGENTS.md`.

> [!NOTE]
> The Nx project name is `aurelius-styles`; the directory and npm package name
> are `aurelius-brand`.

## Layout

- `src/_variables.scss` — colour palette and `$theme-colors` map
- `src/_theme.scss` — light/dark theme overrides
- `src/_main.scss` — entry point (pulls in Bulma + tokens); what consumers `@use`

## Wiring Checklist

- Consumed as the npm package `@aurelius/brand` via a `file:` dependency in
  `apps/aurelius-frontend-example/package.json` — this is the one scoped
  specifier; Angular libs use bare path aliases instead.
- `aurelius-ui` (`.storybook/styles.scss` and component styles) and
  `aurelius-frontend-example` global styles both build on these tokens.
- Depends on `bulma` and `@fortawesome/fontawesome-free` — declare them here,
  not in consuming projects.
- No build targets by design: plain SCSS consumed directly by bundlers.

## Conventions

- All brand colours and theme variables live here — apps and `aurelius-ui`
  must not define their own palettes.
- Changes here ripple to every frontend surface; check Storybook and the app
  after editing tokens.

## Removal

Part of the spine. Removing it means dropping the `file:` dependency and all
`@use "@aurelius/brand/..."` imports in the frontend and `aurelius-ui`, and
replacing the styling baseline (Bulma/FontAwesome) some other way.
