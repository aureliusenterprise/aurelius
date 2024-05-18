import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { TooltipModule } from '@models4insight/directives';
import { TranslateModule } from '@ngx-translate/core';
import { EntityTypeNameModule } from '../entity-type-name/entity-type-name.module';
import { InfiniteScrollContainerModule } from '../infinite-scroll-container/infinite-scroll-container.module';
import { AttributeDetailsCardModule } from './attribute/attribute-details-card.module';
import { CollectionDetailsCardModule } from './collection/collection-details-card.module';
import { GovernanceQualityListComponent } from './components/governance-quality-list/governance-quality-list.component';
import { DataQualityCardModule } from './data-quality/data-quality-card.module';
import { DatasetDetailsCardModule } from './dataset/dataset-details-card.module';
import { DetailsCardComponent } from './details-card.component';
import { DomainDetailsCardModule } from './domain/domain-details-card.module';
import { EntityDetailsCardModule } from './entity/entity-details-card.module';
import { FieldDetailsCardModule } from './field/field-details-card.module';
import { GovernanceQualityCardModule } from './gov-quality/governance-quality-card.module';
import { SystemDetailsCardModule } from './system/system-details-card.module';

@NgModule({
  imports: [
    CommonModule,
    FontAwesomeModule,
    TranslateModule.forChild(),
    AttributeDetailsCardModule,
    CollectionDetailsCardModule,
    DataQualityCardModule,
    DatasetDetailsCardModule,
    DomainDetailsCardModule,
    EntityDetailsCardModule,
    FieldDetailsCardModule,
    GovernanceQualityCardModule,
    InfiniteScrollContainerModule,
    SystemDetailsCardModule,
    TooltipModule,
    EntityTypeNameModule,
  ],
  declarations: [DetailsCardComponent, GovernanceQualityListComponent],
  exports: [DetailsCardComponent],
})
export class DetailsCardModule {}
