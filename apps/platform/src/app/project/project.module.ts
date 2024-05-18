import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { CompareModalModule, HeroModule } from '@models4insight/components';
import { BranchPermissionModule, ProjectPermissionModule } from '@models4insight/permissions';
import { RepositoryModule } from '@models4insight/repository';
import { TranslateModule } from '@ngx-translate/core';
import { CompareModalService } from './compare-modal.service';
import { ConflictNotificationService } from './conflict-notification.service';
import { ProjectRoutingModule } from './project-routing.module';
import { ProjectComponent } from './project.component';
import { ProjectGuard } from './project.guard';
import { TrackRecentProjectsService } from './track-recent-projects.service';

@NgModule({
  imports: [
    BranchPermissionModule.forRoot(),
    CommonModule,
    CompareModalModule,
    FontAwesomeModule,
    HeroModule,
    ProjectPermissionModule.forRoot(),
    ProjectRoutingModule,
    RepositoryModule,
    TranslateModule
  ],
  declarations: [ProjectComponent],
  providers: [
    CompareModalService,
    ConflictNotificationService,
    ProjectGuard,
    TrackRecentProjectsService
  ]
})
export class ProjectModule {
  constructor(
    readonly conflictNotificationService: ConflictNotificationService,
    readonly trackRecentProjectsService: TrackRecentProjectsService
  ) {
    conflictNotificationService.init();
    trackRecentProjectsService.init();
  }
}
