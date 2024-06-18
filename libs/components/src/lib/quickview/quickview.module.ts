import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { QuickviewComponent } from './quickview.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { TooltipModule } from '@models4insight/directives';

@NgModule({
  imports: [CommonModule, FontAwesomeModule, TooltipModule],
  declarations: [QuickviewComponent],
  exports: [QuickviewComponent],
})
export class QuickviewModule {}
