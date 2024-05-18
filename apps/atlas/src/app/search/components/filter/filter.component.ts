import { Component } from '@angular/core';
import { AppSearchDocument } from '@models4insight/atlas/api';
import { Observable } from 'rxjs';
import {
  FilterService,
  SearchFilters
} from '../../services/filter/filter.service';

@Component({
  selector: 'models4insight-filter',
  templateUrl: './filter.component.html',
  styleUrls: ['./filter.component.scss'],
})
export class FilterComponent<T extends AppSearchDocument = AppSearchDocument> {
  readonly filters$: Observable<SearchFilters<T>>;

  constructor(private readonly filterService: FilterService<T>) {
    this.filters$ = this.filterService.filters$;
  }

  preserveKeyOrder() {
    return 0;
  }
}
