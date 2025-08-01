import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { AccordionModule } from '@models4insight/components';
import { DetailsNavigationModule } from '../components/navigation/details-navigation.module';
import { PropertiesModule } from '../components/properties/properties.module';
import { DefaultDetailsComponent } from './default-details.component';

@NgModule({
  imports: [CommonModule, DetailsNavigationModule, PropertiesModule, AccordionModule],
  declarations: [DefaultDetailsComponent]
})
export class DefaultDetailsModule {}
