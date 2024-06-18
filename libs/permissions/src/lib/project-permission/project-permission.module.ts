import { ModuleWithProviders, NgModule } from '@angular/core';
import { RepositoryModule } from '@models4insight/repository';
import { HasProjectPermissionDirective } from './has-project-permission.directive';
import { ProjectPermissionDirective } from './project-permission.directive';
import { ProjectPermissionService } from './project-permission.service';

@NgModule({
  imports: [RepositoryModule],
  declarations: [ProjectPermissionDirective, HasProjectPermissionDirective],
  exports: [ProjectPermissionDirective, HasProjectPermissionDirective],
})
export class ProjectPermissionModule {
  static forRoot(): ModuleWithProviders<ProjectPermissionModule> {
    return {
      ngModule: ProjectPermissionModule,
      providers: [ProjectPermissionService],
    };
  }
}
