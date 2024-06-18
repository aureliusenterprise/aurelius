# BranchNameInput

This module provides the `models4insight-branch-select` form component and the `BranchSelect` form control, for use in forms where a branch needs to be selected by the user. The validation criteria are as follows:

- The selection cannot be empty

The component provides user feedback if the current input violates any of the above criteria.

The `models4insight-branch-select` component makes use of the `models4insight-select` component. This especially helps users who have a lot of branches to choose from.

The `models4insight-branch-select` component also includes a `models4insight-create-branch-modal` which, after submission, adds an additional option to the select menu in addition to creating the branch in the backend. To allow users to create new branches via this select menu, set the `withCreateBranch` input to `true`.

## Usage

To use the `BranchSelect` form control, add it to your form as follows:

```javascript
class ExampleComponent {
  form: FormGroup;

  constructor(formBuilder: FormBuilder) {
    this.form = formBuilder.group({
      branch: new BranchSelect(),
    });
  }
}
```

By default, the selected branch is `null`. Whenever the selection changes, the corresponding form value will be a `Branch` object.

To use the `models4insight-branch-select` component, include it in your html template as follows:

```html
<form [formGroup]="form">
  <models4insight-branch-select [control]="form.controls['branch']"></models4insight-branch-select>
</form>
```
