import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RuleEditorComponent } from './rule-editor.component';
import { RuleEditorService } from './rule-editor.service';
import { HoldableModule } from '@models4insight/directives';

@NgModule({
  imports: [CommonModule, FormsModule, HoldableModule, ReactiveFormsModule],
  declarations: [RuleEditorComponent],
  providers: [RuleEditorService],
  exports: [RuleEditorComponent]
})
export class RuleEditorModule {}
