# aurelius-ui

Shared presentational Angular components for Aurelius frontends, styled with
Bulma design tokens from `@aurelius/brand`. Components are standalone and carry no
data-fetching logic — state and HTTP belong in the consuming app or in
`aurelius-data-access`.

Part of the template **spine**.

## Components

- `Card` — content card
- `Header` — application header bar
- `Modal` — overlay dialog
- `Pagination` — page navigation
- `DarkMode` + `DarkModeService` — theme toggle with persisted preference

Every component ships a Storybook story (`.stories.ts`).

## Storybook

```bash
nx storybook aurelius-ui            # dev server on port 4400
nx build-storybook aurelius-ui      # static build
nx static-storybook aurelius-ui     # serve the static build on port 4500
nx test-storybook aurelius-ui       # interaction tests (Chromatic-ready)
```

## Usage

```ts
import { Card, Pagination } from "aurelius-ui";
```

Built with `ng-packagr-lite` (`nx build aurelius-ui` produces the distributable
package).
