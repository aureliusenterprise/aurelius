import { UntypedFormControl, Validators } from '@angular/forms';

export class Select extends UntypedFormControl {
  constructor(required = false) {
    super(null, required ? [Validators.required] : []);
  }
}
