import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { ProjectDescriptionSettingsComponent } from './project-description.component';


const routes: Routes = [
  {
    path: '',
    component: ProjectDescriptionSettingsComponent,
    data: {
      title: extract('Project Info')
    },
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: []
})
export class ProjectDescriptionSettingsRoutingModule {}
