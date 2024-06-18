import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { MarkdownModule } from '../markdown.module';
import { MarkdownEditorComponent } from './markdown-editor.component';

@NgModule({
  imports: [CommonModule, ReactiveFormsModule, MarkdownModule],
  declarations: [MarkdownEditorComponent],
  exports: [MarkdownEditorComponent],
})
export class MarkdownEditorModule {}
