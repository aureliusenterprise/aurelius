import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { BranchSelectModule } from '../branch-select';
import { ModalModule } from '../modal';
import { ProvenanceSelectModule } from '../provenance-select';
import { CompareModalComponent } from './compare-modal.component';

@NgModule({
  declarations: [CompareModalComponent],
  imports: [
    CommonModule,
    BranchSelectModule,
    ModalModule,
    ProvenanceSelectModule,
  ],
  exports: [CompareModalComponent],
})
export class CompareModalModule {}
