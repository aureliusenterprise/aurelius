import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { ModelExploreComponent } from './model-explore.component';
import { ModelExploreGuard } from './model-explore.guard';
import { ModelExploreResolver } from './model-explore.resolver';

const routes: Routes = [
  {
    path: '',
    component: ModelExploreComponent,
    data: {
      title: extract('Model Explorer')
    },
    canActivate: [ModelExploreGuard],
    resolve: { modelExploreParams: ModelExploreResolver }
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: []
})
export class ModelExploreRoutingModule {}
