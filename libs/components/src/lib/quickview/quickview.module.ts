import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { QuickviewComponent } from './quickview.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { I18nService } from '@models4insight/i18n';
import { TooltipModule } from '@models4insight/directives';
import { TranslateModule } from '@ngx-translate/core';
import enUS from '../../translations/en-US.json';
import nlNL from '../../translations/nl-NL.json';

@NgModule({
    imports: [CommonModule, FontAwesomeModule, TooltipModule, TranslateModule],
    declarations: [QuickviewComponent],
    exports: [QuickviewComponent],
})
export class QuickviewModule {
    constructor(private readonly i18nService: I18nService) {
        this.i18nService.setTranslation('en-US', enUS);
        this.i18nService.setTranslation('nl-NL', nlNL);
    }
}
