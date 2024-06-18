# BranchNameInput

This module provides the `models4insight-provenance-select` form component and the `ProvenanceSelect` form control, for use in forms where a version needs to be selected by the user. The validation criteria are as follows:

- The selection cannot be empty

The component provides user feedback if the current input violates any of the above criteria.

The `models4insight-provenance-select` component makes use of the `models4insight-select` component. This especially helps users who have a lot of versions to choose from.

## Usage

To use the `ProvenanceSelect` form control, add it to your form as follows:

```javascript
class ExampleComponent {
  form: FormGroup;

  constructor(formBuilder: FormBuilder) {
    this.form = formBuilder.group({
      version: new ProvenanceSelect(),
    });
  }
}
```

By default, the selected version is `null`. Whenever the selection changes, the corresponding form value will be a `ModelProvenance` object.

To use the `models4insight-provenance-select` component, include it in your html template as follows:

```html
<form [formGroup]="form">
  <models4insight-provenance-select [control]="form.controls['version']"></models4insight-provenance-select>
</form>
```
