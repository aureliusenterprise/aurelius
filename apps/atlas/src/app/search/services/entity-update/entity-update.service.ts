import { Injectable } from '@angular/core';
import {
    AtlasEntityWithEXTInformation,
    Classification,
    EntityAPIService,
    getEntityById,
    removeEntityClassification,
    saveEntityClassification,
    updateEntityClassification,
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
        private readonly entityApiService: EntityAPIService,
    ) {
        super();
        this.init();
    }

    private init() {
        this.update$
            .pipe(
                exhaustMap((entity) => this.handleUpdateEntity(entity)),
                untilDestroyed(this),
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

    @ManagedTask('search.services.entityUpdate.save', { isQuiet: true })
    @MonitorAsync('isUpdatingEntity')
    private async handleUpdateEntity(entityDetails: AtlasEntityWithEXTInformation) {
        const [guid, _] = await this.handleSaveEntity(entityDetails);

        const saved = await getEntityById(guid, { forceUpdate: true }).toPromise();
        const changed = await this.handleUpdateClassifications(guid, entityDetails, saved);

        this.entityDetailsService.entityDetails = changed
            ? await getEntityById(guid, { forceUpdate: true }).toPromise()
            : saved;

        return guid;
    }

    /**
     * Brings the classifications the entity carries itself in line with the editor. Compared with the entity as it
     * was saved: a new entity already got its classifications with the save, an existing one keeps its old ones
     * (Atlas ignores classifications when updating an entity). Propagated classifications are not editable.
     * Returns whether anything changed.
     */
    private async handleUpdateClassifications(
        guid: string,
        entityDetails: AtlasEntityWithEXTInformation,
        saved: AtlasEntityWithEXTInformation,
    ): Promise<boolean> {
        const editorGuid = entityDetails.entity.guid;
        const isOwn = (classification: Classification) =>
            !classification.entityGuid ||
            classification.entityGuid === guid ||
            classification.entityGuid === editorGuid ||
            classification.entityGuid.startsWith('-');

        const wanted = (entityDetails.entity.classifications ?? [])
            .filter(isOwn)
            .map((classification) => ({ ...classification, entityGuid: guid }));
        const current = (saved?.entity?.classifications ?? []).filter(
            (classification: Classification) => classification.entityGuid === guid,
        );

        const find = (list: Classification[], typeName: string) => list.find((c) => c.typeName === typeName);
        const propagates = (classification: Classification) => classification.propagate !== false;

        const toAdd = wanted.filter((classification) => !find(current, classification.typeName));
        const toRemove = current.filter((classification) => !find(wanted, classification.typeName));
        const toChange = wanted.filter((classification) => {
            const existing = find(current, classification.typeName);
            return existing && propagates(existing) !== propagates(classification);
        });

        await Promise.all([
            toAdd.length ? saveEntityClassification(guid, toAdd).toPromise() : Promise.resolve(),
            toChange.length
                ? updateEntityClassification(
                      guid,
                      toChange.map((classification) => ({
                          ...find(current, classification.typeName),
                          propagate: propagates(classification),
                      })),
                  ).toPromise()
                : Promise.resolve(),
            ...toRemove.map((classification) =>
                removeEntityClassification(guid, classification.typeName).toPromise(),
            ),
        ]);

        return toAdd.length + toChange.length + toRemove.length > 0;
    }

    private async handleSaveEntity(entityDetails: AtlasEntityWithEXTInformation) {
        const response = await this.entityApiService.saveEntity(entityDetails).toPromise();

        const guid = response.guidAssignments?.[entityDetails.entity.guid] ?? entityDetails.entity.guid;

        this.entityApiService.clearCacheById(guid);

        return [guid, response] as const;
    }
}
