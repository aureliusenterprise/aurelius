import { Injectable } from '@angular/core';
import { AppSearchClient } from '../app-search-client.service';
import { AppSearchDocument, AppSearchService } from '../app-search.service';

export interface AtlasEntitySearchObject extends AppSearchDocument {
  readonly breadcrumbguid: string[];
  readonly breadcrumbname: string[];
  readonly breadcrumbtype: string[];
  readonly classificationstext: string[];
  readonly definition: string;
  readonly derivedcollection: string[];
  readonly derivedcollectionguid: string[];
  readonly deriveddataattribute: string[];
  readonly deriveddataattributeguid: string[];
  readonly deriveddatadomain: string[];
  readonly deriveddatadomainguid: string[];
  readonly deriveddataentity: string[];
  readonly deriveddataentityguid: string[];
  readonly deriveddataownerguid: string[];
  readonly deriveddatastewardguid: string[];
  readonly deriveddataset: string[];
  readonly deriveddatasetguid: string[];
  readonly derivedperson: string[];
  readonly derivedpersonguid: string[];
  readonly derivedsystem: string[];
  readonly derivedsystemguid: string[];
  readonly derivedfield: string[];
  readonly derivedfieldguid: string[];
  readonly dqscore_accuracy: number;
  readonly dqscore_completeness: number;
  readonly dqscore_overall: number;
  readonly dqscore_timeliness: number;
  readonly dqscore_uniqueness: number;
  readonly dqscore_validity: number;
  readonly dqscorecnt_accuracy: number;
  readonly dqscorecnt_completeness: number;
  readonly dqscorecnt_overall: number;
  readonly dqscorecnt_timeliness: number;
  readonly dqscorecnt_uniqueness: number;
  readonly dqscorecnt_validity: number;
  readonly dqscoresum_accuracy: number;
  readonly dqscoresum_completeness: number;
  readonly dqscoresum_overall: number;
  readonly dqscoresum_timeliness: number;
  readonly dqscoresum_uniqueness: number;
  readonly dqscoresum_validity: number;
  readonly email: string;
  readonly guid: string;
  readonly id: string;
  readonly m4isourcetype: string[];
  readonly name: string;
  readonly parentguid: string;
  readonly qualifiedname: string;
  readonly qualityguid_accuracy: string[];
  readonly qualityguid_completeness: string[];
  readonly qualityguid_timeliness: string[];
  readonly qualityguid_uniqueness: string[];
  readonly qualityguid_validity: string[];
  readonly referenceablequalifiedname: string;
  readonly sourcetype: string;
  readonly supertypenames: string[];
  readonly typename: string;
}

@Injectable()
export class AtlasEntitySearchService<
  P extends Partial<AtlasEntitySearchObject> = AtlasEntitySearchObject
> extends AppSearchService<AtlasEntitySearchObject, P> {
  constructor(http: AppSearchClient) {
    super(http, 'elastic');
  }
}
