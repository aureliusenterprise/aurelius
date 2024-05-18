import { Component } from '@angular/core';
import { AppSearchDocument } from '@models4insight/atlas/api';
import { Observable } from 'rxjs';
import { AppSearchResultsService } from '../../services/app-search-results/app-search-results.service';

@Component({
  selector: 'models4insight-infinite-scroll-container',
  templateUrl: 'infinite-scroll-container.component.html',
  styleUrls: ['infinite-scroll-container.component.scss'],
})
export class InfiniteScrollContainerComponent<
  T extends AppSearchDocument,
  P extends Partial<T> = T
> {
  readonly allResultsLoaded$: Observable<boolean>;
  readonly isLoadingPage$: Observable<boolean>;

  constructor(
    private readonly searchResultsService: AppSearchResultsService<T, P>
  ) {
    this.allResultsLoaded$ = this.searchResultsService.allResultsLoaded$;
    this.isLoadingPage$ = this.searchResultsService.isLoadingPage$;
  }

  nextPage() {
    this.searchResultsService.nextPage();
  }
}
