import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, Resolve, RouterStateSnapshot } from '@angular/router';
import { clearEntityByIdCache } from '@models4insight/atlas/api';
import { EntityDetailsService } from '../services/entity-details/entity-details.service';

@Injectable()
export class EditEntityResolver implements Resolve<string> {
  constructor(
    private readonly entityDetailsService: EntityDetailsService,

  ) {}

  resolve(route: ActivatedRouteSnapshot) {
    const entityId = route.paramMap.get('id');

    // Ensures that the latest version of the entity will be shown on the page
    clearEntityByIdCache(entityId);

    this.entityDetailsService.entityId = entityId;

    return entityId;
  }
}
