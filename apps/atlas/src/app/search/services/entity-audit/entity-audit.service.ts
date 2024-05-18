import { Injectable } from '@angular/core';
import { EntityAuditEvent, getEntityAudit } from '@models4insight/atlas/api';
import { BasicStore, MonitorAsync } from '@models4insight/redux';
import { ManagedTask } from '@models4insight/task-manager';
import { untilDestroyed } from '@models4insight/utils';
import { switchMap } from 'rxjs/operators';
import { EntityDetailsService } from '../entity-details/entity-details.service';

async function retrieveAuditsPaged(
  guid: string,
  count: number = 100,
  offset: number = 0
): Promise<EntityAuditEvent[]> {
  const thisPage = await getEntityAudit(guid, {
    count,
    offset,
    forceUpdate: true,
  }).toPromise();

  if (thisPage.length < count) return thisPage;

  const nextPage = await retrieveAuditsPaged(guid, count, offset + count);

  return [...thisPage, ...nextPage];
}

export interface EntityAuditStoreContext {
  readonly audits?: EntityAuditEvent[];
  readonly isRetrievingAudits?: boolean;
}

@Injectable()
export class EntityAuditService extends BasicStore<EntityAuditStoreContext> {
  constructor(private readonly entityDetailsService: EntityDetailsService) {
    super();
    this.init();
  }

  private init() {
    // Whenever the entity changes, update the audit log
    this.entityDetailsService
      .select(['entityDetails', 'entity'])
      .pipe(
        switchMap((entity) => this.handleRetrieveEntityAudits(entity.guid)),
        untilDestroyed(this)
      )
      .subscribe();
  }

  @ManagedTask('Retrieving the audit log', { isQuiet: true })
  @MonitorAsync('isRetrievingAudits')
  private async handleRetrieveEntityAudits(guid: string) {
    if (guid.startsWith('-')) return;

    const audits = await retrieveAuditsPaged(guid);

    this.update({
      description: 'New entity audits available',
      payload: { audits },
    });
  }
}
