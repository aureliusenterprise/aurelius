import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Shell, ShellModule } from '@models4insight/shell';
import { ProjectComponent } from './project.component';
import { ProjectGuard } from './project.guard';

const childRoutes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'home'
  },
  {
    path: 'home',
    loadChildren: () =>
      import('./project-home/project-home.module').then(
        m => m.ProjectHomeModule
      )
  },
  {
    path: 'upload',
    loadChildren: () =>
      import('./file-upload/file-upload.module').then(m => m.FileUploadModule)
  },
  {
    path: 'retrieve',
    loadChildren: () =>
      import('./model-retrieve/model-retrieve.module').then(
        m => m.ModelRetrieveModule
      )
  },
  {
    path: 'branches',
    loadChildren: () =>
      import('./branch-merge/branch-merge.module').then(
        m => m.BranchMergeModule
      )
  },
  {
    path: 'conflicts',
    loadChildren: () =>
      import('./conlict-resolution/conflict-resolution.module').then(
        m => m.ConflictResolutionModule
      )
  },
  {
    path: 'settings',
    loadChildren: () =>
      import('./project-settings/project-settings.module').then(
        m => m.ProjectSettingsModule
      )
  },
  {
    path: 'explore',
    loadChildren: () =>
      import('./model/model-explore.module').then(m => m.ModelExploreModule)
  },
  {
    path: 'compare',
    loadChildren: () =>
      import('./model-compare/model-compare.module').then(
        m => m.ModelCompareModule
      )
  },
  {
    path: '**',
    pathMatch: 'full',
    redirectTo: 'home'
  }
];

const routes: Routes = [
  Shell.childRoutes([
    {
      path: ':id',
      component: ProjectComponent,
      data: { title: 'Project' },
      children: childRoutes,
      canActivate: [ProjectGuard]
    }
  ])
];

@NgModule({
  imports: [RouterModule.forChild(routes), ShellModule],
  exports: [RouterModule],
  providers: []
})
export class ProjectRoutingModule {}
