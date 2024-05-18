import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { ProjectHomeComponent } from './project-home.component';
import { ProjectHomeResolver } from './project-home.resolver';
import { ProjectHomeGuard } from './project-home.guard';

const routes: Routes = [
  {
    path: '',
    component: ProjectHomeComponent,
    data: {
      title: extract('Project Home')
    },
    canActivate: [ProjectHomeGuard],
    resolve: { projectHomeParams: ProjectHomeResolver }
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: []
})
export class ProjectHomeRoutingModule {}
