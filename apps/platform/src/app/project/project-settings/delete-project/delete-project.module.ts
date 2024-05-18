import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { HoldableModule } from '@models4insight/directives';
import { DeleteProjectSettingsRoutingModule } from './delete-project-routing.module';
import { DeleteProjectSettingsComponent } from './delete-project.component';
import { DeleteProjectSettingsGuard } from './delete-project.guard';

@NgModule({
  imports: [CommonModule, HoldableModule, DeleteProjectSettingsRoutingModule],
  declarations: [DeleteProjectSettingsComponent],
  providers: [DeleteProjectSettingsGuard]
})
export class DeleteProjectSettingsModule {}
