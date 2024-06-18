import { Inject, Injectable } from '@angular/core';
import { AuthenticationService } from '@models4insight/authentication';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import {
  createProject,
  deleteProject,
  getUserProjects,
  Project,
  updateProject,
} from '@models4insight/repository';
import { ManagedTask } from '@models4insight/task-manager';
import { indexByProperty, untilDestroyed } from '@models4insight/utils';
import { Dictionary, orderBy } from 'lodash';
import { from, Observable, Subject } from 'rxjs';
import { concatMap, map, mergeMap, switchMap } from 'rxjs/operators';
import { ProjectServiceConfig } from './services-project-config.service';
import { ServicesProjectModule } from './services-project.module';

export interface ProjectsStoreContext {
  readonly isCreatingProject?: boolean;
  readonly isDeletingProject?: boolean;
  readonly isRetrievingProjects?: boolean;
  readonly isUpdatingProject?: boolean;
  readonly projectsById?: Dictionary<Project>;
}

export const defaultProjectsServiceState: ProjectsStoreContext = {
  isCreatingProject: false,
  isDeletingProject: false,
  isRetrievingProjects: false,
  isUpdatingProject: false,
};

@Injectable({
  providedIn: ServicesProjectModule,
})
export class ProjectsService extends BasicStore<ProjectsStoreContext> {
  private readonly createProject$ = new Subject<Project>();
  private readonly projectCreated$ = new Subject<Project>();
  private readonly deleteProject$ = new Subject<Project>();
  private readonly projectDeleted$ = new Subject<void>();
  private readonly projectUpdated$ = new Subject<Project>();

  constructor(
    private readonly authenticationService: AuthenticationService,
    @Inject(ProjectServiceConfig) private readonly config: ProjectServiceConfig,
    storeService: StoreService
  ) {
    super({
      defaultState: defaultProjectsServiceState,
      name: 'ProjectsService',
      storeService,
    });

    if (!this.config.standalone) {
      this.init();
    }
  }

  private init() {
    // Whenever the username of the user changes, retrieve the projects of the current user

    this.authenticationService
      .select(['credentials', 'username'])
      .pipe(
        switchMap((username) => this.handleRetrieveProjects(username)),
        untilDestroyed(this)
      )
      .subscribe();

    this.createProject$
      .pipe(
        concatMap((project) => this.handleCreateProject(project)),
        untilDestroyed(this)
      )
      .subscribe(this.projectCreated$);

    this.deleteProject$
      .pipe(
        concatMap((project) => this.handleDeleteProject(project)),
        untilDestroyed(this)
      )
      .subscribe(this.projectDeleted$);

    // Whenever a project is added or changes, save it to the repository
    this.watch('projectsById')
      .pipe(
        concatMap((projects) => from(projects)),
        mergeMap((project) => this.handleUpdateProject(project)),
        untilDestroyed(this)
      )
      .subscribe(this.projectUpdated$);
  }

  @ManagedTask('Creating the project', { isQuiet: true })
  @MonitorAsync('isCreatingProject')
  private async handleCreateProject(project: Project) {
    const { username, email } = await this.authenticationService.get(
      'credentials'
    );

    const projectCreateResponse = await createProject(
      project,
      username,
      email
    ).toPromise();

    this.updateProject(projectCreateResponse);

    return projectCreateResponse;
  }

  /**
   * Saves the given project to the back end.
   * Use this function if your project does not yet have an ID.
   */
  createProject(project: Project) {
    this.updateProject(project);
  }

  /**
   * Deletes the given project
   */
  deleteProject(project: Project) {
    this.deleteProject$.next(project);
  }

  /**
   * Saves the given project to the back end.
   */
  updateProject(project: Project) {
    if (project?.id) {
      this.update({
        description: `Project ${project.id} updated`,
        path: ['projectsById', project.id],
        payload: project,
      });
    } else {
      this.createProject$.next(project);
    }
  }

  /**
   * Returns a snapshot of the `Project` with the given `projectId` as a `Promise`.
   * @param projectId the ID of the project to retrieve
   */
  async getProjectById(projectId: string) {
    return this.get(['projectsById', projectId]);
  }

  /**
   * Returns an `Observable` stream of the `Project` with the given `projectId`.
   * @param projectId the ID of the project to observe
   */
  selectProjectById(projectId: string) {
    return this.select(['projectsById', projectId]);
  }

  /**
   * An `Observable` stream of an `Array` containing all the user's current `Projects`.
   */
  get projects(): Observable<Project[]> {
    return this.select('projectsById').pipe(
      map((projectsById) => {
        const projects = Object.values(projectsById);
        return orderBy(projects, 'last_updated', 'desc');
      })
    );
  }

  /**
   * Emits whenever a project has been created.
   */
  get onProjectCreated(): Observable<Project> {
    return this.projectCreated$.asObservable();
  }

  /**
   * Emits whenever a project has been deleted.
   */
  get onProjectDeleted(): Observable<void> {
    return this.projectDeleted$.asObservable();
  }

  /**
   * Emits whenever a project has been updated.
   */
  get onProjectUpdated(): Observable<Project> {
    return this.projectUpdated$.asObservable();
  }

  @ManagedTask('Deleting the project', { isQuiet: true })
  @MonitorAsync('isDeletingProject')
  private async handleDeleteProject(project: Project) {
    await deleteProject(project?.id).toPromise();

    this.delete({
      description: `Project ${project?.id} deleted`,
      path: ['projectsById', project?.id],
    });
  }

  @ManagedTask('Retrieving your projects', { isQuiet: true })
  @MonitorAsync('isRetrievingProjects')
  private async handleRetrieveProjects(username: string) {
    const projects = await getUserProjects(username).toPromise();

    const projectsById = indexByProperty(projects, 'id');

    this.update({
      description: 'New projects available',
      payload: { projectsById },
    });
  }

  @ManagedTask('Saving the project', { isQuiet: true })
  @MonitorAsync('isUpdatingProject')
  private async handleUpdateProject(project: Project) {
    return updateProject(project.id, project).toPromise();
  }
}
