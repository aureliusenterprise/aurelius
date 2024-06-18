import { Injectable } from '@angular/core';
import { AppSearchClient } from '../app-search-client.service';
import { AppSearchDocument, AppSearchService } from '../app-search.service';

export interface GovQualitySearchObject extends AppSearchDocument {
  readonly business_rule_id: number;
  readonly compliant: string;
  readonly dataqualityruledescription: string;
  readonly dataqualityruledimension: string;
  readonly dataqualitytype: string;
  readonly dataqualityruletypename: string;
  readonly doc_guid: string;
  readonly entity_guid: string;
  readonly expression: string;
  readonly guid: string;
  readonly id: string;
  readonly name: string;
  readonly qualifiedname: string;
  readonly qualityqualifiedname: string;
  readonly result: string;
  readonly result_id: string;
  readonly usedattributes: string[];
}

@Injectable()
export class GovernanceQualitySearchService<
  P extends Partial<GovQualitySearchObject> = GovQualitySearchObject
> extends AppSearchService<GovQualitySearchObject, P> {
  constructor(http: AppSearchClient) {
    super(http, 'gov_quality');
  }
}
