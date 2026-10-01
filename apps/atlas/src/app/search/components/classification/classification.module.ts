import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { TooltipModule } from '@models4insight/directives';
import { TranslateModule } from '@ngx-translate/core';
import { ClassificationLabelModule } from '../classification-label';
import { ClassificationSourceModule } from './classification-source/classification-source.module';
import { ClassificationComponent } from './classification.component';

@NgModule({
  imports: [
    ClassificationLabelModule,
    CommonModule,
    ClassificationSourceModule,
    FontAwesomeModule,
    TooltipModule,
    TranslateModule
  ],
  declarations: [ClassificationComponent],
  exports: [ClassificationComponent]
})
export class ClassificationModule {}
