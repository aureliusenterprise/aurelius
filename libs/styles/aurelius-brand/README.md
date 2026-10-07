# aurelius-brand (`@aurelius/brand`)

SCSS design tokens and styling baseline shared by Aurelius frontends: the brand
colour palette, theme variables, and a Bulma/FontAwesome foundation.

Part of the template **spine**.

## Contents

- `src/_variables.scss` — colour palette and `$theme-colors` map
- `src/_theme.scss` — theme-level overrides (light/dark)
- `src/_main.scss` — entry point pulling in Bulma and the tokens above

Depends on `bulma` and `@fortawesome/fontawesome-free`.

## Usage

Consumed as the npm package `@aurelius/brand` (a `file:` dependency of
`aurelius-frontend-example`; `aurelius-ui` styles build on these tokens):

```scss
@use "@aurelius/brand/src/main" as brand;
```

> [!NOTE]
> The Nx project name is `aurelius-styles` (not `aurelius-brand`) and it defines no
> build targets — it is plain SCSS consumed directly by bundlers.
