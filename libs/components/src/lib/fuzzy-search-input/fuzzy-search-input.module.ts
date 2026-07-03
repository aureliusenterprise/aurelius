import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { TranslateModule } from '@ngx-translate/core';
import { ControlShellModule } from '../control-shell';
import { FuzzySearchInputComponent } from './fuzzy-search-input.component';

@NgModule({
    imports: [CommonModule, ControlShellModule, FormsModule, ReactiveFormsModule, TranslateModule],
    declarations: [FuzzySearchInputComponent],
    exports: [FuzzySearchInputComponent],
})
export class FuzzySearchInputModule {}
