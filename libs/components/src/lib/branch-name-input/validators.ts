import { AbstractControl } from '@angular/forms';
import { Observable } from 'rxjs';
import { first } from 'rxjs/operators';

/** Checks whether or not the current branch name is contained within the supplied set of branch names */
export function unique(
  branchNamesLookupFn: (() => string[]) | (() => Observable<string[]>),
  currentBranchNameLookupFn: () => string = () => null
) {
  return async ({ value: branchName }: AbstractControl) => {
    let branchNames = branchNamesLookupFn();
    const currentBranchName = currentBranchNameLookupFn();
    if (!Array.isArray(branchNames)) {
      if (branchNames) {
        branchNames = await branchNames.pipe(first()).toPromise();
      } else {
        branchNames = [];
      }
    }
    return branchNames &&
      branchName !== currentBranchName &&
      branchNames.includes(branchName)
      ? { unique: true }
      : null;
  };
}

/** Checks whether or not the current branch name contains any leading or trailing white spaces */
export function leadingOrTrailingWhitespace({
  value: branchName,
}: AbstractControl) {
  return branchName && branchName.length !== branchName.trim().length
    ? { leadingOrTrailingWhitespace: true }
    : null;
}

/** Checks whether or not the current branch name contains any consecutive whitespaces */
export function multipleWhitespaces({ value: branchName }: AbstractControl) {
  let matches = [];
  if (branchName) {
    // Find all whitespaces in the string
    matches = branchName.match(/\s+/g);
  }
  // Check whether any of the whitespaces are longer than 1
  return !!matches && !!matches.find((match: string) => match.length > 1)
    ? { multipleWhitespaces: true }
    : null;
}
