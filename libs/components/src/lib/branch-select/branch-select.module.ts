import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { CreateBranchModalModule } from '../create-branch-modal';
import { SelectModule } from '../select';
import { BranchSelectComponent } from './branch-select.component';

@NgModule({
  imports: [
    CommonModule,
    FontAwesomeModule,
    FormsModule,
    ReactiveFormsModule,
    CreateBranchModalModule,
    SelectModule,
  ],
  declarations: [BranchSelectComponent],
  exports: [BranchSelectComponent],
})
export class BranchSelectModule {}
