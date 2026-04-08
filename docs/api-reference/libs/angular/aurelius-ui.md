# aurelius-ui

[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=aurelius-ui&metric=sqale_rating&token=3ec6b3aab1748c077bbe786c64db740cc62ab68a)](https://sonarcloud.io/summary/new_code?id=aurelius-ui)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=aurelius-ui&metric=reliability_rating&token=3ec6b3aab1748c077bbe786c64db740cc62ab68a)](https://sonarcloud.io/summary/new_code?id=aurelius-ui)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=aurelius-ui&metric=security_rating&token=3ec6b3aab1748c077bbe786c64db740cc62ab68a)](https://sonarcloud.io/summary/new_code?id=aurelius-ui)

This library provides common UI components for Angular projects.

## Installation

You can import `aurelius-ui` in your Angular project directly from the monorepo. It will be bundled with
your application code and tree-shaken to include only the parts you use.

## Storybook

The `aurelius-ui` library includes a Storybook instance for interactive documentation and testing of the UI components.
To run Storybook, execute the following command in the root of the monorepo:

```bash
nx run aurelius-ui:storybook
```

This will start the Storybook server and open the Storybook interface in your default web browser, where you can
explore and interact with the UI components provided by the `aurelius-ui` library.
