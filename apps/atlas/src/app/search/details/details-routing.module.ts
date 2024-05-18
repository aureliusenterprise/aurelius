import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DetailsComponent } from './details.component';
import { DetailsResolver } from './details.resolver';

const routes: Routes = [
  {
    path: ':id',
    component: DetailsComponent,
    resolve: { entityId: DetailsResolver },
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class DetailsRoutingModule {}
