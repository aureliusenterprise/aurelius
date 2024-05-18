import { Injectable } from '@angular/core';
import { BasicStore } from '@models4insight/redux';
import { Project } from '@models4insight/repository';
import { ProjectsService as Projects } from '@models4insight/services/project';
import { untilDestroyed } from '@models4insight/utils';
import { combineLatest } from 'rxjs';
import { map } from 'rxjs/operators';

export interface ProjectsStoreContext {
  readonly suggestedProjects?: Project[];
  readonly filteredProjects?: Project[];
  readonly search?: string;
}

export const projectsServiceDefaultState: ProjectsStoreContext = {
  filteredProjects: [],
  suggestedProjects: []
};

@Injectable()
export class ProjectsSearchService extends BasicStore<ProjectsStoreContext> {
  constructor(private projectsService: Projects) {
    super({
      defaultState: projectsServiceDefaultState
    });
    this.init();
  }

  private init() {
    combineLatest([
      this.projectsService.projects,
      this.select('suggestedProjects')
    ])
      .pipe(
        map(([projects, search]) =>
          this.handleFilterProjects(projects, search)
        ),
        untilDestroyed(this)
      )
      .subscribe();
  }

  private handleFilterProjects(
    projects: Project[],
    suggestedProjects: Project[]
  ) {
    const filteredProjects = suggestedProjects.length
      ? suggestedProjects
      : projects;

    this.update({
      description: 'New filtered user projects available',
      payload: { filteredProjects }
    });
  }
}
