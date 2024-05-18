import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { AuthenticationService, Credentials } from '@models4insight/authentication';
import { SortableTableComponent, SortableTableShellConfig } from '@models4insight/components';
import { Project } from '@models4insight/repository';
import { FavoriteProjectsService, LastVisitedRoute, LastVisitedRouteService, RecentProjectsService, UserInfoService } from '@models4insight/services/user-info';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';

const projectsTableConfig: SortableTableShellConfig<Project> = {
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

@Component({
  selector: 'models4insight-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  credentials$: Observable<Credentials>;
  favoriteProjects$: Observable<Project[]>;
  lastVisitedRoute$: Observable<LastVisitedRoute>;
  recentProjects$: Observable<Project[]>;
  skipWelcome$: Observable<boolean>;

  projectsTableConfig = projectsTableConfig;

  constructor(
    private readonly authenticationService: AuthenticationService,
    private readonly continueWorkingService: LastVisitedRouteService,
    private readonly favoriteProjectsService: FavoriteProjectsService,
    private readonly recentProjectsService: RecentProjectsService,
    private readonly router: Router,
    private readonly userInfoService: UserInfoService
  ) {}

  ngOnInit() {
    this.credentials$ = this.authenticationService
      .credentials()
      .pipe(shareReplay());
    this.favoriteProjects$ = this.favoriteProjectsService.selectFavoriteProjects();
    this.lastVisitedRoute$ = this.continueWorkingService.selectLastVisitedRoute();
    this.recentProjects$ = this.recentProjectsService.selectRecentProjects();
    this.skipWelcome$ = this.userInfoService.select([
      'userInfo',
      'skip_welcome'
    ]);
  }

  iGotIt() {
    this.userInfoService.update({
      description: 'Skip welcome enabled',
      path: ['userInfo', 'skip_welcome'],
      payload: true
    });
  }

  showWelcome() {
    this.userInfoService.update({
      description: 'Skip welcome disabled',
      path: ['userInfo', 'skip_welcome'],
      payload: false
    });
  }

  navigateToProject(id: string) {
    this.router.navigate(['project', id]);
  }

  @ViewChild('favoriteProjectsTable', { static: false })
  set favoriteProjectsTable(table: SortableTableComponent<Project>) {
    if (table) {
      table.rowClicked
        .pipe(untilDestroyed(table))
        .subscribe(project => this.navigateToProject(project.id));
    }
  }

  @ViewChild('recentProjectsTable', { static: false }) set recentProjectsTable(
    table: SortableTableComponent<Project>
  ) {
    if (table) {
      table.rowClicked
        .pipe(untilDestroyed(table))
        .subscribe(project => this.navigateToProject(project.id));
    }
  }
}
