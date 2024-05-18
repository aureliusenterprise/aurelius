import { Injectable } from '@angular/core';
import {
    AppSearchQuery,
    AppSearchResults,
    GovernanceQualitySearchService,
    GovQualitySearchObject
} from '@models4insight/atlas/api';
import { Observable, of } from 'rxjs';
import GOV_QUALITY from './gov-quality.json';

@Injectable()
export class MockGovQualityApiService extends GovernanceQualitySearchService {
  search<P extends Partial<GovQualitySearchObject> = GovQualitySearchObject>(
    queryObject: AppSearchQuery<GovQualitySearchObject, P>
  ): Observable<AppSearchResults<P>> {
    return of(GOV_QUALITY as unknown as AppSearchResults<P>);
  }
}
