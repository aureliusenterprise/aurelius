import { Injectable } from '@angular/core';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import { Project } from '@models4insight/repository';
import { ProjectsService } from '@models4insight/services/project';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { combineLatest, Subject } from 'rxjs';
import { concatMap, map } from 'rxjs/operators';
import { ServicesUserInfoModule } from './services-user-info.module';
import { UserInfoService } from './user-info.service';

export interface RecentProjectsStoreContext {
  readonly isAddingRecentProject?: boolean;
}

@Injectable({
  providedIn: ServicesUserInfoModule,
})
export class RecentProjectsService extends BasicStore {
  private readonly addRecentProject$ = new Subject<Project>();
  constructor(
    private readonly projectsService: ProjectsService,
    private readonly userInfoService: UserInfoService,
    readonly storeService: StoreService
  ) {
    super({ name: 'RecentProjectsService', storeService });
    this.init();
  }

  private init() {
    this.addRecentProject$
      .pipe(
        concatMap((project) => this.handleAddRecentProject(project)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  /**
   * Adds the given project to the user's recently visited projects
   * @param project The project that should be added to the list
   */
  addRecentProject(project: Project) {
    this.addRecentProject$.next(project);
  }

  /**
   * Returns a snapshot of the current user's recently visited projects as a `Promise`
   */
  async getRecentProjects() {
    const [recentProjectIds, projectsById] = await Promise.all([
      this.userInfoService.get(['userInfo', 'recent_projects']),
      this.projectsService.get('projectsById'),
    ]);

    return recentProjectIds
      .filter((projectId) => projectId in projectsById)
      .map((projectId) => projectsById[projectId]);
  }

  /**
   * Returns an `Observable` stream of the current user's recently visited projects
   */
  selectRecentProjects() {
    return combineLatest([
      this.userInfoService.select(['userInfo', 'recent_projects']),
      this.projectsService.select('projectsById'),
    ]).pipe(
      map(([recentProjectIds, projectsById]) =>
        recentProjectIds
          .filter((projectId) => projectId in projectsById)
          .map((projectId) => projectsById[projectId])
      )
    );
  }

  @ManagedTask('Updating your recent projects', { isQuiet: true })
  @MonitorAsync('isAddingRecentProject')
  private async handleAddRecentProject(project: Project) {
    // If the recent projects are unavailable, start with an empty list
    const recentProjects =
      (await this.userInfoService.get(['userInfo', 'recent_projects'], {
        includeFalsy: true,
      })) ?? [];

    const updatedRecentProjects = [
      project?.id,
      ...recentProjects.filter(
        (recentProject) => recentProject !== project?.id
      ),
    ].slice(0, 5);

    this.userInfoService.update({
      description: 'Recent projects updated',
      path: ['userInfo', 'recent_projects'],
      payload: updatedRecentProjects,
    });

    return project;
  }
}
