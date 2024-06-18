import { Injectable } from '@angular/core';
import { BasicStore } from '@models4insight/redux';
import { combineLatest } from 'rxjs';
import { map, switchMap } from 'rxjs/operators';
import { ModelExplorerService } from '../../../model-explorer.service';
import { ModelRelation } from '../../../parsers';

export interface ModelBrowserRelationshipRowStoreContext {
  relationship: ModelRelation;
}

@Injectable()
export class ModelBrowserRelationshipRowService extends BasicStore<ModelBrowserRelationshipRowStoreContext> {
  constructor(private readonly modelExplorerService: ModelExplorerService) {
    super();
    this.init();
  }

  private init() {}

  set relationship(relationship: ModelRelation) {
    this.update({
      description: 'New relationship details available',
      payload: { relationship },
    });
  }

  get displayName() {
    return combineLatest([
      this.select(['relationship', 'displayName'], { includeFalsy: true }),
      this.select(['relationship', 'name'], { includeFalsy: true }),
    ]).pipe(map(([displayName, name]) => name || displayName));
  }

  get source() {
    return this.select(['relationship', 'source']).pipe(
      switchMap((id) => this.modelExplorerService.select(['entitiesById', id]))
    );
  }

  get target() {
    return this.select(['relationship', 'target']).pipe(
      switchMap((id) => this.modelExplorerService.select(['entitiesById', id]))
    );
  }

  get type() {
    return combineLatest([
      this.select(['relationship', 'humanReadableType'], {
        includeFalsy: true,
      }),
      this.select(['relationship', 'type']),
    ]).pipe(map(([humanReadableType, type]) => humanReadableType ?? type));
  }
}
