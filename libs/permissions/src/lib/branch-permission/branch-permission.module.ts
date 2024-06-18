import { ModuleWithProviders, NgModule } from '@angular/core';
import { RepositoryModule } from '@models4insight/repository';
import { ProjectPermissionModule } from '../project-permission';
import { BranchPermissionDirective } from './branch-permission.directive';
import { BranchPermissionService } from './branch-permission.service';
import { HasBranchPermissionDirective } from './has-branch-permission.directive';

@NgModule({
  imports: [RepositoryModule, ProjectPermissionModule],
  declarations: [BranchPermissionDirective, HasBranchPermissionDirective],
  exports: [BranchPermissionDirective, HasBranchPermissionDirective],
})
export class BranchPermissionModule {
  static forRoot(): ModuleWithProviders<BranchPermissionModule> {
    return {
      ngModule: BranchPermissionModule,
      providers: [BranchPermissionService],
    };
  }
}
