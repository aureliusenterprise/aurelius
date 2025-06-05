import { Injectable } from '@angular/core';
import {
  AtlasEntityWithEXTInformation,
  Classification,
  EntityAPIService,
  getEntityById,
  removeEntityClassification,
  saveEntityClassification
} from '@models4insight/atlas/api';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { Subject } from 'rxjs';
import { exhaustMap } from 'rxjs/operators';
import { EntityDetailsService } from '../entity-details/entity-details.service';

export interface EntityUpdateStoreContext {
  readonly isUpdatingEntity?: boolean;
}

@Injectable()
export class EntityUpdateService extends BasicStore<EntityUpdateStoreContext> {
  private readonly entityUpdated$ = new Subject<string>();
  private readonly update$ = new Subject<AtlasEntityWithEXTInformation>();

  constructor(
    private readonly entityDetailsService: EntityDetailsService,
    private readonly entityApiService: EntityAPIService
  ) {
    super();
    this.init();
  }

  private init() {
    this.update$
      .pipe(
        exhaustMap((entity) => this.handleUpdateEntity(entity)),
        untilDestroyed(this)
      )
      .subscribe(this.entityUpdated$);
  }

  updateEntity(entity: AtlasEntityWithEXTInformation) {
    this.update$.next(entity);
  }

  /** Whenever an entity is updated, emits its guid */
  get entityUpdated() {
    return this.entityUpdated$.asObservable();
  }

  @ManagedTask('Saving the entity', { isQuiet: true })
  @MonitorAsync('isUpdatingEntity')
  private async handleUpdateEntity(
    entityDetails: AtlasEntityWithEXTInformation
  ) {
    const [guid, _] = await this.handleSaveEntity(entityDetails);

    await this.handleUpdateClassifications(guid, entityDetails);

    this.entityDetailsService.entityDetails = await getEntityById(guid, {
      forceUpdate: true,
    }).toPromise();

    return guid;
  }

  private async handleUpdateClassifications(
    guid: string,
    entityDetails: AtlasEntityWithEXTInformation
  ) {
    const classifications = entityDetails.entity.classifications ?? [],
      currentClassifications = await this.entityDetailsService.get(
        ['entityDetails', 'entity', 'classifications'],
        { includeFalsy: true }
      )
    // filter out classifications that are not owned by the entity (being propagated from a relationship)
    // thouse types of classifications are not editable
    const ownedCurrentClassifications = guid === undefined
      ? (currentClassifications ?? [])
      : (currentClassifications ?? []).filter(
          (classification: Classification) => classification.entityGuid === guid
        );

    function difference(
      a: Classification[],
      b: Classification[]
    ): Classification[] {
      return a.filter((aa) => !b.find((bb) => aa.typeName === bb.typeName));
    }

    const classificationsToAdd = ownedCurrentClassifications
      ? difference(classifications, ownedCurrentClassifications)
      : classifications;

    const classificationsToRemove = ownedCurrentClassifications
      ? difference(ownedCurrentClassifications, classifications)
      : [];

    // When creating a new entity, any classifications direclty assigned to this entity will have a placeholder entityGuid.
    // Override the placeholder entityGuid with the given guid
    const classificationsWithoutPlaceholderGuid = classificationsToAdd.map(
      (classification) =>
        classification.entityGuid.startsWith('-')
          ? { ...classification, entityGuid: guid }
          : classification
    );

    const additions = classificationsToAdd.length
      ? saveEntityClassification(guid, classificationsWithoutPlaceholderGuid).toPromise()
      : Promise.resolve();

    const removals = classificationsToRemove.length
      ? Promise.all(
          classificationsToRemove.map((classification) =>
            removeEntityClassification(
              guid,
              classification.typeName
            ).toPromise()
          )
        )
      : Promise.resolve();

    return Promise.all([additions, removals as Promise<void>]);
  }

  private async handleSaveEntity(entityDetails: AtlasEntityWithEXTInformation) {
    const response = await this.entityApiService
      .saveEntity(entityDetails)
      .toPromise();

    const guid =
      response.guidAssignments?.[entityDetails.entity.guid] ??
      entityDetails.entity.guid;

    this.entityApiService.clearCacheById(guid);

    return [guid, response] as const;
  }
}
