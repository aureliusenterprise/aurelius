import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ProjectDescriptionSettingsRoutingModule } from './project-description-routing.module';
import { ProjectDescriptionSettingsComponent } from './project-description.component';
import { DescriptionInputModule } from '@models4insight/components';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    DescriptionInputModule,
    ProjectDescriptionSettingsRoutingModule
  ],
  declarations: [ProjectDescriptionSettingsComponent]
})
export class ProjectDescriptionSettingsModule {}
