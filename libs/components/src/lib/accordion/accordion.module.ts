import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { TranslateModule } from '@ngx-translate/core';
import { AccordionComponent } from './accordion.component';

@NgModule({
    imports: [CommonModule, FontAwesomeModule, TranslateModule],
    declarations: [AccordionComponent],
    exports: [AccordionComponent],
})
export class AccordionModule {}
