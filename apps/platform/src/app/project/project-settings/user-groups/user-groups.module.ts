import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { ContextMenuModule, CreateUserGroupModalModule, PermissionSelectModule, SortableTableShellModule } from '@models4insight/components';
import { ProjectPermissionModule } from '@models4insight/permissions';
import { UserGroupContextMenuComponent } from './user-group-table/user-group-context-menu/user-group-context-menu.component';
import { UserGroupTableComponent } from './user-group-table/user-group-table.component';
import { UserGroupsSettingsRoutingModule } from './user-groups-routing.module';
import { UserGroupsSettingsComponent } from './user-groups.component';

@NgModule({
  imports: [
    CommonModule,
    PermissionSelectModule,
    UserGroupsSettingsRoutingModule,
    PermissionSelectModule,
    ProjectPermissionModule,
    ContextMenuModule,
    CreateUserGroupModalModule,
    SortableTableShellModule
  ],
  declarations: [
    UserGroupsSettingsComponent,
    UserGroupTableComponent,
    UserGroupContextMenuComponent
  ]
})
export class UserGroupsSettingsModule {}
