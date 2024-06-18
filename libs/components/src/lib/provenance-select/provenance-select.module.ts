import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { SelectModule } from '../select';
import { ProvenanceSelectComponent } from './provenance-select.component';

@NgModule({
  imports: [CommonModule, FormsModule, ReactiveFormsModule, SelectModule],
  declarations: [ProvenanceSelectComponent],
  exports: [ProvenanceSelectComponent],
})
export class ProvenanceSelectModule {}
