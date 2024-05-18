import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { TooltipModule } from '@models4insight/directives';
import { TermComponent } from './term.component';

@NgModule({
  imports: [CommonModule, TooltipModule],
  declarations: [TermComponent],
  exports: [TermComponent]
})
export class TermModule {}
