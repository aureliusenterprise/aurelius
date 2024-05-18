import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { ConflictResolutionComponent } from './conflict-resolution.component';
import { ConflictResolutionGuard } from './conflict-resolution.guard';

const routes: Routes = [
  {
    path: '',
    component: ConflictResolutionComponent,
    data: {
      title: extract('Resolve conflicts')
    },
    canActivate: [ConflictResolutionGuard]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: []
})
export class ConflictResolutionRoutingModule {}
