import { Injectable, OnDestroy } from '@angular/core';
import { ProjectService } from '@models4insight/services/project';
import { RecentProjectsService } from '@models4insight/services/user-info';
import { untilDestroyed } from '@models4insight/utils';

// TODO: Add Angular decorator.
@Injectable()
export class TrackRecentProjectsService implements OnDestroy {
  constructor(
    private readonly projectService: ProjectService,
    private readonly recentProjectsService: RecentProjectsService
  ) {}

  ngOnDestroy() {}

  init() {
    this.projectService
      .selectCurrentProject()
      .pipe(untilDestroyed(this))
      .subscribe(project =>
        this.recentProjectsService.addRecentProject(project)
      );
  }
}
