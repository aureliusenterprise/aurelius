# DatePicker

The `models4insight-date-picker` component implements a standardized date picker. The component consists of an input field which, when clicked, opens a modal window in which the user can choose a date. When the user has chosen a date, the modal window closes and the input reflects the date chosen. The control also provides a button to clear the currently selected date.

The `models4insight-date-picker` provides the following inputs:

- `date`: Accepts a `Date` object or a numeric timestamp. Sets the currently selected date.

Further, it provides the following outputs:

- `dateChanged`: Emits a numeric timestamp whenever the user has selected a new date, or `null` when the value is cleared.
