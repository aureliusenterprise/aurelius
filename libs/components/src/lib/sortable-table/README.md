# SortableTable

This module provides the `models4insight-sortable-table` component.
It implements a version of the `models4insight-sortable-table-shell` which fills the rows and columns based on the given data.
The data input should resemble a list of `Dictionary<any>`.
Every key is turned into a sortable column.
Use this component if you have a simple dataset to display, without the need for advanced configuration.

The `models4insight-sortable-table` inherits all inputs and outputs from the `models4insight-sortable-table-shell`.

## Usage

The example below shows how to include a basic `models4insight-sortable-table` in one of your components:

```javascript
export class ExampleComponent {
  data: Dictionary<any>[] = [
    {
      columnA: 'This',
      columnB: 'is',
      columnC: 'some',
      columnD: 'data',
    },
  ];
}
```

```html
<models4insight-sortable-table [data]="data"><models4insight-sortable-table></models4insight-sortable-table></models4insight-sortable-table>
```
