import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { DataQualityListModule } from '../../components/data-quality-list/data-quality-list.module';
import { DescriptionModule } from '../../components/description/description.module';
import { PeopleModule } from '../../components/people/people.module';
import { DetailsCardsListModule } from '../components/details-cards-list/details-cards-list.module';
import { DetailsNavigationModule } from '../components/navigation/details-navigation.module';
import { AttributeDetailsComponent } from './attribute-details.component';
import { FieldsCardsComponent } from './fields-cards/fields-cards.component';
import { PropertiesModule } from '../components/properties/properties.module';
import { GovernanceQualityCardsModule } from '../components/governance-quality-cards/governance-quality-cards.module';
import { AccordionModule } from '@models4insight/components';
import { TranslateModule } from '@ngx-translate/core';

@NgModule({
    imports: [
        CommonModule,
        DataQualityListModule,
        DescriptionModule,
        DetailsCardsListModule,
        DetailsNavigationModule,
        GovernanceQualityCardsModule,
        PeopleModule,
        PropertiesModule,
        AccordionModule,
        TranslateModule,
    ],
    declarations: [FieldsCardsComponent, AttributeDetailsComponent],
})
export class AttributeDetailsModule {}
