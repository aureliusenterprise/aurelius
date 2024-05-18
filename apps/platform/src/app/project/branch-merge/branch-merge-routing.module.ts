import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { BranchMergeComponent } from './branch-merge.component';
import { BranchMergeGuard } from './branch-merge.guard';

const routes: Routes = [
  {
    path: '',
    component: BranchMergeComponent,
    data: {
      title: extract('Move branches')
    },
    canActivate: [BranchMergeGuard]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: []
})
export class BranchMergeRoutingModule {}
