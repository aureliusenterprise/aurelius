import { AbstractControl } from '@angular/forms';
import { UserGroup } from '@models4insight/repository';

/** Checks whether or not the current branch name is contained within the supplied set of branch names */
export function unique(
  groupNamesLookupFn: () => string[] = () => [],
  currentGroupNameLookupFn: () => string = () => null
) {
  return ({ value: groupName }: AbstractControl) => {
    const groupNames = groupNamesLookupFn();
    const currentGroupName = currentGroupNameLookupFn();
    return groupNames &&
      groupName !== currentGroupName &&
      groupNames.some((name) => name === groupName)
      ? { unique: true }
      : null;
  };
}

/** Checks whether or not the current branch name contains any leading or trailing white spaces */
export function leadingOrTrailingWhitespace({
  value: groupName,
}: AbstractControl) {
  return groupName && groupName.length !== groupName.trim().length
    ? { leadingOrTrailingWhitespace: true }
    : null;
}

/** Checks whether or not the current branch name contains any consecutive whitespaces */
export function multipleWhitespaces({ value: groupName }: AbstractControl) {
  let matches = [];
  if (groupName) {
    // Find all whitespaces in the string
    matches = groupName.match(/\s+/g);
  }
  // Check whether any of the whitespaces are longer than 1
  return !!matches && !!matches.find((match: string) => match.length > 1)
    ? { multipleWhitespaces: true }
    : null;
}
