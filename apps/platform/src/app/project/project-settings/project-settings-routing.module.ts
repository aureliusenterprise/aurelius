import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { ProjectSettingsComponent } from './project-settings.component';
import { ProjectSettingsGuard } from './project-settings.guard';

const childRoutes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'info'
  },
  {
    path: 'groups',
    loadChildren: () =>
      import('./user-groups/user-groups.module').then(
        m => m.UserGroupsSettingsModule
      )
  },
  {
    path: 'info',
    loadChildren: () =>
      import('./project-description/project-description.module').then(
        m => m.ProjectDescriptionSettingsModule
      )
  },
  {
    path: 'members',
    loadChildren: () =>
      import('./project-members/project-members.module').then(
        m => m.ProjectMemberSettingsModule
      )
  },
  {
    path: 'delete',
    loadChildren: () =>
      import('./delete-project/delete-project.module').then(
        m => m.DeleteProjectSettingsModule
      )
  },
  {
    path: '**',
    pathMatch: 'full',
    redirectTo: 'info'
  }
];

const routes: Routes = [
  {
    path: '',
    component: ProjectSettingsComponent,
    children: childRoutes,
    data: {
      title: extract('Project Settings')
    },
    canActivate: [ProjectSettingsGuard]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: []
})
export class ProjectSettingsRoutingModule {}
