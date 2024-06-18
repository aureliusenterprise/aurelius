import { Injectable } from '@angular/core';
import { BasicStore, MonitorAsync, StoreService } from '@models4insight/redux';
import { Project } from '@models4insight/repository';
import {
  ProjectService,
  ProjectsService,
} from '@models4insight/services/project';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { combineLatest, Subject } from 'rxjs';
import { concatMap, map } from 'rxjs/operators';
import { ServicesUserInfoModule } from './services-user-info.module';
import { UserInfoService } from './user-info.service';

export interface FavoriteProjectsStoreContext {
  readonly isAddingFavoriteProject?: boolean;
}

@Injectable({
  providedIn: ServicesUserInfoModule,
})
export class FavoriteProjectsService extends BasicStore<FavoriteProjectsStoreContext> {
  private readonly addFavoriteProject$ = new Subject<Project>();
  private readonly removeFavoriteProject$ = new Subject<Project>();

  constructor(
    private readonly projectsService: ProjectsService,
    private readonly projectService: ProjectService,
    private readonly userInfoService: UserInfoService,
    readonly storeService: StoreService
  ) {
    super({
      name: 'FavoriteProjectsService',
      storeService,
    });
    this.init();
  }

  private init() {
    this.addFavoriteProject$
      .pipe(
        concatMap((project) => this.handleAddFavoriteProject(project)),
        untilDestroyed(this)
      )
      .subscribe();

    this.removeFavoriteProject$
      .pipe(
        concatMap((project) => this.handleRemoveFavoriteProject(project)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  /**
   * Register the given project as one of the current user's favorites.
   * @param project The project that should be registered as a favorite.
   */
  addFavoriteProject(project: Project) {
    this.addFavoriteProject$.next(project);
  }

  /**
   * Returns a snapshot of the current user's favorite projects as a `Promise`
   */
  async getFavoriteProjects() {
    const [favoriteProjectIds, projectsById] = await Promise.all([
      this.userInfoService.get(['userInfo', 'favorite_projects']),
      this.projectsService.get('projectsById'),
    ]);

    return favoriteProjectIds
      .filter((projectId) => projectId in projectsById)
      .map((projectId) => projectsById[projectId]);
  }

  /**
   * Unregisters the given project as one of the current user's favorites.
   * @param project The project that should be unregistered as a favorite.
   */
  removeFavoriteProject(project: Project) {
    this.removeFavoriteProject$.next(project);
  }

  /**
   * Returns an `Observable` stream of the current user's favorite projects
   */
  selectFavoriteProjects() {
    return combineLatest([
      this.userInfoService.select(['userInfo', 'favorite_projects']),
      this.projectsService.select('projectsById'),
    ]).pipe(
      map(([favoriteProjectIds, projectsById]) =>
        favoriteProjectIds
          .filter((projectId) => projectId in projectsById)
          .map((projectId) => projectsById[projectId])
      )
    );
  }

  /**
   * Returns whether the current projcect is a favorite as an `Observable` stream.
   */
  get isCurrentProjectFavorite() {
    return combineLatest([
      this.projectService.select('projectId'),
      this.userInfoService.select(['userInfo', 'favorite_projects'], {
        includeFalsy: true,
      }),
    ]).pipe(
      map(
        ([projectId, favoriteProjects]) =>
          !!favoriteProjects?.includes(projectId)
      )
    );
  }

  @ManagedTask('Adding a favorite project', { isQuiet: true })
  @MonitorAsync('isAddingFavoriteProject')
  private async handleAddFavoriteProject(project: Project) {
    // If the favorite projects are unavailable, start with an empty list
    const favoriteProjects =
      (await this.userInfoService.get(['userInfo', 'favorite_projects'], {
        includeFalsy: true,
      })) ?? [];

    const updatedFavoriteProjects = [
      project?.id,
      ...favoriteProjects.filter(
        (favoriteProject) => favoriteProject !== project?.id
      ),
    ];

    this.userInfoService.update({
      description: 'Favorite projects updated',
      path: ['userInfo', 'favorite_projects'],
      payload: updatedFavoriteProjects,
    });

    return project;
  }

  @ManagedTask('Removing a favorite project', { isQuiet: true })
  @MonitorAsync('isRemovingFavoriteProject')
  private async handleRemoveFavoriteProject(project: Project) {
    const favoriteProjects = await this.userInfoService.get([
      'userInfo',
      'favorite_projects',
    ]);

    const updatedFavoriteProjects = favoriteProjects.filter(
      (favoriteProject) => favoriteProject !== project?.id
    );

    this.userInfoService.update({
      description: 'Favorite project removed',
      path: ['userInfo', 'favorite_projects'],
      payload: updatedFavoriteProjects,
    });

    return project;
  }
}
