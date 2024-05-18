import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { Shell, ShellModule } from '@models4insight/shell';
import { AnalyticsComponent } from './analytics/analytics.component';
import { HomeComponent } from './home.component';
import { InsightsComponent } from './insights/insights.component';
import { ModelingComponent } from './modeling/modeling.component';
import { MonitoringComponent } from './monitoring/monitoring.component';
import { WelcomeComponent } from './welcome/welcome.component';

const childRoutes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'welcome'
  },
  {
    path: 'welcome',
    component: WelcomeComponent
  },
  {
    path: 'modeling',
    component: ModelingComponent
  },
  {
    path: 'insights',
    component: InsightsComponent
  },
  {
    path: 'monitoring',
    component: MonitoringComponent
  },
  {
    path: 'analytics',
    component: AnalyticsComponent
  },
  {
    path: '**',
    pathMatch: 'full',
    redirectTo: 'welcome'
  }
];

const routes: Routes = [
  Shell.childRoutes([
    {
      path: '',
      component: HomeComponent,
      data: { title: extract('Home') },
      children: childRoutes
    }
  ])
];

@NgModule({
  imports: [RouterModule.forChild(routes), ShellModule],
  exports: [RouterModule]
})
export class HomeRoutingModule {}
