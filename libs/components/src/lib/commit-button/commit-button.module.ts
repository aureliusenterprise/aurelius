import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ModalModule } from '../modal';
import { CommitButtonComponent } from './commit-button.component';
import { CommitOptionsModalComponent } from './commit-options-modal/commit-options-modal.component';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { TooltipModule } from '@models4insight/directives';
import { ConflictResolutionTemplateSelectModule } from '../conflict-resolution-template-select';

@NgModule({
  imports: [
    CommonModule,
    FontAwesomeModule,
    FormsModule,
    ReactiveFormsModule,
    ModalModule,
    TooltipModule,
    ConflictResolutionTemplateSelectModule,
  ],
  declarations: [CommitButtonComponent, CommitOptionsModalComponent],
  exports: [CommitButtonComponent],
})
export class CommitButtonModule {}
