import { Component, OnDestroy, OnInit } from '@angular/core';
import { UntypedFormBuilder, UntypedFormGroup } from '@angular/forms';
import { DescriptionInput } from '@models4insight/components';
import { ProjectService, ProjectsService } from '@models4insight/services/project';
import { untilDestroyed } from '@models4insight/utils';

@Component({
  selector: 'models4insight-project-description-settings',
  templateUrl: 'project-description.component.html',
  styleUrls: ['project-description.component.scss']
})
export class ProjectDescriptionSettingsComponent implements OnInit, OnDestroy {
  readonly projectSettingsForm: UntypedFormGroup;

  constructor(
    private readonly formBuilder: UntypedFormBuilder,
    private readonly projectService: ProjectService,
    private readonly projectsService: ProjectsService
  ) {
    this.projectSettingsForm = this.formBuilder.group({
      description: new DescriptionInput()
    });
  }

  ngOnInit() {
    // Whenever the project documentation changes, update the description in the form. This also sets the initial form value.
    this.projectService
      .selectCurrentProject()
      .pipe(untilDestroyed(this))
      .subscribe(project =>
        this.projectSettingsForm.patchValue({
          description: project.documentation
        })
      );
  }

  ngOnDestroy() {}

  async onSaveProjectSettings() {
    const project = await this.projectService.getCurrentProject();

    const { description } = this.projectSettingsForm.value;

    this.projectsService.updateProject({
      ...project,
      documentation: description
    });
  }
}
