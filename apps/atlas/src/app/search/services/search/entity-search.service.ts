import { Injectable } from '@angular/core';
import {
  AppSearchFacets,
  AppSearchFields,
  AtlasEntitySearchObject,
} from '@models4insight/atlas/api';
import { SearchService } from './search.service';

export interface EntitySearchObject {
  readonly breadcrumbguid: string[];
  readonly breadcrumbname: string[];
  readonly breadcrumbtype: string[];
  readonly definition: string;
  readonly derivedcollection: string[];
  readonly deriveddataattribute: string[];
  readonly deriveddatadomain: string[];
  readonly deriveddataentity: string[];
  readonly deriveddataset: string[];
  readonly derivedperson: string[];
  readonly derivedsystem: string[];
  readonly derivedfield: string[];
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
  readonly guid: string;
  readonly id: string;
  readonly name: string;
  readonly supertypenames: string[];
  readonly typename: string;
}

export const ENTITY_SEARCH_FIELDS: AppSearchFields<EntitySearchObject> = {
  typename: { raw: {} },
  breadcrumbguid: { raw: {} },
  breadcrumbname: { raw: {} },
  breadcrumbtype: { raw: {} },
  definition: { raw: {}, snippet: { size: 100, fallback: true } },
  deriveddataentity: {
    raw: {},
  },
  deriveddataset: { raw: {} },
  derivedsystem: { raw: {} },
  guid: { raw: {} },
  derivedperson: { raw: {} },
  id: { raw: {} },
  name: { raw: {} },
  derivedcollection: {
    raw: {},
  },
  deriveddatadomain: {
    raw: {},
  },
  deriveddataattribute: {
    raw: {},
  },
  derivedfield: {
    raw: {},
  },
  dqscore_overall: {
    raw: {},
  },
  dqscorecnt_overall: {
    raw: {},
  },
  dqscore_accuracy: {
    raw: {},
  },
  dqscorecnt_accuracy: {
    raw: {},
  },
  dqscore_completeness: {
    raw: {},
  },
  dqscorecnt_completeness: {
    raw: {},
  },
  dqscore_timeliness: {
    raw: {},
  },
  dqscorecnt_timeliness: {
    raw: {},
  },
  dqscore_uniqueness: {
    raw: {},
  },
  dqscorecnt_uniqueness: {
    raw: {},
  },
  dqscore_validity: {
    raw: {},
  },
  dqscorecnt_validity: {
    raw: {},
  },
  supertypenames: {
    raw: {},
  },
};

export const ENTITY_SEARCH_FACETS: AppSearchFacets<AtlasEntitySearchObject> = {
  supertypenames: { type: 'value', size: 100 },
  deriveddataentity: { type: 'value', size: 100 },
  deriveddataset: { type: 'value', size: 100 },
  derivedsystem: { type: 'value', size: 100 },
  derivedperson: { type: 'value', size: 100 },
  deriveddatadomain: { type: 'value', size: 100 },
  derivedcollection: { type: 'value', size: 100 },
  sourcetype: { type: 'value', size: 100 },
};

@Injectable()
export class EntitySearchService extends SearchService<
  AtlasEntitySearchObject,
  EntitySearchObject
> {
  constructor() {
    super({
      query: '',
      page: {
        current: 1,
        size: 5,
      },
      result_fields: ENTITY_SEARCH_FIELDS,
      facets: ENTITY_SEARCH_FACETS,
    });
  }
}
