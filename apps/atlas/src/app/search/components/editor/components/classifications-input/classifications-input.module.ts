import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { TranslateModule } from '@ngx-translate/core';
import { ClassificationLabelModule } from '../../../classification-label';
import { ClassificationsInputComponent } from './classifications-input.component';

@NgModule({
  imports: [
    ClassificationLabelModule,
    CommonModule,
    FontAwesomeModule,
    ReactiveFormsModule,
    TranslateModule.forChild()
  ],
  declarations: [ClassificationsInputComponent],
  exports: [ClassificationsInputComponent]
})
export class ClassificationsInputModule {}
