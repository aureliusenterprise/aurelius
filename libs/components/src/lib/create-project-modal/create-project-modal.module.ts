import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { DescriptionInputModule } from '../description-input';
import { ModalModule } from '../modal';
import { CreateProjectModalComponent } from './create-project-modal.component';

@NgModule({
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    DescriptionInputModule,
    ModalModule,
  ],
  declarations: [CreateProjectModalComponent],
  exports: [CreateProjectModalComponent],
})
export class CreateProjectModalModule {}
