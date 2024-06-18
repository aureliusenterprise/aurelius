import { Component, OnInit } from '@angular/core';
import { faProjectDiagram } from '@fortawesome/free-solid-svg-icons';
import { Project } from '@models4insight/repository';
import {
  ProjectService,
  ProjectsService,
} from '@models4insight/services/project';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { defaultControlShellContext } from '../control-shell';
import { ModalContext } from '../modal';
import {
  AbstractSelectComponent,
  defaultSelectContext,
  SelectContext,
} from '../select';
import { SortableTableShellConfig } from '../sortable-table-shell';

const projectsModalContext: ModalContext = {
  cancel: 'Close',
  closeOnConfirm: true,
  title: 'Choose a project',
};

const projectsTableConfig: SortableTableShellConfig<Project> = {
  name: { displayName: 'Project name', description: 'The name of the project' },
  documentation: {
    displayName: 'Description',
    description: 'The description of the project',
  },
  last_updated: {
    displayName: 'Last updated on',
    isTimestamp: true,
    description: 'The timestamp of the latest change to the project',
  },
};

const defaultProjectSelectContext: SelectContext = {
  ...defaultSelectContext,
  icon: faProjectDiagram,
  label: 'Project',
  requiredErrorMessage: 'Please select a project',
  nullInputMessage: 'Please select a project',
  searchModalContext: projectsModalContext,
  searchTableConfig: projectsTableConfig,
};

@Component({
  selector: 'models4insight-project-select',
  templateUrl: 'project-select.component.html',
  styleUrls: ['project-select.component.scss'],
})
export class ProjectSelectComponent
  extends AbstractSelectComponent<Project>
  implements OnInit
{
  projects$: Observable<Project[]>;

  constructor(
    private readonly projectService: ProjectService,
    private readonly projectsService: ProjectsService
  ) {
    super();
  }

  ngOnInit() {
    if (
      this.context === defaultControlShellContext ||
      this.context === defaultSelectContext
    ) {
      this.context = defaultProjectSelectContext;
    }
    this.displayField = 'name';

    this.projects$ = this.projectsService.projects;

    // Whenever the current project changes, update the control
    this.projectService
      .selectCurrentProject()
      .pipe(untilDestroyed(this))
      .subscribe((project) => {
        if (project) {
          this.control.patchValue(project, { emitEvent: false });
        } else {
          this.control.reset(null, { emitEvent: false });
        }
      });

    // Whenever a project is selected, update the current project
    this.control.valueChanges
      .pipe(untilDestroyed(this))
      .subscribe((project: Project) =>
        this.projectService.setCurrentProject(project?.id)
      );
  }
}
