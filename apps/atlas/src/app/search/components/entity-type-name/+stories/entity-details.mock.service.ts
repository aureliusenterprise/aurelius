import { Injectable } from '@angular/core';
import { EntityDetailsService } from '../../../services/entity-details/entity-details.service';
import ENTITY_DETAILS from './entity-details.json';

@Injectable()
export class MockEntityDetailsService extends EntityDetailsService {
  constructor() {
    super(null, null);
    this.entityDetails = ENTITY_DETAILS;
  }
}
