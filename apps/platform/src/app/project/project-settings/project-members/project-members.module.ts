import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { ContextMenuModule, PermissionSelectModule, SortableTableShellModule, UserSearchModalModule } from '@models4insight/components';
import { ProjectPermissionModule } from '@models4insight/permissions';
import { ProjectMemberTableContextMenuComponent } from './project-member-table/project-member-table-context-menu/project-member-table-context-menu.component';
import { ProjectMemberTableComponent } from './project-member-table/project-member-table.component';
import { ProjectMemberSettingsRoutingModule } from './project-members-routing.module';
import { ProjectMemberSettingsComponent } from './project-members.component';

@NgModule({
  imports: [
    CommonModule,
    ProjectPermissionModule,
    ProjectMemberSettingsRoutingModule,
    ContextMenuModule,
    UserSearchModalModule,
    PermissionSelectModule,
    SortableTableShellModule
  ],
  declarations: [
    ProjectMemberSettingsComponent,
    ProjectMemberTableComponent,
    ProjectMemberTableContextMenuComponent
  ]
})
export class ProjectMemberSettingsModule {}
