# Aurelius Atlas

This part of the repository contains the code base for the Aurelius Atlas software.
This a data dictionary tool that takes into account the Data modeling of our company. It's still in it's early stages, but with time, it's going to be a key feature of data governance.

# Security

We are basing the security on KeyCloack, which is already into place for our tools.

# Nx

This project was generated using [Nx](https://nx.dev).

<p><img src="https://raw.githubusercontent.com/nrwl/nx/master/nx-logo.png" width="45"></p>

🔎 **Nx is a set of Angular CLI power-ups for modern development.**

## Development server

From inside the Models4Insight repository, run `npm run start atlas` for a dev server. Navigate to http://localhost:4200/. The app will automatically reload if you change any of the source files.

## Build

Run `npm run build atlas` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `build:prod` modifier for a production build.

## Running unit tests

Run `ng test my-app` to execute the unit tests via [Jest](https://jestjs.io).

Run `npm run affected:test` to execute the unit tests affected by a change.

## Running end-to-end tests

Run `ng e2e atlas` to execute the end-to-end tests via [Cypress](https://www.cypress.io).

Run `npm run affected:e2e` to execute the end-to-end tests affected by a change.

## Understand your workspace

Run `npm run dep-graph` to see a diagram of the dependencies of your projects.
