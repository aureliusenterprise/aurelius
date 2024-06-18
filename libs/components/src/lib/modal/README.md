# Modal

This module provides the `models4insight-modal` component, which acts as a generic shell for modal content.
It implements a modal window with a opaque background, as well as confirm, cancel and close buttons.

You can provide a `context` object to configure the the modal component.
The `context` sets the window title, button text and determines whether the modal should close after it has been confirmed.
If you do not include the `confirm` property as part of the modal context, the confirmation button will not appear.

In addition to the `context`, the `models4insight-modal` component defines the following inputs:

- `active`: Dynamically opens or closes the modal based on an outside source
- `isLoading`: Whether or not the confirm button should show a loading spinner

Further, it defines the following outputs:

- `activeStateChanged`: Emits a boolean value indicating the active state of the modal window every time it changes
- `canceled`: Emits whenever the modal window is canceled (either by clicking the cancel button, the close button or the backdrop)
- `confirmed`: Emits whenever the modal window is confirmed

## Usage

The example below shows how you can add a modal window as part of one of your components.

```javascript
export class ExampleComponent {
    readonly modalContext: ModalContext = {
        cancel: 'Close',
        closeOnConfirm: true,
        confirm: 'Save',
        title: 'Example'
    };

    @ViewChild(ModalComponent, {static: true})
        private readonly modal: ModalComponent;

    activateModal() {
        this.modal.activate();
    }
}
```

```html
<!-- This button activates the modal window -->
<a class="button" (click)="activateModal()">Open the modal</a>
<models4insight-modal [context]="modalContext">
  <!-- The content of the modal window goes here. This can be anything. -->
</models4insight-modal>
```
