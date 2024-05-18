import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { CreateProjectModalModule, SimpleSearchInputModule, SortableTableModule, FuzzySearchInputModule } from '@models4insight/components';
import { TranslateModule } from '@ngx-translate/core';
import { ProjectsRoutingModule } from './projects-routing.module';
import { ProjectsComponent } from './projects.component';

@NgModule({
  imports: [
    CommonModule,
    FontAwesomeModule,
    TranslateModule,
    ProjectsRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    CreateProjectModalModule,
    FuzzySearchInputModule,
    SortableTableModule
  ],
  declarations: [ProjectsComponent]
})
export class ProjectsModule {}
