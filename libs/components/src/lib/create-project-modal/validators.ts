import { AbstractControl } from '@angular/forms';
import { Project } from '@models4insight/repository';
import { Observable } from 'rxjs';
import { first } from 'rxjs/operators';

export function unique(
  username$: string | Observable<string>,
  projects$: Project[] | Observable<Project[]>
) {
  return async (control: AbstractControl) => {
    let username = username$;

    if (typeof username !== 'string') {
      username = await username.pipe(first()).toPromise();
    }

    let projects = projects$;

    if (!Array.isArray(projects)) {
      projects = await projects.pipe(first()).toPromise();
    }

    const isNotUnique = projects.some(
      (project) =>
        project.committer.username === username &&
        project.name === control.value
    );

    return isNotUnique ? { unique: true } : null;
  };
}

export function leadingOrTrailingWhitespace(control: AbstractControl) {
  const name: string = control.value;
  return name && name.length !== name.trim().length
    ? { leadingOrTrailingWhitespace: true }
    : null;
}

export function multipleWhitespaces(control: AbstractControl) {
  const name: string = control.value;
  if (name) {
    const match = name.match(/\s+/g);
    return match && match.some((sample: string) => sample.length > 1)
      ? { multipleWhitespaces: true }
      : null;
  }
  return null;
}
