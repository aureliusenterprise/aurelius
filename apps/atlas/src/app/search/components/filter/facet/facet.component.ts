import { KeyValue } from '@angular/common';
import { Component, Input } from '@angular/core';
import {
  AppSearchDocument,
  AppSearchResultsFacetData,
} from '@models4insight/atlas/api';

@Component({
  selector: 'models4insight-facet',
  templateUrl: './facet.component.html',
  styleUrls: ['./facet.component.scss'],
})
export class FacetComponent<
  T extends AppSearchDocument = AppSearchDocument,
  K extends keyof T = any
> {
  constructor() {}

  @Input() facet: KeyValue<K, AppSearchResultsFacetData<T, T[K]>[]>;
  @Input() showMore = false;

  toggleShowMore() {
    this.showMore = !this.showMore;
  }
}
