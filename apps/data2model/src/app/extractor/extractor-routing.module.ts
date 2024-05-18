import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Shell, ShellModule } from '@models4insight/shell';
import { ExtractorComponent } from './extractor.component';

const childRoutes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'upload'
  },
  {
    path: 'dataset',
    loadChildren: () => import('./dataset/dataset.module').then(m => m.DatasetModule)
  },
  {
    path: 'model',
    loadChildren: () => import('./model/model-explore.module').then(m => m.ModelExploreModule)
  },
  {
    path: 'rules',
    loadChildren: () => import('./rules/rules.module').then(m => m.RulesModule)
  },
  {
    path: 'suggestions',
    loadChildren: () => import('./suggestions/suggestions.module').then(m => m.SuggestionsModule)
  },
  {
    path: 'upload',
    loadChildren: () => import('./file-upload/file-upload.module').then(m => m.FileUploadModule)
  }
];

const routes: Routes = [
  Shell.childRoutes([
    {
      path: '',
      component: ExtractorComponent,
      // Reuse ExtractorComponent instance when navigating between child views
      data: { reuse: true, title: 'Model Extractor' },
      children: childRoutes
    }
  ])
];

@NgModule({
  imports: [RouterModule.forChild(routes), ShellModule],
  exports: [RouterModule],
  providers: []
})
export class ExtractorRoutingModule {}
