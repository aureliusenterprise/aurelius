import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { extract } from '@models4insight/i18n';
import { UserGroupsSettingsComponent } from './user-groups.component';

const routes: Routes = [
  {
    path: '',
    component: UserGroupsSettingsComponent,
    data: {
      title: extract('User Groups')
    }
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule],
  providers: []
})
export class UserGroupsSettingsRoutingModule {}
