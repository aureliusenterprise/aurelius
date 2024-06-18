# FileDropzone

This module provides the `models4insight-file-dropzone` form component and the `FileDropzone` form control, for use in forms where a file needs to be uploaded by the user. The `FileDropzone` validates branch names based on the following criteria:

- A file should be selected
- The file name extension of the selected file should match the allowed extensions

The `models4insight-file-dropzone` component provides user feedback in case the given branch name violates any of the above criteria.

## Usage

To use the `FileDropzone` form control, add it to your form as follows:

```javascript
class ExampleComponent {
  form: FormGroup;

  constructor(formBuilder: FormBuilder) {
    this.form = formBuilder.group({
      file: new FileDropzone(['csv', 'xls', 'xlsx']),
    });
  }
}
```

To use the `models4insight-file-dropzone` component, include it in your html template as follows:

```html
<form [formGroup]="form">
  <models4insight-file-dropzone [branchNameInput]="form.controls['file']"></models4insight-file-dropzone>
</form>
```
