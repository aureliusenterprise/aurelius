import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { MarkdownModule as NgxMarkdownModule } from 'ngx-markdown';
import { MarkdownComponent } from './markdown.component';

@NgModule({
  imports: [CommonModule, NgxMarkdownModule.forRoot()],
  declarations: [MarkdownComponent],
  exports: [MarkdownComponent],
})
export class MarkdownModule {}
