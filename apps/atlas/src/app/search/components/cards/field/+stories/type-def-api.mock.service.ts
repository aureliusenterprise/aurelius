import { Injectable } from '@angular/core';
import {
    AtlasTypesDef,
    GetOptions,
    TypeDefAPIService
} from '@models4insight/atlas/api';
import { Observable, of } from 'rxjs';
import TYPES_DEF from './types-def.json';

@Injectable()
export class MockTypeDefAPIService extends TypeDefAPIService {
  getTypeDefs({ forceUpdate }: GetOptions = {}): Observable<AtlasTypesDef> {
    return of(TYPES_DEF as unknown as AtlasTypesDef);
  }
}
