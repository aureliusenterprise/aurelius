import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { EditEntityResolver } from './edit-entity-resolver';
import { EditEntityComponent } from './edit-entity.component';


const routes: Routes = [
  {
    path: ':id',
    component: EditEntityComponent,
    resolve: { entityId: EditEntityResolver },
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class EditEntityRoutingModule {}
