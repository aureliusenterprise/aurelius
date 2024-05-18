import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { ModelRetrieveComponent } from './model-retrieve.component';
import { ModelRetrieveGuard } from './model-retrieve.guard';
import { ModelRetrieveResolver } from './model-retrieve.resolver';

const routes: Routes = [
  {
    path: '',
    component: ModelRetrieveComponent,
    data: {
      title: extract('Retrieve a model')
    },
    canActivate: [ModelRetrieveGuard],
    resolve: { modelRetrieveParams: ModelRetrieveResolver },
    runGuardsAndResolvers: 'paramsOrQueryParamsChange'
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: []
})
export class ModelRetrieveRoutingModule {}
