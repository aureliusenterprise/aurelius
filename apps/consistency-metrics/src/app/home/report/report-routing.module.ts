import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ReportComponent } from './report.component';
import { ReportResolver } from './report.resolver';

const routes: Routes = [
  {
    path: '',
    component: ReportComponent,
    data: { title: 'Report' },
    resolve: { report: ReportResolver },
    runGuardsAndResolvers: 'paramsOrQueryParamsChange'
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ReportRoutingModule {}
