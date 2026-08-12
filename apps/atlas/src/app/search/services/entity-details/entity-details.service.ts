import { Injectable, Optional, SkipSelf } from '@angular/core';
import { AtlasEntityWithEXTInformation, EntityAPIService, EntityElementWithEXTInfo } from '@models4insight/atlas/api';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { Observable } from 'rxjs';
import { switchMap } from 'rxjs/operators';

export interface EntityDetailsStoreContext {
    readonly entityId?: string;
    readonly entityDetails?: AtlasEntityWithEXTInformation;
    readonly isRetrievingDetails?: boolean;
}

@Injectable()
export class EntityDetailsService extends BasicStore<EntityDetailsStoreContext> {
    readonly entityDetails$: Observable<EntityElementWithEXTInfo>;

    constructor(
        private readonly entityApiService: EntityAPIService,
        @Optional() @SkipSelf() readonly parent: EntityDetailsService,
    ) {
        super();

        this.entityDetails$ = this.select(['entityDetails', 'entity']);

        this.select('entityId')
            .pipe(
                switchMap((guid) => this.handleGetEntityDetails(guid)),
                untilDestroyed(this),
            )
            .subscribe();
    }

    set entityId(entityId: string) {
        this.delete({
            description: 'Clear previous entity details',
            path: ['entityDetails'],
        });

        this.delete({
            description: 'Clear previous entity id',
            path: ['entityId'],
        });

        this.update({
            description: 'New entity id available',
            payload: { entityId },
        });
    }

    set entityDetails(entityDetails: AtlasEntityWithEXTInformation) {
        this.update({
            description: 'New entity details available',
            payload: {
                entityDetails,
            },
        });
    }

    clear() {
        this.delete({
            description: 'Clear entity details state',
        });
    }

    @ManagedTask('search.services.entityDetails.retrieve', { isQuiet: true })
    @MonitorAsync('isRetrievingDetails')
    private async handleGetEntityDetails(entityId: string) {
        const entityDetails = await this.entityApiService.getEntityById(entityId).toPromise();

        // Ignore stale fetches from a previous edit/details route if the GUID has already changed.
        if ((await this.get('entityId')) !== entityId) return;

        this.entityDetails = entityDetails;
    }
}
