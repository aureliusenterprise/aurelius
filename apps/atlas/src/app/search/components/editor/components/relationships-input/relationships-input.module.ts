import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import {
  ModalModule,
  SimpleSearchInputModule
} from '@models4insight/components';
import { TranslateModule } from '@ngx-translate/core';
import { DetailsCardModule } from '../../../cards/details-card.module';
import { FilterModule } from '../../../filter/filter.module';
import { TypeNameModule } from '../../../type-name/type-name.module';
import { RelationshipOptionModule } from './relationship-option/relationship-option.module';
import { RelationshipsFacetsComponent } from './relationships-facets/relationships-facets.component';
import { RelationshipsInputComponent } from './relationships-input.component';

@NgModule({
  imports: [
    CommonModule,
    FilterModule,
    FontAwesomeModule,
    ModalModule,
    SimpleSearchInputModule,
    ReactiveFormsModule,
    RelationshipOptionModule,
    TranslateModule.forChild(),
    TypeNameModule,
    DetailsCardModule,
  ],
  declarations: [RelationshipsInputComponent, RelationshipsFacetsComponent ],
  exports: [RelationshipsInputComponent],
})
export class RelationshipsInputModule {}
