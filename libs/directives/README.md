# Directives

This library provides common directives that can be used across applications. The following directives are available:

## Dropzone

The `dropzone` directive turns any container into a drag-and-drop file selector. The container emits the following events:
.
- `dropped`
  - Emits a `FileList` whenever the user drops a file into the zone.
- `hovered`
  - Emits `true` whenever the user drags a file into the dropzone area, and `false` whenever the user drags the file out again. 

## Holdable

The `holdable` directive tracks mouse-down and -up events for any container. It is intended to be used on buttons and links. Tracks the amount of time the user holds down the mouse, and emits an event indicating whether or not the user held the mouse down for a specific amount of time. By default, the required amount of time is `1 second`. The directive also adds a tooltip to the container indicating to the user how long they need to hold down the mouse.

The directive supports the following configurations:

- `holdTime`
  - The amount of time the user should hold down the mouse in `seconds`

The directive emits the following events:

- `held`
  - Emits whenever the user holds down the mouse for the required time, or when the user releases the mouse. Emits `true` if the user held down the mouse long enough, `false` if otherwise.

### Dependencies

The `holdable` directive depends on `bulma-tooltip` to show a tooltip to the user.

# Nx

This library was generated with [Nx](https://nx.dev).

## Running unit tests

Run `ng test directives` to execute the unit tests.
