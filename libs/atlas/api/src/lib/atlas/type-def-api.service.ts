import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AtlasTypesDef, GetOptions } from '../types';
import { AtlasApiClient } from './atlas-api-client.service';

@Injectable()
export class TypeDefAPIService {
  readonly BASE_PATH = 'atlas/v2/types';

  constructor(private readonly http: AtlasApiClient) {}

  getTypeDefs({
    forceUpdate = false,
  }: GetOptions = {}): Observable<AtlasTypesDef> {
    const path = `${this.BASE_PATH}/typedefs`;

    return this.http.cache(forceUpdate).get<AtlasTypesDef>(path);
  }
}
