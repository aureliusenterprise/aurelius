# DescriptionInput

This module provides the `models4insight-description-input` form component and the `DescriptionInput` form control, for use in forms where some sort of description needs to be provided by the user. The `DescriptionInput` validates branch names based on the following criteria:

- The description cannot be empty

The `models4insight-description-input` component provides user feedback in case the given branch name violates any of the above criteria.

## Usage

To use the `DescriptionInput` form control, add it to your form as follows:

```javascript
class ExampleComponent {
  branches: string[];
  form: FormGroup;

  constructor(formBuilder: FormBuilder) {
    this.form = formBuilder.group({
      description: new DescriptionInput(),
    });
  }
}
```

To use the `models4insight-description-input` component, include it in your html template as follows:

```html
<form [formGroup]="form">
  <models4insight-description-input [branchNameInput]="form.controls['description']"></models4insight-description-input>
</form>
```
