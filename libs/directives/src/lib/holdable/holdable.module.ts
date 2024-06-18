import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { I18nService } from '@models4insight/i18n';
import { TranslateModule } from '@ngx-translate/core';
import { HoldableDirective } from './holdable.directive';
import enUS from './translations/en-US.json';

@NgModule({
  imports: [CommonModule, TranslateModule.forChild()],
  declarations: [HoldableDirective],
  exports: [HoldableDirective],
})
export class HoldableModule {
  constructor(private i18nService: I18nService) {
    this.i18nService.setTranslation('en-US', enUS);
  }
}
