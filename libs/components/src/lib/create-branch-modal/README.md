# CreateBranchModal

This module provedes the `models4insight-create-branch-modal` component which implements a form for creating/editing a branch as part of a modal window.

## Usage

The `models4insight-create-branch-modal` component has the following inputs:

- `branches`: The names of the currently existing branches. Used to check whether or not the branch name chosen by the user is still available.
- `groupNames`: The names of the user groups which can be added as members of the branch.
- `usernames`: The names of the users who can be added as members of the branch.

Further, all standard inputs and outputs from the `AbstractModalComponent` are also available, such as the `subject` input which puts the form in edit mode when set.
