# PermissionSelect

This module provides the `models4insight-permission-select` component, which defines a generic control for selecting user permissions based on the `models4insight-select` component.

The select menu lists all permission levels from strongest to weakest.

In addition to the inputs inherited from `models4insight-select`, this component supports the following inputs:

- `isDisabled`: Whether or not the select box should be disabled. Use this when you want to show the permission level of a user, but you do not want the current user to be able to edit these permissions
- `isOwner`: Whether or not the user can select the `owner` option. This option should only be selectable if the current user is an owner as well
- `permission`: The current permission level, or the permission level to show by default

Further, it supports the following outputs:

- `permissionChanged`: Whenever a new value is selected, emits the corresponding `PermissionLevel`.
