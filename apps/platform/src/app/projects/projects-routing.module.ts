import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Shell, ShellModule } from '@models4insight/shell';
import { ProjectsComponent } from './projects.component';

const routes: Routes = [
  Shell.childRoutes([
    {
      path: '',
      component: ProjectsComponent,
      data: { title: 'Projects' }
    }
  ])
];

@NgModule({
  imports: [RouterModule.forChild(routes), ShellModule],
  exports: [RouterModule],
  providers: []
})
export class ProjectsRoutingModule {}
