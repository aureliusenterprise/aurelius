# AbstractModalForm

Components which want to implement a form inside of a `models4insight-modal` should inherit from `AbstractModalComponent`.

This class hooks into the modal component and implements features such as:

- Submit the form when the modal is confirmed
- Validate the form on submission
- Close the window when submitted successfully
- Clear the form on cancel
- Switch the modal window between `create` and `edit` mode

## Usage

Inheriting classes should implement the following methods:

### createSubmission()

The `createSubmission()` method should return the object that is emitted by the `submission` output after the form is submitted. `AbstractModalForm` takes a type argument which lets you define the shape of your submission object.

### initForm()

The `initForm()` method should create the form as a `FormGroup`. Don't forget to assign the created `FormGroup` to the `form` property after creation.

## Create/Edit mode

The title of the modal window changes based on whether the form is in `create` or `edit` mode.

Set the `subject` property to put the form into `edit` mode. The form is automatically filled with values from the given subject.

When an `AbstractModalForm` does not have a `subject` (i.e. the property is `null` or `undefined`), the form is assumed to be in `create` mode.

The `subject` property is also available as an external `input`.
