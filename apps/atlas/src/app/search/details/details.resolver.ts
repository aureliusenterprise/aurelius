import { Injectable } from '@angular/core';
import {
  ActivatedRouteSnapshot,
  Resolve,
  RouterStateSnapshot
} from '@angular/router';
import {
  AtlasEntitySearchObject,
  EntityAPIService
} from '@models4insight/atlas/api';
import { ElementSearchService } from '../services/element-search/element-search.service';
import { EntityDetailsService } from '../services/entity-details/entity-details.service';

@Injectable()
export class DetailsResolver implements Resolve<string> {
  constructor(
    private readonly entityApiService: EntityAPIService,

  ) {}

  resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot) {
    const entityId = route.paramMap.get('id');

    this.entityApiService.clearCacheById(entityId);

    return entityId;
  }
}
