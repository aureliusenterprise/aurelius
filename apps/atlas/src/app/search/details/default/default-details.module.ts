import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { AccordionModule } from '@models4insight/components';
import { DetailsNavigationModule } from '../components/navigation/details-navigation.module';
import { PropertiesModule } from '../components/properties/properties.module';
import { DefaultDetailsComponent } from './default-details.component';
import { DescriptionModule } from '../../components/description/description.module';
import { TranslateModule } from '@ngx-translate/core';

@NgModule({
    imports: [
        CommonModule,
        DetailsNavigationModule,
        DescriptionModule,
        PropertiesModule,
        AccordionModule,
        TranslateModule,
    ],
    declarations: [DefaultDetailsComponent],
})
export class DefaultDetailsModule {}
