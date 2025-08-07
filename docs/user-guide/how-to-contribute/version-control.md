# Version Control

When making changes to the project, follow these guidelines.

## Branching

Always create a new branch for your changes. This makes it easier to handle multiple contributions simultaneously.

??? QUESTION "Why should I create a new branch?"

    Creating a new branch allows you to work on your changes without affecting the `main` branch. This makes it
    easier to collaborate with others and keep the codebase clean.

First, pull the latest changes from the `main` branch:

```bash
git pull main
```

Next, create a new branch with the following command:

```bash
git checkout -b "<YOUR_BRANCH_NAME>"
```

Replace `<YOUR_BRANCH_NAME>` with a short, descriptive name for your branch. For example, `add-uptime-command`.

## Commits

To add your changes to the repository, you need to commit them to your branch. When committing your changes, follow
the [conventional commit format](https://www.conventionalcommits.org/en/v1.0.0/).

The conventional commit format helps keep the commit history clean and organized. It also makes it easier to
generate changelogs and track changes over time.

??? EXAMPLE "Conventional Commit Format"

    Here are some examples of conventional commits:

    ```plaintext
    feat: add uptime command
    fix: handle edge case in command
    chore: update dependencies
    docs: update README
    ```

    Each commit message should start with a type, followed by a colon and a short description of the changes.

To commit your changes, first you need to stage the files you want to commit:

```bash
git add <FILES>
```

Replace `<FILES>` with the files you want to commit. You can also use `.` to stage all changes.

Next, commit your changes using the following command:

```bash
git commit -m "<YOUR_COMMIT_MESSAGE>"
```

Replace `<YOUR_COMMIT_MESSAGE>` with a short, descriptive message following the conventional commit format.

??? TIP "Use a Git GUI"

    If you prefer a graphical interface, you can use a Git GUI tool to stage and commit your changes. For example, VS Code
    has a built-in Git interface that you can use.

??? QUESTION "How often should I commit my changes?"

    It's a good practice to commit your changes often. This allows you to track your progress and revert changes if needed.

### Automated Checks

The project includes pre-commit hooks to ensure your code meets the quality standards. These hooks run automatically
before each commit.

The pre-commit hooks perform the following checks:

- Check JSON, TOML, and YAML files for syntax errors
- Ensure files end with a newline
- Trim trailing whitespace
- Lint and format Python code with [Ruff](https://docs.astral.sh/ruff/)
- Check for Python type issues with [Pyright](https://github.com/microsoft/pyright)
- Format Markdown and JSON files with [Prettier](https://prettier.io/)
- Lint Markdown files with [markdownlint](https://github.com/DavidAnson/markdownlint)
- Scan for secrets with [Talisman](https://github.com/thoughtworks/talisman/)

??? QUESTION "What if the pre-commit hooks fail?"

    If the pre-commit hooks fail, you will need to address the issues before committing your changes. Follow the
    instructions provided by the pre-commit hooks to identify and fix the issues.

??? QUESTION "How do I run the pre-commit hooks manually?"

    Pre-commit hooks can also be run manually using the following command:

    ```bash
    poetry run pre-commit
    ```

The pre-commit hooks are intended to help us keep the codebase maintainable. If there are rules that you believe
are too strict, please discuss them with the team.

## Pull Requests

Once you have completed your changes, it's time to create a pull request. A pull request allows your changes to
be reviewed and merged into the `main` branch.

Before creating a pull request, ensure your branch is up to date with the latest changes from the `main` branch:

```bash
git pull main
```

Next, push your changes to the repository:

```bash
git push
```

Finally, [create a pull request on GitHub](https://github.com/aureliusenterprise/project-template/compare). Select
your branch as the source and the `main` branch as the base.

Give your pull request a descriptive title that summarizes the changes you have made. Please ensure the title
follows the [conventional commit format](https://www.conventionalcommits.org/en/v1.0.0/).

In the pull request description, provide a brief overview of the changes and any relevant information for reviewers.

??? EXAMPLE "Pull Request Description"

    Here's an example of a good pull request description:

    ```plaintext
    # feat: add uptime command

    This pull request adds a new uptime command to display the bot's uptime.

    ## Changes

    - Added a new command to display the bot's uptime
    - Updated the help command to include information about the new command

    ## Notes

    - The new command is implemented in a separate file for better organization
    - The command has been tested locally and works as expected
    ```

### Automated Checks

The same pre-commit hooks that run locally will also run automatically on the pull request.

??? QUESTION "What if the pre-commit hooks fail on the pull request?"

    If the pre-commit hooks fail on the pull request, you will need to address the issues in your branch and push
    the changes. The pre-commit hooks will run again automatically.

    Please address any issues identified by the pre-commit hooks before requesting a review.

### Code Review

All pull requests should be reviewed by at least one other team member before merging. The reviewer will provide
feedback and suggestions for improvement.

Once the reviewer approves the pull request, you can merge it into the `main` branch.

??? QUESTION "How do I request a review?"

    Request a review from a team member by [assigning them as a reviewer](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/requesting-a-pull-request-review)
    to your pull request.

#### Giving Feedback

When providing feedback on a pull request, be constructive and specific. Point out areas for improvement and suggest
possible solutions. If you have any questions or concerns, don't hesitate to ask the author for clarification.

A code review should focus on the following aspects:

- Correctness and functionality
- Code quality and readability
- Adherence to the project guidelines

??? EXAMPLE "Good Code Review Feedback"

    Here are some examples of good code review feedback:

    ```plaintext
    - Great work on the new command! The implementation looks good overall.
    - I noticed a small typo in the docstring. Could you update it to fix the typo?
    - The logic in the new command is a bit complex. Consider breaking it down into smaller functions for clarity.
    - The tests cover most of the functionality, but we are missing a test case for edge case X. Could you add a test for that?
    ```

Always be respectful and considerate when giving feedback. Remember that the goal is to improve the code and help
the author grow as a developer.

!!! SUCCESS "Be Positive"

    Don't forget to acknowledge the positive aspects of the contribution as well!
