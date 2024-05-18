import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { ProjectMemberSettingsComponent } from './project-members.component';

const routes: Routes = [
  {
    path: '',
    component: ProjectMemberSettingsComponent,
    data: {
      title: extract('Project Members')
    }
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: []
})
export class ProjectMemberSettingsRoutingModule {}
