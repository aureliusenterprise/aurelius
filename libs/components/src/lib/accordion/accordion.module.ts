import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { AccordionComponent } from './accordion.component';

@NgModule({
    imports: [CommonModule, FontAwesomeModule],
    declarations: [AccordionComponent],
    exports: [AccordionComponent],
})
export class AccordionModule { }
