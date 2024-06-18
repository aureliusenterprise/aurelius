# BranchNameInput

This module provides the `models4insight-branch-name-input` form component and the `BranchNameInput` form control, for use in forms where a branch name needs to be defined by the user. The `BranchNameInput` validates branch names based on the following criteria:

- A branch name should have a minimum length of 3 characters
- A branch name should have a maximum length of 50 characters
- A branch name should not include leading or trailing whitespace
- A branch name should not whitespace with a length longer than 1 (e.g. no double spaces)
- A branch name should not already be in use in the current project
- The branch name should not be empty

The `models4insight-branch-name-input` component provides user feedback in case the given branch name violates any of the above criteria.

## Usage

To use the `BranchNameInput` form control, add it to your form as follows:

```javascript
class ExampleComponent {
  branches: string[];
  form: FormGroup;

  constructor(formBuilder: FormBuilder) {
    this.form = formBuilder.group({
      branchName: new BranchNameInput(() => this.branches),
    });
  }
}
```

To use the `models4insight-branch-name-input` component, include it in your html template as follows:

```html
<form [formGroup]="form">
  <models4insight-branch-name-input [branchNameInput]="form.controls['branchName']"></models4insight-branch-name-input>
</form>
```
