import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { I18nService } from '@models4insight/i18n';
import { TranslateModule } from '@ngx-translate/core';
import { ControlShellModule } from '../control-shell';
import { FuzzySearchInputComponent } from './fuzzy-search-input.component';
import enUS from '../../translations/en-US.json';
import nlNL from '../../translations/nl-NL.json';

@NgModule({
    imports: [CommonModule, ControlShellModule, FormsModule, ReactiveFormsModule, TranslateModule],
    declarations: [FuzzySearchInputComponent],
    exports: [FuzzySearchInputComponent],
})
export class FuzzySearchInputModule {
    constructor(private readonly i18nService: I18nService) {
        this.i18nService.setTranslation('en-US', enUS);
        this.i18nService.setTranslation('nl-NL', nlNL);
    }
}
