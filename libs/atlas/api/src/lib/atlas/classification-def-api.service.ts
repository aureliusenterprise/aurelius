import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ClassificationDef, GetOptions } from '../types';
import { AtlasApiClient } from './atlas-api-client.service';

@Injectable()
export class ClassificationDefAPIService {
  readonly BASE_PATH = 'atlas/v2/types/classificationdef';

  constructor(private readonly http: AtlasApiClient) {}

  getClassificationDefByName(
    name: string,
    { forceUpdate = false }: GetOptions = {}
  ): Observable<ClassificationDef> {
    const path = `${this.BASE_PATH}/name/${name}`;

    return this.http.cache(forceUpdate).get<ClassificationDef>(path);
  }
}
