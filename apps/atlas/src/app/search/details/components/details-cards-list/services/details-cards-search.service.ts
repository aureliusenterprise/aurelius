import { AppSearchDocument, AppSearchQuery } from '@models4insight/atlas/api';
import { isEqual } from 'lodash';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { SearchService } from '../../../../services/search/search.service';

export abstract class DetailsCardsSearchService<
  T extends AppSearchDocument,
  P extends Partial<T> = T
> extends SearchService<T, P> {
  readonly isFilterActive$: Observable<boolean>;

  protected defaultQueryObject: AppSearchQuery<T, P>;

  constructor(defaultQueryObject?: AppSearchQuery<T, P>) {
    super(defaultQueryObject);

    this.isFilterActive$ = this.queryObject$.pipe(
      map((queryObject) => !isEqual(queryObject, this.defaultQueryObject))
    );
  }

  reset() {
    this.queryObject = this.defaultQueryObject;
  }

  protected updateDefaultQueryObject(queryObject: AppSearchQuery<T, P>) {
    this.defaultQueryObject = queryObject;
    this.queryObject = queryObject;
  }
}
