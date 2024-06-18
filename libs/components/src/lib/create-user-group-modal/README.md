# CreateUserGroupModal

This module provedes the `models4insight-create-user-group-modal` component which implements a form for creating/editing a user group as part of a modal window.

## Usage

The `models4insight-create-user-group-modal` component has the following inputs:

- `groups`: The user groups which currently exist in the project. Used as search suggestions when adding group members, as well as to check whether the group name chosen by the user is still available.
- `usernames`: The names of the users who can be added as members of the user group.

Further, all standard inputs and outputs from the `AbstractModalComponent` are also available, such as the `subject` input which puts the form in edit mode when set.
