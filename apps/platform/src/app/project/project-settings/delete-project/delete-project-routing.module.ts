import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { DeleteProjectSettingsGuard } from './delete-project.guard';
import { DeleteProjectSettingsComponent } from './delete-project.component';

const routes: Routes = [
  {
    path: '',
    component: DeleteProjectSettingsComponent,
    data: {
      title: extract('Delete Project')
    },
    canActivate: [DeleteProjectSettingsGuard]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: []
})
export class DeleteProjectSettingsRoutingModule {}
