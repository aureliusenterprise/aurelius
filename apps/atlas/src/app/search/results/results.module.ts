import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { TranslateModule } from '@ngx-translate/core';
import { DetailsCardModule } from '../components/cards/details-card.module';
import { FilterModule } from '../components/filter/filter.module';
import { InfiniteScrollContainerModule } from '../components/infinite-scroll-container/infinite-scroll-container.module';
import { ResultsComponent } from './results.component';

@NgModule({
  declarations: [ResultsComponent],
  imports: [
    CommonModule,
    FilterModule,
    FontAwesomeModule,
    InfiniteScrollContainerModule,
    DetailsCardModule,
    TranslateModule.forChild(),
  ],
})
export class ResultsModule {}
