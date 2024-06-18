# ContextMenuComponent

The `models4insight-context-menu` component provides a generic way of defining a context menu with custom actions. The component itself provides the dropdown menu and the formatting of the buttons.

## Usage

You can set the context menu actions by passing a matrix of `ContextMenuItem` to the `menuItems` input. For every context menu action, you can specify the following parameters:

- `click`: A function which should trigger when the action is clicked in the context menu. When `holdTime` is also specified, the function only triggers if the item is held for a sufficient amount of time.
- `hasPermission`: A function which should return whether nor not the current user has permission to perform the action. If the user does not have permission, the action will not show up in the menu.
- `holdTime`: The amount of time in seconds which the user should hold down the button for this action. A tooltip will appear next to the button to indicate the required hold time.
- `icon`: The fontawesome icon class for the icon which should appear next to the button text.
- `iconModifier`: The names of additional classes which should be applied to the icon such as size or color.
- `title`: The button text describing the action

You can specifiy actions in groups by passing them as part of separate arrays in the `ContextMenuItems` matrix. Every action group is delimited by a horizontal separator in the context menu. See the example below:

```javascript
const contextMenuItems: ContextMenuItem[][] = [
  // Group 1
  [
    // Action 1
    // Action 2
  ],
  // Group 2
  [
    // Action 3
    // Action 4
  ],
];
```
