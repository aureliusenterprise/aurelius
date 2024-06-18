import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AppSearchResult, GovQualitySearchObject } from '../elastic';
import { AtlasEntityWithEXTInformation } from '../types';
import { GovQualityApiClient } from './gov-quality-api-client.service';

export interface EntityValidationResult {
  readonly items: AppSearchResult<GovQualitySearchObject>[];
  readonly isNonCompliant: boolean;
}

export interface EntityValidationResponse {
  readonly [key: string]: EntityValidationResult;
}

@Injectable()
export class GovQualityApi {
  readonly PATH = 'validate_entity';

  constructor(private readonly http: GovQualityApiClient) {}

  validateEntity(
    entity: AtlasEntityWithEXTInformation
  ): Observable<EntityValidationResponse> {
    return this.http.post<EntityValidationResponse>(this.PATH, entity);
  }
}
