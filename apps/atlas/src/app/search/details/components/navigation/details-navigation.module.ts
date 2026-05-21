import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgxPageScrollCoreModule } from 'ngx-page-scroll-core';
import { DetailsNavigationItemDirective, DetailsNavigationItemService } from './details-navigation-item.directive';
import { DetailsNavigationComponent } from './details-navigation.component';
import { TranslateModule } from '@ngx-translate/core';

@NgModule({
    imports: [CommonModule, FontAwesomeModule, NgxPageScrollCoreModule, TranslateModule],
    declarations: [DetailsNavigationComponent, DetailsNavigationItemDirective],
    providers: [DetailsNavigationItemService],
    exports: [DetailsNavigationComponent, DetailsNavigationItemDirective],
})
export class DetailsNavigationModule {}
