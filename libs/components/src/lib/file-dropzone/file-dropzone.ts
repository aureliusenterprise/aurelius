import { UntypedFormControl, Validators } from '@angular/forms';
import { extension } from './validators';

export class FileDropzone extends UntypedFormControl {
  constructor(public validExtensions: string[] = []) {
    super('', [Validators.required, extension(validExtensions)]);
  }
}
