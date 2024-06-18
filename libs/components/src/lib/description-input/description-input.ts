import { UntypedFormControl, Validators } from '@angular/forms';

export class DescriptionInput extends UntypedFormControl {
  constructor() {
    super('', [Validators.required]);
  }
}
