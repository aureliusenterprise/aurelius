import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { HoldableModule } from '@models4insight/directives';
import { TranslateModule } from '@ngx-translate/core';
import { ProjectSettingsRoutingModule } from './project-settings-routing.module';
import { ProjectSettingsComponent } from './project-settings.component';
import { ProjectSettingsGuard } from './project-settings.guard';
import { ProjectPermissionModule } from '@models4insight/permissions';

@NgModule({
  imports: [
    CommonModule,
    HoldableModule,
    TranslateModule,
    ProjectSettingsRoutingModule,
    ProjectPermissionModule
  ],
  declarations: [ProjectSettingsComponent],
  providers: [ProjectSettingsGuard]
})
export class ProjectSettingsModule {}
