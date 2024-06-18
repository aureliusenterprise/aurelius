# SortableTableShell

This module provides the `models4insight-sortable-table-shell` component, which implements a basic structure for tables which should have sortable columns. It also provides pagination. Components using the shell only need to implement the content of the table rows.

To further customize the table, components using the shell can provide a `SortableTableShellConfig` object as an input.

The `models4insight-sortable-table-shell` provides the following inputs:

- `config`: Accepts a `SortableTableShellConfig` object which allows for table customization
- `currentPage`: Sets the current page to the given number
- `data`: Sets the current dataset. The data should be shaped like a list of `Dictionary<any>`
- `enableTableContainer`: Determines whether or not the table should be wrapped inside of a container div which enables scrolling, but can cause issues with dropdown menus
- `itemsPerPage`: The number of items shown per page
- `rowComparator`: Function used to compare rows with one another. This function is used when determining whether a row is selected
- `rowsSelectable`: Whether or not the rows in the table can be selected when the user clicks them
- `totalItems`: The total number of rows in the dataset. Set this value if you are lazy loading your data whenever the page changes

Further, it provides the following outputs:

- `pageChanged`: Emits the current page number whenever the current page changes
- `rowClicked`: Emits the value of the row whenever a row is clicked
- `rowSelected`: Emits the value of the row whenever a row is selected
- `rowDeselected`: Emits whenever a row is deselected
- `rowIntersectionChanged`: Emits the value of a row whenever the corresponding row enters or leaves the view. This is useful when lazy loading data based on whether or not the user can see a row.

To expose all inputs and outputs from the `models4insight-sortable-table-shell` to parent components, components using the shell should inherit from the `AbstractSortableTable` class.

## Usage

The `models4insight-sortable-table-shell` expects any child components to define the row content as part of a `ng-template` element. It then passes a variable called `rowData` to the template. See the example below:

```javascript
export interface TableData {
  columnA: string;
  columnB: string;
  columnC: string;
  columnD: string;
}

const tableConfig: SortableTableShellConfig<TableData> = {
  columnA: { description: 'This is a column', displayName: 'Column A' },
  columnB: { description: 'This is another column', displayName: 'Column B' },
  columnC: {
    description: 'This is yet another column',
    displayName: 'Column C',
  },
  columnD: { description: 'This is the last column', displayName: 'Column D' },
};

export class ExampleComponent {
  data: TableData[] = [
    {
      columnA: 'This',
      columnB: 'is',
      columnC: 'some',
      columnD: 'data',
    },
  ];

  tableConfig = tableConfig;
}
```

```html
<models4insight-sortable-table-shell [config]="tableConfig" [data]="data">
  <ng-template let-rowData>
    <td>{{rowData.columnA}}</td>
    <td>{{rowData.columnB}}</td>
    <td>{{rowData.columnC}}</td>
    <td>{{rowData.columnD}}</td>
  </ng-template>
</models4insight-sortable-table-shell>
```
