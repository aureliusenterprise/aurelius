import { Injectable } from '@angular/core';
import {
    AtlasEntityWithEXTInformation,
    EntityAPIService,
    GetOptions
} from '@models4insight/atlas/api';
import { Observable, of } from 'rxjs';
import ENTITY_DETAILS from './entity-details.json';

@Injectable()
export class MockEntityAPIService extends EntityAPIService {
  getEntityById(
    guid: string,
    { forceUpdate }: GetOptions = {}
  ): Observable<AtlasEntityWithEXTInformation> {
    return of(ENTITY_DETAILS as unknown as AtlasEntityWithEXTInformation);
  }
}
