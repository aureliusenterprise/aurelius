import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { Shell, ShellModule } from '@models4insight/shell';
import { HomeComponent } from './home.component';

const childRoutes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'generate'
  },
  {
    path: 'generate',
    loadChildren: () =>
      import('./generate-report/generate-report.module').then(
        m => m.GenerateReportModule
      )
  },
  {
    path: 'report',
    loadChildren: () =>
      import('./report/report.module').then(m => m.ReportModule)
  },
  {
    path: '**',
    pathMatch: 'full',
    redirectTo: 'generate'
  }
];

const routes: Routes = [
  Shell.childRoutes([
    {
      path: '',
      component: HomeComponent,
      data: { title: 'Home' },
      children: childRoutes
    }
  ])
];

@NgModule({
  imports: [RouterModule.forChild(routes), ShellModule],
  exports: [RouterModule]
})
export class HomeRoutingModule {}
