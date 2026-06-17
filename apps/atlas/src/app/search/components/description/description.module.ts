import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { MarkdownModule } from '@models4insight/components';
import { DescriptionComponent } from './description.component';
import { TranslateModule } from '@ngx-translate/core';

@NgModule({
    imports: [CommonModule, MarkdownModule, TranslateModule],
    declarations: [DescriptionComponent],
    exports: [DescriptionComponent],
})
export class DescriptionModule {}
