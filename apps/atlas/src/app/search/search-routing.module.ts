import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Shell } from '@models4insight/shell';
import { BrowseComponent } from './browse/browse.component';
import { CreateEntityComponent } from './create-entity/create-entity.component';
import { QueryResolver } from './query.resolver';
import { ResultsComponent } from './results/results.component';
import { SearchComponent } from './search.component';

const childRoutes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'browse'
  },
  {
    path: 'browse',
    component: BrowseComponent
  },
  {
    path: 'results',
    component: ResultsComponent,
    resolve: { query: QueryResolver },
    runGuardsAndResolvers: 'paramsOrQueryParamsChange'
  },
  {
    path: 'details',
    loadChildren: () =>
      import('./details/details.module').then(m => m.DetailsModule)
  },
  {
    path: 'create-entity',
    component: CreateEntityComponent
  },
  {
    path: 'edit-entity',
    loadChildren: () =>
      import('./edit-entity/edit-entity.module').then(m => m.EditEntityModule)
  },
  {
    path: '**',
    pathMatch: 'full',
    redirectTo: 'browse'
  }
];

const routes: Routes = [
  Shell.childRoutes([
    {
      path: '',
      component: SearchComponent,
      children: childRoutes
    }
  ])
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: [QueryResolver]
})
export class SearchRoutingModule {}
