import { Injectable } from '@angular/core';
import { BasicStore, StoreService } from '@models4insight/redux';
import { switchMap } from 'rxjs/operators';
import { ProjectsService } from './projects.service';
import { ServicesProjectModule } from './services-project.module';

export interface ProjectStoreContext {
  /** The id of the current project */
  readonly projectId?: string;
}

@Injectable({
  providedIn: ServicesProjectModule,
})
export class ProjectService extends BasicStore<ProjectStoreContext> {
  constructor(
    private readonly projectsService: ProjectsService,
    storeService: StoreService
  ) {
    super({
      name: 'ProjectService',
      storeService,
    });
  }

  /**
   * Returns a snapshot of the current `Project` as a `Promise`.
   */
  async getCurrentProject() {
    const projectId = await this.get('projectId');
    return this.projectsService.getProjectById(projectId);
  }

  /**
   * Deletes the current project
   */
  async deleteCurrentProject() {
    const project = await this.getCurrentProject();
    this.projectsService.deleteProject(project);
  }

  /**
   * Returns an `Observable` stream of the current `Project`.
   */
  selectCurrentProject() {
    return this.select('projectId').pipe(
      switchMap((projectId) =>
        this.projectsService.selectProjectById(projectId)
      )
    );
  }

  /** Updates the ID of the currently selected `Project` */
  setCurrentProject(projectId: string) {
    this.update({
      description: `Project ${projectId} selected`,
      payload: {
        projectId,
      },
    });
  }
}
