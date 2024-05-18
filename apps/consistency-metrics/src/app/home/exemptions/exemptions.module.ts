import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { BranchSelectModule, ProjectSelectModule, ProvenanceSelectModule, SortableTableModule } from '@models4insight/components';
import { ExemptionsRoutingModule } from './exemptions-routing.module';
import { ExemptionsComponent } from './exemptions.component';

@NgModule({
  imports: [
    BranchSelectModule,
    CommonModule,
    FontAwesomeModule,
    FormsModule,
    ProjectSelectModule,
    ProvenanceSelectModule,
    ReactiveFormsModule,
    ExemptionsRoutingModule,
    SortableTableModule
  ],
  declarations: [ExemptionsComponent]
})
export class ExemptionsModule {}
