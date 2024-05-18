import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { SortableTableShellModule } from '@models4insight/components';
import { HoldableModule } from '@models4insight/directives';
import { ApiModule } from '../../api/api.module';
import { SuggestionsRoutingModule } from './suggestions-routing.module';
import { SuggestionsComponent } from './suggestions.component';
import { SuggestionsService } from './suggestions.service';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ValidationResultModule } from '../validation-result/validation-result.module';
import { Modelview2Module} from '@models4insight/modelview2'
@NgModule({
  imports: [
    ApiModule,
    CommonModule,
    SuggestionsRoutingModule,
    FormsModule,
    HoldableModule,
    ReactiveFormsModule,
    Modelview2Module,
    SortableTableShellModule,
    FontAwesomeModule,
    ValidationResultModule
  ],
  declarations: [SuggestionsComponent],
  providers: [SuggestionsService]
})
export class SuggestionsModule {}
