import { UntypedFormControl, Validators } from '@angular/forms';
import { Observable } from 'rxjs';
import {
  leadingOrTrailingWhitespace,
  multipleWhitespaces,
  unique,
} from './validators';

export class BranchNameInput extends UntypedFormControl {
  constructor(
    branchNamesLookupFn:
      | (() => string[])
      | (() => Observable<string[]>) = () => [],
    currentBranchNameLookupFn: () => string = () => null
  ) {
    super(
      '',
      [
        Validators.required,
        Validators.minLength(3),
        Validators.maxLength(50),
        leadingOrTrailingWhitespace,
        multipleWhitespaces,
      ],
      [unique(branchNamesLookupFn, currentBranchNameLookupFn)]
    );
  }
}
