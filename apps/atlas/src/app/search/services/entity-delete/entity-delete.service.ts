import { Injectable } from '@angular/core';
import { deleteEntitySoft } from '@models4insight/atlas/api';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { identity, Subject } from 'rxjs';
import { exhaustMap, filter } from 'rxjs/operators';
import { EntityDetailsService } from '../entity-details/entity-details.service';

export interface EntityDeleteStoreContext {
  readonly isDeletingEntity?: boolean;
}

@Injectable()
export class EntityDeleteService extends BasicStore<EntityDeleteStoreContext> {
  private readonly delete$ = new Subject<void>();
  private readonly entityDeleted$ = new Subject<boolean>();

  constructor(private readonly entityDetailsService: EntityDetailsService) {
    super();
    this.init();
  }

  private init() {
    this.delete$
      .pipe(
        exhaustMap(() => this.handleDeleteEntity()),
        untilDestroyed(this)
      )
      .subscribe(this.entityDeleted$);
  }

  deleteEntity() {
    this.delete$.next();
  }

  /**
   * Emits whenever the entity is successfully deleted
   */
  get entityDeleted() {
    return this.entityDeleted$.pipe(filter(identity));
  }

  @ManagedTask('Deleting the entity', { isQuiet: true })
  @MonitorAsync('isDeletingEntity')
  private async handleDeleteEntity() {
    const guid = await this.entityDetailsService.get([
      'entityDetails',
      'entity',
      'guid'
    ]);

    const response = await deleteEntitySoft(guid).toPromise();

    const deletedHeader = response.mutatedEntities['DELETE']?.find(
      header => header.guid === guid
    );

    return Boolean(deletedHeader);
  }
}
