import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { CreateProjectModalComponent, defaultSimpleSearchInputContext, FuzzySearchTokenizerConfig, SimpleSearchInputContext, SortableTableComponent, SortableTableShellConfig } from '@models4insight/components';
import { Project } from '@models4insight/repository';
import { ProjectsService } from '@models4insight/services/project';
import { untilDestroyed } from '@models4insight/utils';
import { merge, Observable } from 'rxjs';
import { ProjectsSearchService } from './projects-search.service';

const searchInputContext: SimpleSearchInputContext = {
  ...defaultSimpleSearchInputContext,
  inputClasses: ['is-medium'],
  label: null,
  placeholder: 'Project name or owner...',
  withSubmitButton: false
};

const projectsTableOptions: SortableTableShellConfig<Project> = {
  name: { displayName: 'Project name', description: 'The name of the project' },
  owner: {
    displayName: 'Project owner',
    description: 'The name of the user who created the project'
  },
  last_updated: {
    displayName: 'Last updated on',
    description: 'When the latest activity in this project occurred',
    isTimestamp: true
  }
};

const projectTokenizerConfig: FuzzySearchTokenizerConfig<Project> = {
  id: {static: true},
  name: {},
  documentation: {},
  owner: {}
}

@Component({
  selector: 'models4insight-projects',
  templateUrl: './projects.component.html',
  styleUrls: ['./projects.component.scss'],
  providers: [ProjectsSearchService]
})
export class ProjectsComponent implements OnInit, OnDestroy {
  readonly projectsTableOptions = projectsTableOptions;
  readonly projectTokenizerConfig = projectTokenizerConfig;
  readonly searchInputContext = searchInputContext;

  filteredProjects$: Observable<Project[]>;
  isCreatingProject$: Observable<boolean>;
  projects$: Observable<Project[]>;

  @ViewChild(CreateProjectModalComponent, { static: true })
  private readonly createProjectModal: CreateProjectModalComponent;

  @ViewChild(SortableTableComponent, { static: true })
  private readonly projectsTable: SortableTableComponent<Project>;

  constructor(
    private readonly projectsSearchService: ProjectsSearchService,
    private readonly projectsService: ProjectsService,
    private router: Router
  ) {}

  ngOnInit() {
    this.filteredProjects$ = this.projectsSearchService.select(
      'filteredProjects'
    );
    this.isCreatingProject$ = this.projectsService.select('isCreatingProject');
    this.projects$ = this.projectsService.projects;

    merge(this.projectsService.onProjectCreated, this.projectsTable.rowClicked)
      .pipe(untilDestroyed(this))
      .subscribe(project => this.openProject(project));
  }

  ngOnDestroy() {}

  activateModal() {
    this.createProjectModal.activate();
  }

  openProject(project: Project) {
    this.router.navigate(['/project', project.id]);
  }

  updateSuggestedProjects(suggestedProjects: Project[]) {
    this.projectsSearchService.update({
      description: 'New suggested projects available',
      payload: { suggestedProjects }
    });
  }
}
