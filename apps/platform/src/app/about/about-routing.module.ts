import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { Shell, ShellModule } from '@models4insight/shell';
import { AboutComponent } from './about.component';


const routes: Routes = [
  Shell.childRoutes([
    { path: '', component: AboutComponent, data: { title: extract('About') } }
  ])
];

@NgModule({
  imports: [RouterModule.forChild(routes), ShellModule],
  exports: [RouterModule],
  providers: []
})
export class AboutRoutingModule {}
