import { Injectable } from '@angular/core';
import { HttpCacheService } from '@models4insight/http';
import { Observable } from 'rxjs';
import {
  AtlasEntityWithEXTInformation,
  EntityMutationResponse,
  GetOptions,
} from '../types';
import { AtlasApiClient } from './atlas-api-client.service';

@Injectable()
export class EntityAPIService {
  readonly BASE_PATH = 'atlas/v2/entity';

  constructor(
    private readonly http: AtlasApiClient,
    private readonly cache: HttpCacheService
  ) {}

  clearCache() {
    this.cache.clearCache(`${this.BASE_PATH}/guid`);
  }

  clearCacheById(guid: string) {
    this.cache.clearCache(`${this.BASE_PATH}/guid/${guid}`);
  }

  getEntityById(
    guid: string,
    { forceUpdate = false }: GetOptions = {}
  ): Observable<AtlasEntityWithEXTInformation> {
    const path = `${this.BASE_PATH}/guid/${guid}`;

    return this.http
      .cache(forceUpdate)
      .get<AtlasEntityWithEXTInformation>(path);
  }

  saveEntity(
    entity: AtlasEntityWithEXTInformation
  ): Observable<EntityMutationResponse> {
    return this.http.post<EntityMutationResponse>(this.BASE_PATH, entity);
  }
}
