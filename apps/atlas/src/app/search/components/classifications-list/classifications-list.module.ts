import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { ClassificationModule } from '../classification/classification.module';
import { ClassificationsListComponent } from './classifications-list.component';

@NgModule({
  imports: [CommonModule, ClassificationModule],
  declarations: [ClassificationsListComponent],
  exports: [ClassificationsListComponent]
})
export class ClassificationsListModule {}
