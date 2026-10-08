# Documentation

This page provides guidelines for contributing to the documentation.

## Tools

The documentation is built using [Zensical](https://zensical.org/), a static site generator built by the
creators of Material for MkDocs. It converts Markdown files into a website and reads the existing
`mkdocs.yaml` configuration.

Markdown is a lightweight markup language with plain-text formatting syntax. Refer to the [Markdown Guide](https://www.markdownguide.org)
for more information on how to use Markdown.

The documentation uses the Material design, which is built into Zensical. Please review the
[Zensical documentation](https://zensical.org/docs/) for guidance on how to use its various features.

## Running the Documentation

!!! NOTE "Prerequisites"

    Ensure you have [set up your development environment](./development-environment.md) before running the documentation.

To view the documentation locally, you can use the following command:

```bash
nx docs
```

Open your browser and navigate to [`http://localhost:8000`](http://localhost:8000) to view the documentation.
The changes you make to the documentation will be automatically reflected in the browser.

## Adding a New Page

To add a new page to the documentation, create a new Markdown file in the `docs` directory.

Next, update the `nav` section in the `mkdocs.yaml` file to include the new page. The `nav` section defines the
structure of the documentation and the order in which the pages are displayed in the navigation bar.

Please ensure that the folder structure in the `docs` directory matches the structure defined in the `nav` section.

## Architecture Decisions

Significant technical and organisational decisions are recorded as
[Architecture Decision Records](../architecture/adr/index.md) under
`docs/architecture/adr/`. When a change you are making establishes, alters, or
reverses a decision that constrains the project, propose an ADR as part of the
pull request using the [ADR Template](../architecture/adr/template.md). Keep
records business-focused: the reasoning belongs in the ADR, the implementation
in the code and project documentation.

## Linting

This project is configured to use [markdownlint](https://github.com/DavidAnson/markdownlint) to ensure consistent
Markdown styling and formatting across the documentation. The linter is automatically run when you commit changes
to the repository.

You can configure the linter rules in the `.markdownlint.json` file. Refer to the [markdownlint rules](https://github.com/DavidAnson/markdownlint?tab=readme-ov-file#rules--aliases)
for more information on the available rules.

!!! TIP "Use a Markdown Linter Extension"

    We recommend installing a Markdown linter extension in your editor to help identify and fix issues as you write.
    The development container is pre-configured with the [`markdownlint`](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint)
    extension for Visual Studio Code.

## Formatting

The documentation is formatted using [Prettier](https://prettier.io/), an opinionated code formatter that ensures
consistent style across the project. Prettier is automatically run when you save a Markdown file in the editor.

You can configure the formatting rules in the `.prettierrc.json` file. Refer to the [Prettier options](https://prettier.io/docs/en/options.html)
for more information on the available options.

## Publishing the Documentation

The documentation is published automatically when changes are merged into the `main` branch. A GitHub Action workflow
is trigged to build the documentation and push it to the `public-docs` branch. The published documentation is
hosted on GitHub Pages.

For review purposes, documentation is also published for pull requests. A link to the published documentation
is provided as a comment on the pull request. This allows reviewers to view the changes in the documentation before
merging the pull request. When the pull request is merged, this documentation is removed.

### Versioning

This project uses [mike](https://github.com/squidfunk/mike) (the Zensical-compatible fork) to manage the
documentation versions. Versions are
defined by tags in the repository, and the documentation for each version is published to a separate directory.
The `main` branch is aliased to the `latest` directory, which is the default version displayed on the website.
