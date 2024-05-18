import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Shell, ShellModule } from '@models4insight/shell';
import { AboutComponent } from './about.component';

const routes: Routes = [
  Shell.childRoutes([
    {
      path: '',
      component: AboutComponent,
      data: { title: 'About' }
    }
  ])
];

@NgModule({
  imports: [RouterModule.forChild(routes), ShellModule],
  exports: [RouterModule]
})
export class AboutRoutingModule {}
