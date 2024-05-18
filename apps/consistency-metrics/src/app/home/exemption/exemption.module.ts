import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { BranchSelectModule, ModalModule, ProjectSelectModule, ProvenanceSelectModule, DescriptionInputModule } from '@models4insight/components';
import { ExemptionComponent } from './exemption.component';

@NgModule({
  imports: [
    ModalModule,
    FormsModule,
    ReactiveFormsModule,
    ProjectSelectModule,
    BranchSelectModule,
    ProvenanceSelectModule,
    DescriptionInputModule
  ],
  declarations: [ExemptionComponent],
  exports: [ExemptionComponent]
})
export class ExemptionModule {}
