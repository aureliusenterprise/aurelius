import { Injectable } from '@angular/core';
import { AppSearchClient } from '../app-search-client.service';
import { AppSearchDocument, AppSearchService } from '../app-search.service';

export interface DataQualitySearchObject extends AppSearchDocument {
  readonly businessruleid: number;
  readonly datadomainname: string;
  readonly dataqualityruledescription: string;
  readonly dataqualityruledimension: string;
  readonly dqscore: number;
  readonly expression: string;
  readonly fieldguid: string;
  readonly fieldqualifiedname: string;
  readonly guid: string;
  readonly id: string;
  readonly name: string;
  readonly qualifiedname: string;
  readonly qualityguid: string;
  readonly qualityqualifiedname: string;
}

@Injectable()
export class DataQualitySearchService<
  P extends Partial<DataQualitySearchObject> = DataQualitySearchObject
> extends AppSearchService<DataQualitySearchObject, P> {
  constructor(http: AppSearchClient) {
    super(http, 'data_quality');
  }
}
