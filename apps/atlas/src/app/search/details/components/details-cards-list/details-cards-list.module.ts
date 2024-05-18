import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { SimpleSearchInputModule } from '@models4insight/components';
import { TooltipModule } from '@models4insight/directives';
import { DetailsCardModule } from '../../../components/cards/details-card.module';
import { FilterModule } from '../../../components/filter/filter.module';
import { InfiniteScrollContainerModule } from '../../../components/infinite-scroll-container/infinite-scroll-container.module';
import { SortingModule } from '../../../components/sorting/sorting.module';
import { DetailsCardsListComponent } from './details-cards-list.component';
import { ShowDescendantsControlDirective } from './show-descendants-control.directive';

@NgModule({
  imports: [
    CommonModule,
    DetailsCardModule,
    FilterModule,
    FontAwesomeModule,
    InfiniteScrollContainerModule,
    ReactiveFormsModule,
    SortingModule,
    SimpleSearchInputModule,
    TooltipModule,
  ],
  declarations: [DetailsCardsListComponent, ShowDescendantsControlDirective],
  exports: [DetailsCardsListComponent],
})
export class DetailsCardsListModule {}
