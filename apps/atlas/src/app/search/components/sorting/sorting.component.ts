import { Component, Input, OnDestroy, OnInit } from '@angular/core';
import { FormControl, FormGroup, UntypedFormGroup } from '@angular/forms';
import {
  faSort,
  faSortAlphaDown,
  faSortAlphaUp
} from '@fortawesome/free-solid-svg-icons';
import {
  AppSearchDocument,
  AppSearchSort,
  AppSearchSortKey
} from '@models4insight/atlas/api';
import { untilDestroyed } from '@models4insight/utils';
import { SearchService } from '../../services/search/search.service';

export interface SortForm<T extends AppSearchDocument> {
  readonly sortBy: FormControl<AppSearchSortKey<T>>;
  readonly sortDirection: FormControl<boolean>;
}

export interface SortFormValue<T extends AppSearchDocument> {
  readonly sortBy?: AppSearchSortKey<T>;
  readonly sortDirection?: boolean;
}

@Component({
  selector: 'models4insight-sorting',
  templateUrl: './sorting.component.html',
  styleUrls: ['./sorting.component.scss'],
})
export class SortingComponent<T extends AppSearchDocument = AppSearchDocument>
  implements OnInit, OnDestroy
{
  readonly sortingIcon = faSort;
  readonly faSortUp = faSortAlphaUp;
  readonly faSortDown = faSortAlphaDown;

  sortBy: FormControl<AppSearchSortKey<T>>;
  sortDirection: FormControl<boolean>;
  sortingForm: FormGroup<SortForm<T>>;

  @Input() sortingOptions: string[] = [];

  constructor(private readonly searchService: SearchService<T>) {}

  ngOnInit() {
    this.sortBy = new FormControl<AppSearchSortKey<T>>('_score');
    this.sortDirection = new FormControl<boolean>(false);

    this.sortingForm = new UntypedFormGroup({
      sortBy: this.sortBy,
      sortDirection: this.sortDirection,
    });

    this.sortingForm.valueChanges
      .pipe(untilDestroyed(this))
      .subscribe((formValue) => this.updateSorting(formValue));

    this.searchService
      .select(['queryObject', 'sort'])
      .pipe(untilDestroyed(this))
      .subscribe((sorting) => this.applySorting(sorting));
  }

  ngOnDestroy() {}

  toggleSortDirection() {
    this.sortDirection.setValue(!this.sortDirection.value);
  }

  private applySorting(sorting: AppSearchSort<T>) {
    const entries = Object.entries(sorting);

    if (entries.length === 0) return;

    const [sortBy, sortDirection] = entries[0];

    this.sortingForm.patchValue({
      sortBy: sortBy as AppSearchSortKey<T>,
      sortDirection: sortDirection === 'asc',
    });
  }

  private updateSorting({ sortBy, sortDirection }: SortFormValue<T>) {
    const sorting = {
      [sortBy]: sortDirection ? 'asc' : 'desc',
    } as AppSearchSort<T>;
    this.searchService.sort = sorting;
  }
}
