import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { MarkdownModule } from '@models4insight/components';
import { DescriptionComponent } from './description.component';

@NgModule({
  imports: [CommonModule, MarkdownModule],
  declarations: [DescriptionComponent],
  exports: [DescriptionComponent],
})
export class DescriptionModule {}
