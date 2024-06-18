# Select

The `models4insight-select` component implements a select menu with a detail view for looking up values. This is useful when you have a select menu with a lot of options, or if you want to provide a description for every value.

## Behaviour

The select menu has a button next to it with a looking glass icon. When pressed, the search menu opens as a modal window. It contains a `models4insight-sortable-table`, which should list additional details for every option.

In addition to the table, the search window also has a search filter which is either based on a `models4insight-fuzzy-search-input`, or a `models4insight-date-picker` depending on whether the options are text values or timestamps.

By clicking a row of the table, the user can select an option. This is then reflected in the select menu. The search menu table highlights the row of the currently selected option. Once an option is selected, the search menu closes.

## Inputs

The `models4insight-select` component has the following inputs:

- `comparator`: A function which compares two options. Used to determine which option is currently selected. By default, uses the lodash `isEqual` function.
- `context`: Accepts a `SelectContext` object which allows for customization of the select menu and search menu.
- `control`: The `FormControl` that should reflect the value of the option selected.
- `data`: The options the user can choose from.
- `displayField`: The name of the property that should be displayed as part of the select menu. Also determines which values the user can search for in the search menu.
- `inputClasses`: A list of HTML classes which should be applied to the select menu to alter its appearance.
- `isDisabled`: Whether or not the select menu should be disabled.
- `isSubmitted`: Whether or not the form to which this control belongs has been submitted. When submitted, validation messages are shown if the control is invalid.

To expose all inputs from the `models4insight-select` to parent components, components extending the `models4insight-select` should inherit from the `AbstractSelectComponent` class.

## Adding more options

You can add additional options to the select menu by defining them as content of the component. Options can be placed before or after the options generated based on the given data based on the selected transclusion slot. For example:

```html
<models4insight-select>
  <ng-container options-before>
    <option>Static option A</option>
    <option>Static option B</option>
  </ng-container>
  <ng-container options-after>
    <option>Static option Z</option>
  </ng-container>
</models4insight-select>
```

## Adding more buttons

You can add additional buttons to the select menu by defining them as content of the component. Buttons can be placed to the left or to the right of the search button based on the selected transclusion slot. For example:

```html
<models4insight-select>
  <ng-container buttons-left>
    <div class="control">
      <a type="button" class="button" (click)="doSomething()">
        <span class="icon is-small">
          <fa-icon [icon]="someIcon"></fa-icon>
        </span>
      </a>
    </div>
  </ng-container>
  <ng-container buttons-right>
    <div class="control">
      <a type="button" class="button" (click)="doSomethingElse()">
        <span class="icon is-small">
          <fa-icon [icon]="someIcon"></fa-icon>
        </span>
      </a>
    </div>
  </ng-container>
</models4insight-select>
```
