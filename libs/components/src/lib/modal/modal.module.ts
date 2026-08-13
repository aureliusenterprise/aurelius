import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { HoldableModule } from '@models4insight/directives';
import { TranslateModule } from '@ngx-translate/core';
import { ModalComponent } from './modal.component';

@NgModule({
    imports: [CommonModule, HoldableModule, TranslateModule],
    declarations: [ModalComponent],
    exports: [ModalComponent],
})
export class ModalModule {}
