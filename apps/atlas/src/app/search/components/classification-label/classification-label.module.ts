import { NgModule } from '@angular/core';
import { ClassificationLabelPipe } from './classification-label.pipe';

@NgModule({
    declarations: [ClassificationLabelPipe],
    exports: [ClassificationLabelPipe],
})
export class ClassificationLabelModule {}
