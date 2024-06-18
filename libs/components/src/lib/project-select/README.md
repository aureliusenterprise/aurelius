# BranchNameInput

This module provides the `models4insight-project-select` form component and the `ProjectSelect` form control, for use in forms where a project needs to be selected by the user. The validation criteria are as follows:

- The selection cannot be empty

The component provides user feedback if the current input violates any of the above criteria.

The `models4insight-project-select` component makes use of the `models4insight-select` component. This especially helps users who have a lot of projects to choose from.

## Usage

To use the `ProjectSelect` form control, add it to your form as follows:

```javascript
class ExampleComponent {
  form: FormGroup;

  constructor(formBuilder: FormBuilder) {
    this.form = formBuilder.group({
      project: new ProjectSelect(),
    });
  }
}
```

By default, the selected project is `null`. Whenever the selection changes, the corresponding form value will be a `Project` object.

To use the `models4insight-project-select` component, include it in your html template as follows:

```html
<form [formGroup]="form">
  <models4insight-project-select [control]="form.controls['project']"></models4insight-project-select>
</form>
```
