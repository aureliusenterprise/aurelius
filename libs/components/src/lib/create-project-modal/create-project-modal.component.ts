import { Component, OnInit } from '@angular/core';
import {
  UntypedFormBuilder,
  UntypedFormGroup,
  Validators,
} from '@angular/forms';
import { AuthenticationService } from '@models4insight/authentication';
import { Project } from '@models4insight/repository';
import { ProjectsService } from '@models4insight/services/project';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { AbstractModalForm } from '../abstract-modal-form/abstract-modal-form';
import {
  defaultDescriptionInputContext,
  DescriptionInput,
  DescriptionInputContext,
} from '../description-input';
import {
  leadingOrTrailingWhitespace,
  multipleWhitespaces,
  unique,
} from './validators';

const descriptionContext: DescriptionInputContext = {
  ...defaultDescriptionInputContext,
  label: 'Description',
  placeholder: 'Description',
  requiredErrorMessage: 'Please provide a description for your project',
};

@Component({
  selector: 'models4insight-create-project-modal',
  templateUrl: 'create-project-modal.component.html',
  styleUrls: ['create-project-modal.component.scss'],
})
export class CreateProjectModalComponent
  extends AbstractModalForm<Project>
  implements OnInit
{
  readonly descriptionContext = descriptionContext;

  isCreatingProject$: Observable<boolean>;

  constructor(
    private readonly authenticationService: AuthenticationService,
    private readonly formBuilder: UntypedFormBuilder,
    private readonly projectsService: ProjectsService
  ) {
    super('project');
    this.form = this.initForm();
  }

  ngOnInit() {
    super.ngOnInit();

    this.isCreatingProject$ = this.projectsService.select('isCreatingProject');

    // Whenever the form is successfully submitted, create a new project
    this.submission
      .pipe(untilDestroyed(this))
      .subscribe((project) => this.projectsService.createProject(project));
  }

  protected createSubmission(): Project {
    return {
      ...this.form.value,
      subscription: 'private',
    };
  }

  protected initForm(): UntypedFormGroup {
    return this.formBuilder.group({
      name: this.formBuilder.control('', {
        validators: [
          Validators.required,
          Validators.minLength(3),
          Validators.maxLength(25),
          leadingOrTrailingWhitespace,
          multipleWhitespaces,
        ],
        asyncValidators: [
          unique(
            this.authenticationService.select(['credentials', 'username']),
            this.projectsService.projects
          ),
        ],
      }),
      documentation: new DescriptionInput(),
    });
  }
}
