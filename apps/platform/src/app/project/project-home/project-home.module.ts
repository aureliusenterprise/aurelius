import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { BranchSelectModule, CalendarHeatmapModule, ContextMenuModule, DescriptionInputModule, FileDropzoneModule, SortableTableShellModule } from '@models4insight/components';
import { BranchPermissionModule, ProjectPermissionModule } from '@models4insight/permissions';
import { TranslateModule } from '@ngx-translate/core';
import { ProjectHomeRoutingModule } from './project-home-routing.module';
import { ProjectHomeComponent } from './project-home.component';
import { ProjectHomeGuard } from './project-home.guard';
import { ProjectHomeResolver } from './project-home.resolver';
import { ProjectHomeService } from './project-home.service';
import { RecentActivityContextMenuComponent } from './recent-activity-table/recent-activity-context-menu/recent-activity-context-menu.component';
import { RecentActivityTableComponent } from './recent-activity-table/recent-activity-table.component';

@NgModule({
  imports: [
    CalendarHeatmapModule,
    CommonModule,
    FontAwesomeModule,
    TranslateModule,
    ProjectHomeRoutingModule,
    ReactiveFormsModule,
    ProjectPermissionModule,
    BranchPermissionModule,
    FileDropzoneModule,
    BranchSelectModule,
    DescriptionInputModule,
    ContextMenuModule,
    SortableTableShellModule
  ],
  declarations: [
    ProjectHomeComponent,
    RecentActivityTableComponent,
    RecentActivityContextMenuComponent
  ],
  providers: [ProjectHomeGuard, ProjectHomeResolver, ProjectHomeService]
})
export class ProjectHomeModule {}
