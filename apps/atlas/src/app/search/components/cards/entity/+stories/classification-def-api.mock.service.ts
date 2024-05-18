import { Injectable } from '@angular/core';
import {
  ClassificationDef,
  ClassificationDefAPIService,
} from '@models4insight/atlas/api';
import { GetOptions } from '@models4insight/repository';
import { EMPTY, Observable, of } from 'rxjs';
import CLASSIFICATION_DEFS_BY_NAME from './classfication-defs.json';

@Injectable()
export class MockClassficationDefAPIService extends ClassificationDefAPIService {
  getClassificationDefByName(
    name: string,
    { forceUpdate }: GetOptions = {}
  ): Observable<ClassificationDef> {
    if (!(name in CLASSIFICATION_DEFS_BY_NAME)) return EMPTY;

    return of(CLASSIFICATION_DEFS_BY_NAME[name]);
  }
}
